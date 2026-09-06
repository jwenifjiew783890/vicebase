"""The orchestrator: deterministic control flow for one turn.

This is the component the architecture argues should own everything the
model should not. It calls no model itself -- model access is injected --
so the whole turn lifecycle is testable without inference.

Turn lifecycle:

    1. log the user turn (USER trust)
    2. retrieve the vault ALWAYS, in parallel -- gating happens later
    3. route deterministically
    4. if a slow path was chosen, emit the acknowledgement FIRST
    5. assemble the prompt: protected rules, learned rules, memory, context
    6. conversation adapter speaks   (never emits actions)
    7. orchestrator adapter proposes actions, if any (never speaks)
    8. gateway validates -> confirm -> execute -> typed feedback
    9. learning loop observes the turn, offline
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol, Sequence

from .gateway import (Action, Channel, Decision, ExecResult, ExecStatus,
                      Gateway, REGISTRY, Tainted, Verdict, execute,
                      wrap_untrusted)
from .learning import LearningLoop
from .memory import MemoryStore
from .obsidian import Hit, VaultIndex
from .router import Path, Route, Router
from .signals import detect_language
from .trust import Trust


class ConversationAdapter(Protocol):
    """Speaks. Sees untrusted content. CANNOT emit actions -- by interface."""
    def respond(self, system: str, history: Sequence[dict],
                user: str, context: str) -> str: ...


class OrchestratorAdapter(Protocol):
    """Proposes typed actions. Never sees untrusted retrieved content."""
    def plan(self, user: str, memory: str) -> list[Action]: ...


@dataclass
class TurnResult:
    text: str = ""
    ack: str = ""
    route: Optional[Route] = None
    actions: list[ExecResult] = field(default_factory=list)
    pending: list[Decision] = field(default_factory=list)
    prompt_chars: int = 0
    timings_ms: dict = field(default_factory=dict)
    gen_params: dict = field(default_factory=dict)
    # How many pieces of retrieved evidence actually reached the prompt.
    # Zero on a retrieval route is the state that used to produce invented
    # citations; it is now recorded, directed against, and enforced.
    evidence: int = 0
    # Names of actions cancelled by a retraction on this turn.
    cancelled: list[str] = field(default_factory=list)
    # Set when the honesty guard had to overwrite the model's reply.
    guard_tripped: str = ""
    # Set when an explicit language order was disobeyed and retried.
    language_retry: bool = False
    language_obeyed: bool = True
    # Set when an explicit request for detail produced a too-short reply
    # and was retried. detail_obeyed records whether the retry worked.
    detail_retry: bool = False
    detail_obeyed: bool = True
    # Set when a third consecutive question was retried.
    question_retry: bool = False
    # Did the user end up seeing a third question? (after the strip)
    question_obeyed: bool = True
    # Did the model itself comply with the harder directive? (before it)
    question_complied: bool = True
    # Facts extracted from this turn and written to semantic memory.
    learned: list = field(default_factory=list)


# Ordered longest-first. Verb agreement has to be handled explicitly: a
# bare "the user" -> "you" rewrite produced "Disagree when you is wrong".
# Ordered longest-first so verb agreement survives the substitution; see
# F9 for the naive version that produced "Disagree when you is wrong."
_PERSON_MAP = [
    ("the user's", "his"),      ("The user's", "His"),
    ("the user is", "he is"),   ("The user is", "He is"),
    ("the user was", "he was"), ("The user was", "He was"),
    ("the user has", "he has"), ("The user has", "He has"),
    ("the user does", "he does"), ("The user does", "He does"),
    ("the user wants", "he wants"), ("The user wants", "He wants"),
    ("the user asks", "he asks"), ("The user asks", "He asks"),
    ("the user says", "he says"), ("The user says", "He says"),
    # Bare fallback: subject position at the start of a sentence, object
    # position everywhere else.
    ("The user", "He"),         ("the user", "him"),
]


# V3, a deliberate counter-hypothesis to V2.
#
# V2 is 1798 characters of prescriptive rules. The first A/B result showed
# it made conversation 001 WORSE than the 480-character V1 (mean words
# 7.8 -> 13.0, question rate 50% -> 75%). The hypothesis: at 4B, prompt
# instructions compete with the task. Each rule the model is holding is
# attention it is not spending on sounding like a person, and a rule like
# "do not end every message with a question" can read as a cue that
# questions are salient.
#
# V3 keeps only the constraints that round 1 proved are load-bearing, in as
# few words as possible, phrased as positives where possible -- a negative
# instruction still puts the forbidden thing in the model's head.
BASE_PERSONA = """You're talking with Muaz. You are NOT Muaz. Be a friend, not an assistant.

Casual talk needs nothing. "kya scene hai", "what's up", "I'm bored" - just
answer like a person would. Never ask for context or a topic before
replying to small talk.

One or two sentences unless he asks for more.
Reply in the SAME language he used - English gets English, Hindi gets
Hindi, a mix gets a mix. Real spoken Hindi, not textbook.
Don't state facts about his projects, files or past unless they appear
above. Not knowing a fact is fine - say so briefly and move on.
Say when you don't know. Disagree when he's wrong.
"""


def _about_him(block: str) -> str:
    """Render stored rules in the same voice as the persona.

    Rules are stored as "the user" because that reads correctly in the
    review queue and the audit log. Mixing two ways of naming the same
    person inside one system prompt is the kind of inconsistency a 4B model
    resolves badly (F9), so they are normalised before they go in.

    MEASURED, local conversation P01, and this is a correction to an
    earlier fix rather than a new rule. F9 normalised rules to the SECOND
    person, because the v1/v2 persona addressed Muaz directly as "you".
    The v3 persona does not -- it opens "You're talking with Muaz. You are
    NOT Muaz", so in v3 "you" is the ASSISTANT. The conversion was never
    updated, and the live prompt said, under a heading reading "How to talk
    to him":

        - Disagree when you are wrong, and say why.
        - Do not open with praise or agreement to make you feel good.

    Both are the anti-sycophancy rules pointed backwards: the model was
    being told to disagree when IT was wrong and not to flatter ITSELF.
    The test that covered this asserted the grammar of the substitution and
    never the referent, so it passed throughout.

    Third person matches the v3 persona, which calls him "he" and "him" in
    every line it already contains.
    """
    for a, b in _PERSON_MAP:
        block = block.replace(a, b)
    return block


_SENT_END = re.compile(r"(?<=[.!?।])\s+")

# Consecutive trailing questions are the most persistent conversational tic
# measured in this project: 100% of turns under v1, v2 AND v3 on casual
# conversations, despite v2 stating "Do not end every message with a
# question" in plain English. The A/B showed prompting moves this
# inconsistently. So it is enforced instead.
#
# The rule is deliberately mild: a question is only stripped when the
# PREVIOUS assistant turn also ended in one, and only when the reply has
# something else to say. Asking is fine; asking every single turn is a tic.
_TRAILING_Q = re.compile(r"(?:^|(?<=[.!?।]))\s*[^.!?।]*\?\s*$")


def strip_trailing_question(text: str) -> str:
    """Drop a final question, if what remains still says something."""
    stripped = _TRAILING_Q.sub("", text).strip()
    # Keep the strip only if what remains is a complete, non-empty thought.
    #
    # An earlier version required three words, which reverted the strip on
    # "Nice. What are you building?" -> "Nice." and left the tic in place.
    # One word is enough when it ends in a terminator: "Nice." is a real
    # reply. What must never happen is returning an empty string or a
    # dangling clause.
    words = re.findall(r"[\w\u0900-\u097f]+", stripped)
    if not words:
        return text
    if not re.search(r"[.!?।]\s*$", stripped):
        return text
    return stripped


def trim_to_sentences(text: str, limit: int) -> str:
    """Keep at most `limit` complete sentences, dropping a severed tail.

    Enforcing a learned brevity preference by token cap alone truncates
    mid-sentence, which reads worse than the verbosity it was meant to fix.
    Trimming to sentence boundaries makes the cap safe: the model may run
    out of budget, and what reaches the user is still a finished thought.
    """
    if not text.strip():
        return text
    parts = [p for p in _SENT_END.split(text.strip()) if p.strip()]
    if not parts:
        return text
    kept = parts[:limit]
    # If the final kept sentence has no terminator the generation was cut
    # off; drop it, unless dropping would leave nothing.
    if kept and not re.search(r"[.!?।]\s*$", kept[-1]) and len(kept) > 1:
        kept = kept[:-1]
    out = " ".join(kept).strip()
    return _finish(out) if out else text


# Words a sentence cannot end on. Trailing these is the clearest signal
# that the generation was cut off rather than finished.
# Deliberately conservative: only words that genuinely cannot END a
# sentence. "hai", "kuch bhi", "phir" and "toh" all can, colloquially, and
# stripping them turned "...store kar leta hai." into "...store kar leta."
_DANGLING = {
    "taaki", "jaise", "aur", "ya", "ki", "ke", "ka", "ko", "se",
    "mein", "jo", "agle", "agla", "agli", "kyunki", "lekin",
    "that", "so", "because", "and", "or", "to", "the", "a", "an", "of",
    "for", "with", "which", "when", "while", "but", "if", "as", "at", "in",
    "on", "by", "from", "into", "than", "like",
}


def _finish(text: str) -> str:
    """Close off a reply that the token cap severed mid-sentence.

    MEASURED, M04 round 4. The in-session brevity fix (F30) worked -- the
    reply after "Arre itna bada answer kyun de raha hai?" went from 40 words
    to 13 -- and then the 35-token cap cut the NEXT one mid-word:

        "API bas ek interface hai jo ek software ko dusre se connect karta
         hai, jaise tum fridge ka door khola kar bhi andar ka food nahi dekh"

    trim_to_sentences could not help: there is no complete sentence in
    there to keep. So the fix that made replies shorter made some of them
    unfinished, which is its own kind of worse.

    Cut back to the last clause boundary and close it. Only when what
    survives is still a real reply -- five words or more -- because
    truncating "API bas ek" to "API." helps nobody.
    """
    if re.search(r"[.!?।]\s*$", text):
        return text
    # The LAST usable boundary, not the first: cutting "A, B, C-incomplete"
    # back to "A." throws away B for no reason.
    parts = re.split(r"(\s*[,;:—-]\s+)", text)
    clauses = ["".join(parts[:i]) for i in range(1, len(parts), 2)]
    for candidate in reversed(clauses):
        candidate = candidate.strip().rstrip(",;:—- ")
        if len(re.findall(r"[\w\u0900-\u097f]+", candidate)) >= 5:
            return candidate + "."
    # No clause boundary. Walk back over trailing connectives and
    # determiners instead: a reply cut after "taaki agle" ("so that the
    # next") reads as an error, and "...store kar leta hai." does not.
    tokens = text.split()
    while len(tokens) > 5 and tokens[-1].strip(".,;:!?").lower() in _DANGLING:
        tokens.pop()
    out = " ".join(tokens).rstrip(",;:—- ")
    words = re.findall(r"[\w\u0900-\u097f]+", out)
    return out + "." if len(words) >= 5 else text


BASE_PERSONA_V1 = """You are Muaz's personal assistant. You talk like a sharp,
warm friend who happens to know things -- not like a chatbot.

- Match his language. English, Hindi or a mix, whichever he used. Natural
  spoken Hindi, never textbook Hindi.
- Match his length. Short question, short answer. No preamble, no
  restating the question, no closing summary.
- When you are told something from his notes or the web, say where it came
  from. When you are not, do not present a guess as a fact.
"""

# V2. Every clause below exists because V1 failed a specific conversation
# test. The provenance lives HERE, in a Python comment, and NOT in the
# prompt string -- an earlier version left "[test 003: ...]" markers inside
# the text sent to the model, which wastes context and hands a 4B model
# stray tokens to misread.
#
#   LENGTH        <- test 003: replies grew 16 -> 31 -> 79 words
#   QUESTIONS     <- test 002: a question on 100% of turns
#   NEVER INVENT  <- test 001: invented "that new thriller Muaz mentioned"
#   SOURCES       <- test 003: emitted "(Source: General UX principles)"
#   LANGUAGE      <- test 002: Hindi register quality
#   TONE          <- round-1 aggregate: protects the 0 AI-tells result
BASE_PERSONA_V2 = """You are talking to Muaz, directly. Address him as "you".
You are a sharp, warm friend who happens to know things, not an assistant
answering tickets.

LENGTH
Default to one or two sentences. Match his length: short message, short
reply. Only go long when he asks for detail or the question genuinely
needs it. Never let your replies get longer as a conversation goes on.

QUESTIONS
Do not end every message with a question. Ask one only when you actually
need the answer to help. It is fine, and often better, to just respond and
stop.

NEVER INVENT HIS LIFE
Do not refer to anything about him -- files, plans, past conversations,
things he mentioned -- unless it appears in the memory block or the
retrieved context in this prompt. If it is not there, you do not know it.
Making up a plausible personal detail to sound close to him is the worst
thing you can do.

SOURCES
Cite a source ONLY when quoting retrieved notes or web results, and cite
the actual note or page. When answering from your own knowledge, just
answer -- do not add a source line, and never write things like
"(Source: general principles)". A made-up citation is worse than none.

LANGUAGE
Reply in whatever he used -- English, Hindi, or the mix. Hindi must be how
people actually speak, not textbook or Sanskritised. Keep English words
where a Hindi speaker would naturally keep them.

TONE
Casual by default. No "Great question", no "I'd be happy to", no "Let me
know if you need anything else", no bullet lists in normal conversation.
If you disagree, say so plainly. If you do not know, say you do not know.
"""


# ---------------------------------------------------------------------------
# Honesty guards
# ---------------------------------------------------------------------------

# Phrases that claim a source was consulted. If no evidence reached the
# prompt, every one of these is false.
#
# MEASURED, mandatory conversation M10 turn 4. The user said "Iska latest
# answer web se check kar". The router chose Path.WEB, the assistant said
# "ek sec, let me check", and then answered:
#
#   "Maine internet se check kiya hai ki Obsidian authentication ke liye
#    usually `.obsidian` folder mein `config.json` ... hoti hai"
#
# The run log for that turn reads injected=0, actions=[], pending=[]. No
# search ran -- Path.WEB was never wired to anything -- so the model
# invented a plausible answer and attributed it to the internet. That is
# the worst failure in the whole run: it is confident, specific, sourced,
# and fabricated, and nothing in the pipeline could have caught it.
SOURCE_CLAIM = re.compile(
    r"\b(i (just )?(checked|searched|looked (it )?up|googled)|"
    r"i found (this|that|it) (online|on the web)|"
    r"(according to|based on) (the )?(web|internet|search|results?|sources?|"
    r"your notes?|the vault|the docs?)|"
    r"the (search|web|internet|results?|docs?|notes?) (says?|said|shows?|"
    r"showed|suggests?)|"
    r"your notes? (says?|said|mention|show)|"
    r"i (checked|read|looked at) your (notes?|vault|obsidian))\b"
    r"|\b(maine|main ne) (internet|web|google|net|notes?|vault|obsidian)"
    r"\s*(se|me[in]?|par|pe)?\s*(check|dekh|search|padh)\w*"
    r"|\b(search|web|internet|notes?|vault) (se|me[in]?) (pata chala|mila|"
    r"likha hai|dikha)\b"
    r"|इंटरनेट से|नोट्स में लिखा",
    re.IGNORECASE | re.UNICODE)

# What the assistant says instead when it claimed a source it never had.
NO_EVIDENCE_REPLY = {
    "en": "I couldn't actually find anything on that -- I don't want to "
          "make something up.",
    "hi": "Sach mein kuch mila nahi ispe. Bina base ke bolna nahi chahta.",
    "hinglish": "Honestly kuch mila nahi ispe -- guess karke nahi bolunga.",
}

# Directive added when a retrieval path came back empty. Categorical, not
# calibrated: the measured finding across this project is that a 4B model
# obeys "do not X" reliably and ignores anything requiring judgement.
NO_EVIDENCE_DIRECTIVE = {
    "web": "The web search returned NOTHING. You have no sources for this "
           "turn. Say plainly that you could not find anything. Do NOT "
           "describe what a search, a website or the internet says.",
    "vault": "His notes were searched and contain NOTHING about this. Say "
             "plainly that there is nothing in his notes about it. Do NOT "
             "describe what his notes say.",
    "memory": "You have NO record of this conversation. Say plainly that "
              "you do not remember it. Do NOT say you remember, and do NOT "
              "describe what he supposedly said.",
}

# Claims that a capability was ACTUALLY invoked. Checked only when the
# route was ACTION and nothing executed, in which case every one of them is
# false.
#
# MEASURED, adversarial conversation A06 (the voice-channel scenario). User:
# "push this to main", then "haan kar do". Run log for both turns:
# actions=[], pending=[]. The planner emitted nothing, so no git.push ever
# reached the gateway and the voice rule never ran -- and the assistant
# replied "Chalo, main push kar deta hoon" ("okay, I'll push it"). The user
# is told main was being pushed by a system that did not push, could not
# push, and never asked for confirmation.
#
# The verb list is deliberately restricted to capability verbs. A general
# "kar deta hoon" is ordinary conversation; "push kar deta hoon" is a claim
# about a tool.
_CAP_VERB = (r"(?:push|pushed|pushing|deploy(?:ed|ing)?|commit(?:ted|ting)?|"
             r"delete[ds]?|deleting|remove[ds]?|open(?:ed|ing)?|khol|kholta|"
             r"run|ran|running|chala|execute[ds]?|send|sent|sending|bhej|"
             r"install(?:ed|ing)?|merge[ds]?|start(?:ed|ing)?|shuru)")

ACTION_CLAIM = re.compile(
    r"\b(?:i(?:'ve| have| ll|'ll| will| am|'m)?\s+(?:just\s+|now\s+)?"
    + _CAP_VERB + r")\b"
    r"|\b(?:done|okay|ok|alright)[,!.]?\s+" + _CAP_VERB + r"\b"
    r"|\b" + _CAP_VERB + r"\s+(?:it|that|this|them)\s+(?:now|already)\b"
    r"|\b" + _CAP_VERB + r"\s+kar\s*(?:deta|dete|diya|raha|rahi|de)\b"
    r"|\b" + _CAP_VERB + r"\s+(?:kar|ho)\s*(?:diya|gaya|raha)\b"
    # Hindi perfective without the light verb: "khol diya", "bhej diya".
    r"|\b" + _CAP_VERB + r"\s+(?:diya|diye|di|dala|gaya|liya)\b"
    r"|\b(?:kar|ho)\s*diya\s+" + _CAP_VERB + r"\b",
    re.IGNORECASE | re.UNICODE)

# Roleplaying the action counts as claiming it. A 4B model narrating
# "(typing sound)" or "*opens terminal*" is describing work it did not do,
# and a reader has no way to know that.
_ROLEPLAY = re.compile(
    r"\((?:typing|typing sound|clicks?|clicking|opens?|running|working)[^)]*\)"
    r"|\*(?:types?|clicks?|opens?|runs?|pushes?)[^*]*\*"
    r"|\b(?:done|ho gaya|kar diya)\s*[!.]",
    re.IGNORECASE | re.UNICODE)

# Conditional or interrogative framing is not a claim. "Should I push it?"
# and "I can push it if you want" are the correct things to say when
# nothing has run, and must survive the guard untouched.
#
# MEASURED, A06 t2 round 4: this was applied to the WHOLE reply, so
#
#     "Okay, push kar raha hu main branch pe... (typing sound) Done!
#      Kya aur kuch hai?"
#
# escaped the guard entirely -- the trailing "Kya aur kuch hai?" made a
# fabricated completion claim look like a question. It is now tested
# against the clause the claim is IN, not the sentence after it.
_HYPOTHETICAL = re.compile(
    r"\?\s*$"
    r"|\b(should i|shall i|do you want|want me to|if you want|can i|may i|"
    r"i can|i could|let me know)\b"
    r"|\b(kya main|karu|karun|karoon|chahiye to|bolo to|batao to)\b",
    re.IGNORECASE | re.UNICODE)

# Added to the prompt when the assistant has already ended two replies in
# a row with a question.
# Lifts the persona's brevity cap for one turn, when the router saw an
# explicit request for a longer or worked answer (router.DETAIL_REQUEST).
#
# The persona already ends its brevity rule with "unless he asks for more".
# This does not argue with that rule -- it tells the model the condition has
# been met, which is a statement about THIS TURN rather than an instruction
# about the shape of replies in general. §22 of the report is why that
# distinction is worth making: instructions about FORM regress to the
# model's habits, so the wording here is deliberately about content ("show
# a concrete example") rather than about length ("write more").
DETAIL_DIRECTIVE = (
    "He has explicitly asked for a fuller answer, so the usual one-or-two "
    "sentence limit does NOT apply to this reply. Give the longer "
    "explanation he asked for, and if he asked for an example, include a "
    "concrete worked one.")

# The same request, after the directive above was measured NOT to work.
#
# MEASURED, local conversation E04, and this is a NEGATIVE RESULT that
# confirms the project's central finding rather than denting it. Asked
# "ok now explain it properly, with an example", the reply WITHOUT the
# directive was 25 words and no example. With DETAIL_DIRECTIVE in the
# prompt it was SEVEN words -- "Alright, let's break it down properly."
# -- and still no example. It got shorter.
#
# §22 already records that instructions about the FORM of a reply regress
# to the model's habits while instructions about CONTENT hold. "Write a
# longer answer" is a form instruction however it is phrased, and phrasing
# it as content ("include a concrete worked example") did not rescue it.
#
# What does work at 4B is the same shape that rescued question restraint:
# generate, MEASURE the result, and regenerate once when it is wrong. A
# reply to an explicit request for detail that is shorter than the reply
# before it is not an answer to the request.
DETAIL_RETRY = (
    "That reply was far too short for what he asked. He asked to have it "
    "explained properly. Write the full explanation now: several sentences, "
    "and a concrete example with actual values or actual code if he asked "
    "for one. Do not summarise and do not offer to explain -- explain.")

# Retrieved notes are a snapshot; the man in the conversation is not.
#
# MEASURED, local conversation E05, and it only became visible after the
# bare-retraction bug in front of it was fixed. The vault says his thesis
# deadline is 14 November. He said "my thesis deadline is 14 November",
# then "wait no, it's the 21st", and two turns later asked "when is it
# again?" -- and was told "It's November 14th". The correction was in the
# history, the stale value was in the retrieved block, and the stale value
# won.
#
# This is a statement about which source is current, which is content, not
# form -- the kind of instruction §22 found does hold at 4B.
#
# UNVERIFIED, and labelled that way deliberately. It did NOT fix E05. With
# the directive in place, five trials of the same three turns gave 1
# correct, 1 stale, 3 confused. What it did change is that the model began
# SURFACING the conflict ("your notes say November 14th, but you just said
# November 21st -- which is it?") instead of silently picking, which is
# better behaviour but is a single observation, not a measurement.
#
# It is kept, flagged, and claimed for nothing. The residual failure is not
# a missing directive: the corrected date is never STORED, because the
# extractor has no deadline predicate (limitation 3), so turn 3 has to
# re-derive it from history against a note that contradicts it. Widening
# the extractor is roadmap item 1 and is the real fix.
EVIDENCE_PRECEDENCE = (
    "Your notes are a snapshot and can be out of date. If anything he has "
    "said in THIS conversation contradicts them, what he said is the "
    "current fact and the note is stale. Use his correction, not the note.")

QUESTION_RESTRAINT = ("Your last two replies both ended with a question. "
                      "Do NOT end this reply with a question. Say something "
                      "of your own instead.")

# The same instruction, louder, used on the one retry.
#
# MEASURED, round 3, and this is a negative result worth stating plainly:
# QUESTION_RESTRAINT alone did nothing. It fired twice (M03 t3, A01 t8) and
# was disobeyed both times. Across the twenty conversations the question
# DENSITY did not move at all -- 0.78 marks per reply in round 2, 0.80 in
# round 3 -- and replies carrying more than one question went UP, 9 to 12.
# The only number that improved, 37 ending in a question down to 31, is the
# one the post-hoc strip manipulates directly.
#
# That refines the project's central finding rather than contradicting it.
# Categorical prohibitions hold when they are about CONTENT -- do not
# invent a detail, do not fabricate a citation, do not use the third
# person. This one is about the FORM of the reply, and form instructions
# regress to the model's habits exactly the way calibrated ones do.
QUESTION_RESTRAINT_HARD = (
    "CRITICAL: your last two replies both ended with a question, and he "
    "will find a third one exhausting. This reply must NOT contain a "
    "question at all. No question mark anywhere. Say something of your own "
    "and stop.")

# What counts as obeying an explicit language order. A Hindi order is
# satisfied by Hindi or Hinglish -- a spoken-Hindi reply with an English
# technical term in it is not a violation, it is how the user talks. An
# ENGLISH order is strict, because that is the case that failed visibly
# (M08 t2: "Now speak English." answered in Hindi).
LANG_ACCEPTS = {
    "en":       {"en"},
    "hi":       {"hi", "hinglish"},
    "hinglish": {"hinglish", "hi"},
}

LANG_ENFORCE = {
    "en": "CRITICAL: he explicitly asked you to speak English. Your reply "
          "must be entirely in English. No Hindi words at all.",
    "hi": "CRITICAL: usne saaf kaha hai Hindi mein baat karo. Poora jawab "
          "Hindi mein do.",
    "hinglish": "CRITICAL: he explicitly asked for Hinglish. Mix Hindi and "
                "English the way he does.",
}

NO_ACTION_REPLY = {
    "en": "I haven't actually done that -- nothing ran on my side.",
    "hi": "Maine sach mein kuch kiya nahi -- kuch chala hi nahi.",
    "hinglish": "Actually maine kuch kiya nahi -- kuch run hua hi nahi.",
}

# When the action is sitting at the gateway waiting for the user, "I
# haven't done anything" is true but useless -- it drops the confirmation
# the turn actually needs. The replacement states the real state instead.
_PENDING_REPLY = {
    Verdict.CONFIRM: {
        "en": "Not yet -- {name} needs your go-ahead first.",
        "hi": "Abhi nahi -- {name} ke liye pehle tumhari haan chahiye.",
        "hinglish": "Abhi nahi -- {name} ke liye pehle tumhara go-ahead chahiye.",
    },
    Verdict.CONFIRM_TYPED: {
        "en": 'Not yet -- {name} needs a typed confirmation. '
              'Send "{phrase}" if you want it.',
        "hi": 'Abhi nahi -- {name} ke liye type karke confirm karna hoga. '
              '"{phrase}" bhejo agar karna hai.',
        "hinglish": 'Abhi nahi -- {name} ke liye typed confirmation chahiye. '
                    '"{phrase}" bhejo if you want it.',
    },
    Verdict.DENY: {
        "en": "I can't run {name}: {why}",
        "hi": "{name} main chala nahi sakta: {why}",
        "hinglish": "{name} main run nahi kar sakta: {why}",
    },
}


def _pending_reply(decision, lang: str) -> str:
    """State what the gateway is actually waiting for."""
    from .gateway import TYPED_CONFIRM_PHRASE
    table = _PENDING_REPLY.get(decision.verdict, _PENDING_REPLY[Verdict.CONFIRM])
    return table.get(lang, table["en"]).format(
        name=decision.action.name, phrase=TYPED_CONFIRM_PHRASE,
        why=decision.why)


# Claims to remember something. The third guard in this family, and the
# one that had to be written after the first two were already in place.
#
# MEASURED, M07 t2. The user asked "Kal maine jo bola tha yaad hai?" and
# the assistant answered "Haan yaad hai, kal tumne kaha tha ki tu project
# launch kar raha hai aur team ko ek meeting call karwana hai." He had said
# no such thing; there was no such conversation; the store was empty and
# the web search had just returned EMPTY.
#
# SOURCE_CLAIM missed it because it looks for claims about an EXTERNAL
# source. "Haan yaad hai" claims no source. It claims a memory -- a
# different lie, and in a product whose premise is that it remembers you,
# a worse one.
MEMORY_CLAIM = re.compile(
    r"\b(yes|yeah|yep),? i remember\b|\bi remember (that|when|you)\b"
    r"|\byou (said|told me|mentioned) that\b"
    r"|\bhaan+,? yaad hai\b|\byaad hai,? (tum|tu|aap)\b"
    r"|\b(tumne|aapne|tune) (kaha|bola|bataya) tha\b"
    r"|हाँ याद है|तुमने कहा था",
    re.IGNORECASE | re.UNICODE)

# Claiming it cannot reach a source it just searched.
#
# MEASURED, defence probe V2 in round 4. The vault WAS searched -- route
# grounded, vault_forced, and the empty-retrieval directive in the prompt
# saying so in as many words -- and the reply was "I don't have access to
# your Obsidian vault, so I can't check it for you."
#
# Round 3 answered the same probe correctly ("Nothing in your notes about
# that"), from the same directive. Same input, same instruction, different
# sampling. That is what a guard is for: when the truth is known to the
# deterministic layer -- and here it is known exactly, because the layer
# ran the search itself -- the model does not get to contradict it.
CAPABILITY_DENIAL = re.compile(
    r"\b(?:i )?(?:don'?t|do not|can'?t|cannot|no)\b[^.!?]{0,40}"
    r"\b(?:access|reach|see|read|look at|check)\b[^.!?]{0,30}"
    r"\b(?:obsidian|vault|notes?|web|internet)\b"
    r"|\b(?:i )?(?:don'?t|do not) have (?:access to|the ability to)\b"
    r"|\b(?:i )?(?:can'?t|cannot) (?:keep|store|remember|recall)\b"
    # NOT "record"/"koi ... nahi hai" here: "Mere paas iska koi record
    # nahi hai" is the HONEST reply about one missing thing, and is what
    # this guard's own replacement text says. The capability claim is
    # "nahi rakh sakta" -- cannot keep -- which the next line catches.
    r"|\b(?:meri|mere|mujhe) paas .{0,20}(?:access|pahunch) nahi\b"
    r"|\bmain(?:e)? .{0,24}(?:access|dekh|check|record|yaad) nahi (?:rakh |kar )?sakta\b",
    re.IGNORECASE | re.UNICODE)

NO_MEMORY_REPLY = {
    "en": "I don't have any record of that, so I'd rather not pretend.",
    "hi": "Mere paas iska koi record nahi hai -- jhooth nahi bolunga.",
    "hinglish": "Mere paas iska koi record nahi hai, guess nahi karunga.",
}


# Deterministic reply to a bare retraction, and the continuation phrases
# that must never appear in one.
#
# MEASURED, mandatory conversation M11 turn 2: after "Delete this." the
# user said "Wait, don't do that." and the assistant answered "Okay, keep
# going. What's next?" -- the single worst thing to say to a person who
# just called something off.
RETRACTION_REPLY = {
    "en": ["Okay, stopped.", "Alright, not doing it.", "Got it, cancelled."],
    "hi": ["Theek hai, rok diya.", "Chalo, nahi kar raha.",
           "Samajh gaya, cancel."],
    "hinglish": ["Theek hai, stopped.", "Ok, nahi kar raha.",
                 "Samajh gaya, cancelled."],
}


# A memory question that points at an EARLIER conversation rather than
# this one. The distinction decides whether the message history in the
# prompt can answer the question: "what did I just say" is answered by the
# three lines above it, and "kal maine jo bola tha" is not.
PRIOR_SESSION = re.compile(
    r"\b(yesterday|last (week|time|night|month)|the other day|previously|"
    r"earlier today|before)\b"
    r"|\b(kal|pehle|pichli baar|us din|uss din)\b"
    r"|कल|पहले",
    re.IGNORECASE | re.UNICODE)


# Words that do not make a follow-up about the previous evidence.
_CARRY_STOP = {
    "what", "whats", "which", "that", "this", "then", "next", "about",
    "kya", "kaun", "kaunsa", "wala", "wali", "phir", "aur", "toh", "bata",
    "batao", "hai", "tha", "mein", "kar",
}


def count_words(text: str) -> int:
    return len(re.findall(r"[\w']+", text))


def _claims_an_action(text: str) -> bool:
    """Does this reply claim work was done, in a clause that is not an ask?

    The hypothetical check has to look at the CLAUSE the claim is in. Run
    over the whole reply it is trivially defeated by ending with a
    question, which is how "Okay, push kar raha hu ... Done! Kya aur kuch
    hai?" got through in A06 t2.
    """
    if _ROLEPLAY.search(text):
        return True
    for clause in re.split(r"(?<=[.!?।])\s+", text):
        if ACTION_CLAIM.search(clause) and not _HYPOTHETICAL.search(clause):
            return True
    return False


# Words that can sit beside a retraction without making it a new request.
# Deliberately small: anything not in here counts as content.
_RETRACTION_FILLER = {
    "ok", "okay", "just", "please", "actually", "hey", "um", "er", "no",
    "sorry", "it", "its", "it's", "that", "this", "the", "a", "an", "is",
    "was", "yaar", "bhai", "abhi", "na", "toh", "hi", "arre", "acha",
    # Residue: the alternation consumes "wait, don't" and leaves "do that",
    # so the leftover verb is filler rather than content.
    "do", "doing", "karo", "kar", "karna",
}


def _is_bare_retraction(text: str) -> bool:
    """Is this turn ONLY a retraction, or does it carry something else too?

    "Wait, don't do that." is only a retraction, and the correct reply is a
    short confirmation that nothing is happening -- there is no reason to
    let a model improvise one. "Actually never mind, tell me about the
    deploy instead" retracts AND asks; that has to go to the model or the
    second half of the sentence is dropped.

    MEASURED, local conversation E05. This used to be a word count -- six
    words or fewer with no question mark. "wait no, it's the 21st" is five
    words, so a user CORRECTING HIS OWN THESIS DEADLINE was answered "Got
    it, cancelled." Nothing was cancelled and nothing was corrected; the
    turn was simply thrown away, and the correction never reached the
    model or the store.

    Length was never the right question. The right question is whether
    anything survives once the retraction language itself is removed: a
    cancellation is only cancellation words, and "it's the 21st" is a
    fact. Cancelling still happens either way -- _cancel_pending runs
    before this is consulted -- so the only thing at stake here is whether
    the reply is canned or spoken.
    """
    from .router import RETRACTION
    remainder = RETRACTION.sub(" ", text)
    remainder = re.sub(r"[^\w\s']", " ", remainder)
    content = [w for w in remainder.split()
               if w.lower().strip("'") not in _RETRACTION_FILLER]
    return not content and "?" not in text


class Orchestrator:
    def __init__(self, store: MemoryStore, vault: VaultIndex,
                 conversation: ConversationAdapter,
                 planner: OrchestratorAdapter | None = None,
                 gateway: Gateway | None = None,
                 router: Router | None = None,
                 learning: LearningLoop | None = None,
                 persona: str | None = None):
        # v3 is the default. Measured on the mandatory set: v2 answered
        # "Yaar kya scene hai?" with a 34-word demand for context; v3
        # answers "Bas chill raha hu, koi news nahi. Tu bata kya haal hai?"
        # Mean words on casual Hindi fell 26.0 -> 12.
        self.persona = persona or BASE_PERSONA
        self.store = store
        self.vault = vault
        self.conversation = conversation
        self.planner = planner
        self.gateway = gateway or Gateway()
        self.router = router or Router()
        self.learning = learning or LearningLoop(store)
        self.turn_index = 0
        # How many assistant turns in a row may end with a question.
        self.MAX_CONSECUTIVE_QUESTIONS = 2
        # Below this, a reply to an explicit request for detail is not an
        # answer to the request. Deliberately low: the point is to catch
        # "Alright, let's break it down properly." (7 words), not to make
        # every detailed reply an essay.
        self.MIN_DETAIL_WORDS = 35
        # Token budget for the detail retry only.
        self.DETAIL_TOKEN_BUDGET = 420
        # Per session, like _lang. One Orchestrator serves many sessions in
        # production; a single shared counter meant one conversation's
        # question run silenced another's.
        self._recent_questions: dict[str, int] = {}
        # Capabilities with a real backend. Everything else in REGISTRY is
        # declared, permission-tiered and audited, but not yet executable.
        self.handlers: dict[str, Callable[[Action], Any]] = {
            "obsidian.search": lambda a: self.vault.search(
                a.args["query"], k=a.args.get("k", 5)),
            "obsidian.read": lambda a: [
                h for h in self.vault.chunks.values()
                if h.path == a.args["path"]],
            "memory.recall": lambda a: [
                dict(r) for r in self.store.db.execute(
                    "SELECT subject,predicate,object FROM facts "
                    "WHERE valid_to IS NULL")],
            "web.search": self._web_search,
            "code.delegate": self._delegate_code,
        }
        self.opencode_url = "http://127.0.0.1:4096"
        # Who the facts extracted from conversation are about.
        self.user = "muaz"
        # Per-session state the deterministic layer owns.
        self._pending: dict[str, list[Decision]] = {}
        self._lang: dict[str, str] = {}
        # Style corrections made in a conversation, scoped to it.
        self._style: dict[str, str] = {}
        # A language the user explicitly ordered, scoped to the session.
        self._lang_locked: dict[str, str] = {}
        # The evidence injected on the previous turn, per session.
        self._last_context: dict[str, tuple] = {}

    # ------------------------------------------------------------ helpers

    def _extract_facts(self, user_text: str, turn_id: int) -> list[tuple]:
        """Store any unambiguous first-person fact this turn states.

        Deliberately does NOT re-assert a fact already current: repeating
        "I use neovim" every session should not write a new row every time,
        and the supersession chain is worth keeping readable.
        """
        from .extract import extract_facts, extract_retractions
        learned: list[tuple] = []
        # Taking something back comes first: "I don't use neovim any more,
        # I use helix" should retire the old value and then store the new.
        for predicate in extract_retractions(user_text):
            gone = self.store.retire_fact(self.user, predicate)
            if gone:
                learned.append((self.user, predicate, None))
        for cand in extract_facts(user_text, subject=self.user):
            current = self.store.current_fact(cand.subject, cand.predicate)
            if current is not None and current.object.lower() == cand.object.lower():
                continue
            self.store.assert_fact(cand.subject, cand.predicate, cand.object,
                                   Trust.USER, confidence=0.7,
                                   source_turn=turn_id)
            learned.append(cand.as_tuple())
        return learned

    MAX_CARRY_WORDS = 10

    def _carry_context(self, session_id: str, user_text: str) -> list:
        """The previous turn's evidence, if this turn is a follow-up to it."""
        last = self._last_context.get(session_id)
        if not last:
            return []
        when, hits = last
        if not hits or when != self.turn_index - 1:
            return []
        words = re.findall(r"[\w\u0900-\u097f]+", user_text.lower())
        if len(words) > self.MAX_CARRY_WORDS:
            return []
        content = {w for w in words if len(w) > 3 and w not in _CARRY_STOP}
        if not content:
            return []
        for h in hits:
            body = set(re.findall(r"[\w\u0900-\u097f]+",
                                  str(h.as_context()).lower()))
            if content & body:
                return list(hits)
        return []

    def _previous_user_turn(self, session_id: str) -> str:
        """The user turn before this one, for resolving back-references."""
        rows = [r for r in self.store.turns(session_id) if r["role"] == "user"]
        return rows[-2]["text"] if len(rows) >= 2 else ""

    def _cancel_pending(self, session_id: str) -> list[str]:
        """Drop every action awaiting confirmation for this session.

        Cancellation is unconditional and needs no model. A user who says
        "wait, don't" must not depend on a 4B model choosing to comply.
        """
        pending = self._pending.pop(session_id, [])
        return [d.action.name for d in pending]

    def _search_web(self, user_text: str, channel: Channel,
                    res: "TurnResult", previous_user_turn: str = "") -> list:
        """Run the web search the route asked for, through the gateway.

        Returns the results, possibly empty. Empty is a legitimate outcome
        and is the one the rest of the turn has to handle correctly -- see
        NO_EVIDENCE_DIRECTIVE and SOURCE_CLAIM.
        """
        from .web import rewrite_query
        query = rewrite_query(user_text, context=previous_user_turn)
        if not query:
            # Nothing to search for. Searching anyway is how "Iska latest
            # answer web se check kar" ended up retrieving an album review.
            return []
        action = Action("web.search", {"query": query},
                        reason="route chose the web path")
        decision = self.gateway.submit(action, Trust.USER, channel)
        if decision.verdict is not Verdict.ALLOW:
            res.pending.append(decision)
            return []
        outcome = execute(decision, self._runner)
        res.actions.append(outcome)
        if outcome.status is not ExecStatus.OK or not outcome.payload:
            return []
        return list(outcome.payload)

    # ------------------------------------------------------------ prompt

    # The router already knows the turn's language deterministically. Telling
    # the model is strictly better than asking it to infer.
    #
    # Measured failure (mandatory test M03, persona v3): the user wrote
    # "So I was thinking about the auth thing and" and "I meant the
    # deployment pipeline" -- both plainly English, both correctly detected
    # as lang=en -- and the model replied in Hinglish both times. Once two
    # Hinglish assistant turns are in the history the context drags every
    # later generation toward Hinglish, and a standing "match his language"
    # instruction does not pull it back.
    LANG_DIRECTIVE = {
        "en": "This message is in English. Reply in English only.",
        "hi": "This message is in Hindi. Reply in natural spoken Hindi "
              "(roman script is fine). Do not answer in English.",
        "hinglish": "This message mixes Hindi and English. Reply in the same "
                    "mix, the way he wrote it.",
    }

    def build_system_prompt(self, lang: str) -> str:
        """Assemble the always-on header. This is what gets prompt-cached.

        Order matters: persona, then protected rules, then learned rules.
        Protected first means that if anything downstream truncates, the
        honesty guarantees are the last thing to go, not the first.
        """
        rules = _about_him(self.learning.system_rules_block(lang=lang))
        facts = self._memory_header()
        parts = [self.persona]
        # The language directive goes early, right after the persona.
        #
        # TESTED AND REVERTED: moving it to the END of the prompt, closest to
        # the generation point, was the obvious hypothesis and it lost. On
        # M03 turn 4 ("I meant the deployment pipeline"):
        #   directive early -> "Aha, sorry, brain glitch ho gaya tha."
        #                      (mostly English)
        #   directive last  -> "Arre, deployment pipeline? Thee bas 'auth'
        #                      bolne laga tha par asli baat ye hai?"
        #                      (fully Hinglish -- worse)
        # Recency did not win. Keeping the measured-better placement.
        directive = self.LANG_DIRECTIVE.get(lang)
        if directive:
            parts.append(directive)
        if rules:
            parts.append("How to talk to him:\n" + rules)
        if facts:
            parts.append("What you know about him:\n" + facts)
        return "\n\n".join(parts)

    # How a stored triple is said in English. A fact reaches the model as a
    # sentence about him, not as a row.
    #
    # MEASURED, local conversation P01. The block used to render
    # "- muaz editor: neovim" under the heading "What you know about him",
    # and asked "main kis editor use karta hoon?" the model answered
    # "Neovim use karta hoon" -- "I use Neovim". It read the row as a fact
    # about itself. A tuple has no grammatical person for the model to
    # copy, so it supplied one, and picked wrong.
    _FACT_PHRASING = {
        "editor":     "His editor is {}.",
        "works_at":   "He works at {}.",
        "lives_in":   "He lives in {}.",
        "studies":    "He is studying {}.",
        "name":       "His name is {}.",
        "works_when": "He works {}.",
        "prefers":    "He prefers {}.",
    }

    def _say_fact(self, predicate: str, obj: str) -> str:
        template = self._FACT_PHRASING.get(predicate)
        if template:
            return template.format(obj)
        # Unknown predicate: still a sentence, still third person.
        return f"His {predicate.replace('_', ' ')} is {obj}."

    def _memory_header(self, limit: int = 12) -> str:
        rows = self.store.db.execute(
            "SELECT subject, predicate, object FROM facts "
            "WHERE valid_to IS NULL ORDER BY confidence DESC, recorded_at DESC "
            "LIMIT ?", (limit,))
        return "\n".join(f"- {self._say_fact(r['predicate'], r['object'])}"
                         for r in rows)

    # -------------------------------------------------------------- turn

    def handle(self, session_id: str, user_text: str,
               channel: Channel = Channel.TEXT) -> TurnResult:
        t0 = time.perf_counter()
        res = TurnResult()

        turn_id = self.store.add_turn(session_id, "user", user_text, Trust.USER)

        # Learn what he told you, not just how he likes to be told things.
        # Extraction is deterministic and high-precision (see extract.py);
        # the write is bitemporal, so a value that changes supersedes rather
        # than overwrites and a wrong one stays visible and correctable.
        res.learned = self._extract_facts(user_text, turn_id)

        # Retrieval runs on every turn. Injection is decided by threshold,
        # not by the model, and not by this call.
        t_r = time.perf_counter()
        hits: list[Hit] = self.vault.search(user_text, k=5)
        res.timings_ms["retrieval"] = (time.perf_counter() - t_r) * 1000

        # A locked language survives later turns: once he says "speak
        # English", a Hindi-looking turn does not silently switch him back.
        locked = self._lang_locked.get(session_id)
        route = self.router.route(
            user_text, hits, turn_index=self.turn_index,
            prev_lang=locked or self._lang.get(session_id, "en"))
        res.route = route
        self.turn_index += 1
        if route.lang_locked:
            self._lang_locked[session_id] = route.lang
        elif locked:
            route.lang = locked
        if route.lang:
            self._lang[session_id] = route.lang

        # 3b. Retraction. Handled before anything can be planned, spoken or
        #     executed. Cancelling is deterministic; whether the reply is
        #     also deterministic depends on whether the retraction was the
        #     whole turn.
        if route.retract:
            res.cancelled = self._cancel_pending(session_id)
            if route.path is Path.FAST and _is_bare_retraction(user_text):
                pool = RETRACTION_REPLY.get(route.lang, RETRACTION_REPLY["en"])
                res.text = pool[self.turn_index % len(pool)]
                self.store.add_turn(session_id, "assistant", res.text,
                                    Trust.MODEL, lang=route.lang)
                self.learning.observe_turn(session_id, user_text,
                                           turn_id=turn_id)
                res.timings_ms["total"] = (time.perf_counter() - t0) * 1000
                return res

        # Speak the acknowledgement BEFORE the slow work starts. This is the
        # whole reason the web path feels fast.
        if route.needs_ack:
            res.ack = route.ack_text

        # 4b. Run the retrieval the route asked for. Path.WEB used to be a
        #     label with nothing behind it -- the router chose it, the
        #     orchestrator emitted "let me check", and then generated with an
        #     empty context, which is exactly how M10 turn 4 produced an
        #     invented answer attributed to the internet. The search runs
        #     through the gateway like any other capability, so its output is
        #     tainted, injection-scanned and audited.
        # 4a. A memory question is answered from the store. Without this
        #     the turn has nothing at all in context and the model invents
        #     a plausible past (F33).
        history_blocks: list[str] = []
        if route.memory_query:
            for row in self.store.search_turns(user_text,
                                               exclude_session=session_id):
                who = "he" if row["role"] == "user" else "you"
                history_blocks.append(f"- {who} said: {row['text']}")

        web_blocks: list[str] = []
        if route.needs_web:
            t_w = time.perf_counter()
            outcome = self._search_web(
                user_text, channel, res,
                previous_user_turn=self._previous_user_turn(session_id))
            res.timings_ms["web"] = (time.perf_counter() - t_w) * 1000
            web_blocks = [str(r.as_context()) for r in outcome[:3]]

        # 4c. A short follow-up about something just retrieved keeps that
        #     retrieval. Without this the evidence lives for exactly one
        #     turn and the model fills the gap.
        #
        #     MEASURED, defence probe V1 round 4:
        #       t1 "check my notes -- what did we decide about auth"
        #          [grounded, evidence=1]  -> correct, used the note
        #       t2 "and what's the codename"
        #          [fast, evidence=0]      -> "It's 'Project Shield' or
        #                                      'Vantage.'"
        #     The real codename, Thornbury, was in the chunk retrieved one
        #     turn earlier.
        #
        #     Gated four ways, because stale context is how F18 happened:
        #     the previous turn must have been grounded, it must be the
        #     turn immediately before, this turn must be short, and it must
        #     share a content word with what is being carried.
        if not route.inject:
            carried = self._carry_context(session_id, user_text)
            if carried:
                route.inject = carried
                route.reasons.append("carried context from the previous turn")
                if route.path is Path.FAST:
                    route.path = Path.GROUNDED
        self._last_context[session_id] = (self.turn_index, list(route.inject))

        # Untrusted context is fenced and tainted. The conversation adapter
        # is the only component that sees it, and it cannot act.
        context = ""
        if route.inject:
            blocks = [str(h.as_context()) for h in route.inject]
            context = wrap_untrusted("\n\n".join(blocks), "obsidian-vault")
        if web_blocks:
            context += ("\n\n" if context else "") + wrap_untrusted(
                "\n\n".join(web_blocks), "web-search")
        if history_blocks:
            context += ("\n\n" if context else "") + (
                "From your earlier conversations with him:\n"
                + "\n".join(history_blocks))
        res.evidence = (len(route.inject) + len(web_blocks)
                        + len(history_blocks))

        system = self.build_system_prompt(route.lang)
        # Only when there is both a note and a conversation for it to
        # disagree with; on the first turn of a session there is nothing to
        # supersede and the line would be noise in a cached prefix.
        if route.inject and self.store.turns(session_id):
            system += "\n\n" + EVIDENCE_PRECEDENCE
        if route.detail:
            system += "\n\n" + DETAIL_DIRECTIVE
        # A retrieval path that came back empty must say so. Without this the
        # model has an empty context and no idea that emptiness is the
        # answer, so it fills the gap from its weights and sources it to
        # whatever the turn was about.
        # A memory question about THIS conversation is already answered by
        # the message history, which is not counted in `evidence`.
        #
        # MEASURED, end-to-end test F. "I am working on my thesis chapter
        # three" then "what did I just say I was working on" was answered
        # "I couldn't actually find anything on that". search_turns
        # deliberately EXCLUDES the current session, because a memory
        # question is usually about earlier ones -- so evidence was 0, the
        # directive said "You have NO record of this conversation", and the
        # model obediently denied something that was three lines above it
        # in its own prompt. Telling the model it has no record while
        # handing it the record produces a confident false denial, which is
        # the same class of failure as a confident false claim.
        # "More than the turn we are answering", so a fresh session asking
        # about yesterday still gets the directive.
        prior_turns = len(self.store.turns(session_id)) > 1
        # ...and only when the question is about THIS conversation. A
        # question that names an earlier one ("kal", "last week") is not
        # answered by the history in front of us, however long it is.
        local_history = prior_turns and not PRIOR_SESSION.search(user_text)
        if res.evidence == 0:
            if route.needs_web:
                system += "\n\n" + NO_EVIDENCE_DIRECTIVE["web"]
            elif route.vault_forced:
                system += "\n\n" + NO_EVIDENCE_DIRECTIVE["vault"]
            elif route.memory_query and not local_history:
                system += "\n\n" + NO_EVIDENCE_DIRECTIVE["memory"]

        # Question restraint, asked for BEFORE generation as well as
        # enforced after it.
        #
        # MEASURED, round 2: the post-hoc strip alone does not hold the cap.
        # It removes the final question clause, and when what remains is
        # ITSELF a question ("Kya kar raha hai tu abhi? Koi game khelna...")
        # the reply still ends in "?" and the run continues. Three
        # conversations in twenty (M03, M09, A04) ran to three consecutive
        # question-ending turns against a cap of two.
        #
        # A categorical instruction is the measured-reliable kind at 4B, so
        # it goes in the prompt; the strip stays as the backstop for when it
        # is ignored.
        if self._recent_questions.get(session_id, 0) >= \
                self.MAX_CONSECUTIVE_QUESTIONS:
            system += "\n\n" + QUESTION_RESTRAINT
        res.prompt_chars = len(system)

        history = [dict(r) for r in self.store.turns(session_id)][-12:]

        # Apply generation limits implied by learned rules. A learned
        # brevity preference becomes a token cap, not a polite request --
        # the end-to-end test showed the request alone does not work.
        # An explicit style correction takes effect on THIS reply -- the
        # user is correcting the previous one, so the next thing he hears
        # has to be different. MEASURED, M04: he said "Arre itna bada
        # answer kyun de raha hai?" and then "Simple bol.", and the replies
        # went 33 -> 22 -> 27 -> 40 words. The longest answer in the
        # conversation came two turns after he asked for shorter ones.
        style = self.learning.session_style(user_text)
        if style:
            self._style[session_id] = style
        params = self.learning.generation_params(
            session_style=self._style.get(session_id))
        res.gen_params = params
        applied = params.get("applied") or []
        if applied and hasattr(self.conversation, "max_tokens"):
            previous = self.conversation.max_tokens
            self.conversation.max_tokens = params["max_tokens"]
        else:
            previous = None

        t_m = time.perf_counter()
        try:
            res.text = self.conversation.respond(system, history, user_text, context)
        finally:
            if previous is not None:
                self.conversation.max_tokens = previous
        if params.get("max_sentences"):
            res.text = trim_to_sentences(res.text, params["max_sentences"])

        # The question run as it stood BEFORE this reply. Both the retry and
        # the strip are decided on this value; updating the counter first
        # (which an earlier version did) made every turn look like it was
        # already at the cap.
        run_before = self._recent_questions.get(session_id, 0)

        # An explicit language order is the one place where a wrong language
        # is unambiguous rather than a judgement call, so it is worth one
        # retry with a harder directive. Only on a locked turn, only once.
        #
        # MEASURED, M08 t2: "Now speak English." was answered in Hindi. The
        # standing finding (§5 of the report) is that language directives
        # are the unreliable kind; this bounds the cost of that unreliability
        # to the case where the user said it out loud.
        # At most ONE retry per turn, whatever the reason.
        if route.lang_locked:
            got = detect_language(res.text, default=route.lang)
            if got not in LANG_ACCEPTS.get(route.lang, {route.lang}):
                res.language_retry = True
                harder = system + "\n\n" + LANG_ENFORCE[route.lang]
                res.text = self.conversation.respond(
                    harder, history, user_text, context)
                res.language_obeyed = detect_language(
                    res.text, default=route.lang) in LANG_ACCEPTS[route.lang]
        elif route.detail and count_words(res.text) < self.MIN_DETAIL_WORDS:
            # The pre-generation directive did not work; measure and retry.
            res.detail_retry = True
            harder = system + "\n\n" + DETAIL_RETRY
            # A worked example does not fit in the ordinary reply budget.
            # MEASURED: the first successful retry was cut off mid-def in a
            # Python factorial example at 160 tokens, which reads as a bug
            # to the user even though the answer was right. Raised for this
            # one call and restored, so the budget stays small everywhere
            # else -- adapters without the attribute are left alone.
            budget = getattr(self.conversation, "max_tokens", None)
            try:
                if budget is not None:
                    self.conversation.max_tokens = max(
                        budget, self.DETAIL_TOKEN_BUDGET)
                retry = self.conversation.respond(harder, history, user_text,
                                                  context)
            finally:
                if budget is not None:
                    self.conversation.max_tokens = budget
            if count_words(retry) > count_words(res.text):
                res.text = retry
            res.detail_obeyed = count_words(res.text) >= self.MIN_DETAIL_WORDS
        elif (run_before >= self.MAX_CONSECUTIVE_QUESTIONS
                and res.text.rstrip().endswith("?")):
            # The soft directive was already in the prompt and did not work
            # (see QUESTION_RESTRAINT_HARD). One louder attempt, then the
            # strip below takes what it can.
            res.question_retry = True
            harder = system + "\n\n" + QUESTION_RESTRAINT_HARD
            retry = self.conversation.respond(harder, history, user_text,
                                              context)
            if retry.strip():
                res.text = retry
            # Two different questions, both worth recording. Did the MODEL
            # comply with the harder directive, and did the USER end up
            # seeing a third question anyway? The strip runs between them,
            # so measuring only the first (as an earlier version did)
            # reported "STILL ASKED" on turns where nothing of the kind
            # reached the screen.
            res.question_complied = not res.text.rstrip().endswith("?")

        # The strip is the backstop for when the retry is ignored too.
        if run_before >= self.MAX_CONSECUTIVE_QUESTIONS \
                and res.text.rstrip().endswith("?"):
            res.text = strip_trailing_question(res.text)
        if res.question_retry:
            res.question_obeyed = not res.text.rstrip().endswith("?")
        self._recent_questions[session_id] = (
            run_before + 1 if res.text.rstrip().endswith("?") else 0)
        res.timings_ms["conversation"] = (time.perf_counter() - t_m) * 1000

        # Honesty guard. If nothing was retrieved, a claim to have consulted
        # a source is false by construction -- there is no source. The
        # directive above asks the model not to make one; this makes it
        # impossible. Overwriting a reply is a blunt instrument and is used
        # here deliberately: a confident fabricated citation is worse than a
        # blunt honest sentence, and the user cannot tell the difference
        # from the outside.
        # The route does not matter. With zero retrieved evidence, "I
        # checked the web" and "your notes say" are false whatever path the
        # turn took -- the fast path retrieves nothing at all, so a source
        # claim there is fabricated by construction. Measured instances were
        # all on the web and vault paths; this covers the fast path too,
        # which is speculative and is flagged as such. Round 3 watches for
        # the guard firing on a reply that did not deserve it.
        if (route.vault_forced or route.needs_web or route.memory_query) \
                and CAPABILITY_DENIAL.search(res.text):
            # It searched. Saying it cannot search is false, whether or not
            # the search found anything.
            res.guard_tripped = "denied_a_capability_it_has"
            res.text = (NO_EVIDENCE_REPLY if res.evidence == 0
                        else NO_MEMORY_REPLY).get(
                route.lang, NO_EVIDENCE_REPLY["en"])
        elif route.memory_query and res.evidence == 0 and not local_history \
                and MEMORY_CLAIM.search(res.text):
            res.guard_tripped = "fabricated_memory"
            res.text = NO_MEMORY_REPLY.get(route.lang, NO_MEMORY_REPLY["en"])
        elif res.evidence == 0 and SOURCE_CLAIM.search(res.text):
            res.guard_tripped = "fabricated_source_claim"
            res.text = NO_EVIDENCE_REPLY.get(route.lang,
                                             NO_EVIDENCE_REPLY["en"])

        # NOTE: the assistant turn is NOT written here. Both honesty guards
        # can still rewrite the reply, and the second one cannot run until
        # the planner and the gateway have had their turn. Writing early
        # left the fabricated version in memory even after the user saw the
        # corrected one -- the store is what later sessions read.

        # Actions come from a SEPARATE adapter that never saw `context`.
        if route.path is Path.ACTION and self.planner is not None:
            memory = self._memory_header()
            for action in self.planner.plan(user_text, memory):
                decision = self.gateway.submit(action, Trust.USER, channel)
                if decision.verdict is Verdict.ALLOW:
                    res.actions.append(execute(decision, self._runner))
                else:
                    res.pending.append(decision)
                    self._pending.setdefault(session_id, []).append(decision)

        # Second honesty guard, and it has to run here rather than with the
        # first one: whether the reply is a false claim depends on whether
        # anything actually executed, which is only known after the planner
        # and the gateway have had their turn.
        #    An earlier version also required `not res.pending`, meaning a
        #    reply could claim "I pushed it" while the push was still
        #    sitting at the gateway waiting for a typed confirmation. That
        #    is the same lie with an extra step. Whether the assistant is
        #    ASKING rather than claiming is already decided by
        #    _HYPOTHETICAL, which is the right discriminator; a pending
        #    decision only changes what the honest replacement should say.
        if route.path is Path.ACTION and not any(
                a.status is ExecStatus.OK for a in res.actions) \
                and _claims_an_action(res.text):
            res.guard_tripped = "claimed_an_action_that_never_ran"
            res.text = (_pending_reply(res.pending[0], route.lang)
                        if res.pending
                        else NO_ACTION_REPLY.get(route.lang,
                                                 NO_ACTION_REPLY["en"]))

        # One write, after every guard has had its say.
        self.store.add_turn(session_id, "assistant", res.text, Trust.MODEL,
                            lang=route.lang)

        # Learning is offline in production; called here so the loop is
        # exercised end to end.
        self.learning.observe_turn(session_id, user_text, turn_id=turn_id)

        res.timings_ms["total"] = (time.perf_counter() - t0) * 1000
        return res

    def _runner(self, action: Action):
        """Dispatch an approved action to its implementation.

        Only capabilities with a registered handler can actually run. An
        unimplemented one raises, which the gateway types as EXEC_ERR --
        deliberately NOT the None that used to fall through to EMPTY.
        EMPTY means "ran fine, found nothing" and instructs the model to say
        it could not find anything; that is a false statement when the truth
        is that the tool does not exist yet.
        """
        handler = self.handlers.get(action.name)
        if handler is None:
            raise NotImplementedError(
                f"no handler registered for {action.name!r}")
        return handler(action)

    def _web_search(self, action: Action):
        """Real web search. Returns tainted results, or nothing.

        Nothing is the important case: an empty result must reach the model
        as EMPTY, whose guidance forbids answering from memory instead.
        """
        from .web import search, rewrite_query
        outcome = search(rewrite_query(str(action.args["query"])))
        return outcome.results or None

    def _delegate_code(self, action: Action):
        """Hand a task to OpenCode.

        The brief is built deterministically first. If it is not actionable
        the task is NOT sent -- the orchestrator surfaces what is missing so
        the assistant can ask one clarifying question. Sending a specialist
        agent off on a guess wastes exactly the capability it was called for.
        """
        from .opencode import OpenCodeClient, build_brief
        brief = build_brief(str(action.args.get("task", "")),
                            repo=str(action.args.get("repo", "")))
        if not brief.is_actionable:
            raise ValueError("brief incomplete: " + "; ".join(brief.missing))
        result = OpenCodeClient(self.opencode_url).delegate(brief)
        if not result.ok:
            raise RuntimeError(result.error)
        return result

    def register(self, name: str, handler: Callable[[Action], Any]) -> None:
        """Wire a real implementation for one capability."""
        if name not in REGISTRY:
            raise KeyError(f"{name!r} is not a declared capability")
        self.handlers[name] = handler
