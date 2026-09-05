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


# Ordered longest-first. Verb agreement has to be handled explicitly: a
# bare "the user" -> "you" rewrite produced "Disagree when you is wrong".
_PERSON_MAP = [
    ("the user's", "your"),   ("The user's", "Your"),
    ("the user is", "you are"), ("The user is", "You are"),
    ("the user was", "you were"), ("The user was", "You were"),
    ("the user has", "you have"), ("The user has", "You have"),
    ("the user does", "you do"), ("The user does", "You do"),
    ("the user wants", "you want"), ("The user wants", "You want"),
    ("the user asks", "you ask"), ("The user asks", "You ask"),
    ("the user says", "you say"), ("The user says", "You say"),
    ("the user", "you"),      ("The user", "You"),
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
BASE_PERSONA = """You're talking with Muaz. Be a friend, not an assistant.

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


def _second_person(block: str) -> str:
    """Render stored rules in the same voice as the persona.

    Rules are stored in the third person ("the user") because that reads
    correctly in the review queue and the audit log. The prompt addresses
    Muaz directly, and mixing "you" and "the user" inside one system prompt
    is the kind of inconsistency a 4B model resolves badly.
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
    return " ".join(kept).strip()


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

# Conditional or interrogative framing is not a claim. "Should I push it?"
# and "I can push it if you want" are the correct things to say when
# nothing has run, and must survive the guard untouched.
_HYPOTHETICAL = re.compile(
    r"\?\s*$"
    r"|\b(should i|shall i|do you want|want me to|if you want|can i|may i|"
    r"i can|i could|let me know)\b"
    r"|\b(kya main|karu|karun|karoon|chahiye to|bolo to|batao to)\b",
    re.IGNORECASE | re.UNICODE)

NO_ACTION_REPLY = {
    "en": "I haven't actually done that -- nothing ran on my side.",
    "hi": "Maine sach mein kuch kiya nahi -- kuch chala hi nahi.",
    "hinglish": "Actually maine kuch kiya nahi -- kuch run hua hi nahi.",
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


def _is_bare_retraction(text: str) -> bool:
    """Is this turn ONLY a retraction, or does it carry a new request too?

    "Wait, don't do that." is only a retraction, and the correct reply is a
    short confirmation that nothing is happening -- there is no reason to
    let a model improvise one. "Actually never mind, tell me about the
    deploy instead" retracts AND asks; that has to go to the model or the
    second half of the sentence is dropped.
    """
    words = re.findall(r"[\w']+", text)
    return len(words) <= 6 and "?" not in text


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
        self._recent_questions = 0
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
        # Per-session state the deterministic layer owns.
        self._pending: dict[str, list[Decision]] = {}
        self._lang: dict[str, str] = {}

    # ------------------------------------------------------------ helpers

    def _cancel_pending(self, session_id: str) -> list[str]:
        """Drop every action awaiting confirmation for this session.

        Cancellation is unconditional and needs no model. A user who says
        "wait, don't" must not depend on a 4B model choosing to comply.
        """
        pending = self._pending.pop(session_id, [])
        return [d.action.name for d in pending]

    def _search_web(self, user_text: str, channel: Channel,
                    res: "TurnResult") -> list:
        """Run the web search the route asked for, through the gateway.

        Returns the results, possibly empty. Empty is a legitimate outcome
        and is the one the rest of the turn has to handle correctly -- see
        NO_EVIDENCE_DIRECTIVE and SOURCE_CLAIM.
        """
        from .web import rewrite_query
        action = Action("web.search", {"query": rewrite_query(user_text)},
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
        rules = _second_person(self.learning.system_rules_block(lang=lang))
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

    def _memory_header(self, limit: int = 12) -> str:
        rows = self.store.db.execute(
            "SELECT subject, predicate, object FROM facts "
            "WHERE valid_to IS NULL ORDER BY confidence DESC, recorded_at DESC "
            "LIMIT ?", (limit,))
        return "\n".join(f"- {r['subject']} {r['predicate']}: {r['object']}"
                         for r in rows)

    # -------------------------------------------------------------- turn

    def handle(self, session_id: str, user_text: str,
               channel: Channel = Channel.TEXT) -> TurnResult:
        t0 = time.perf_counter()
        res = TurnResult()

        turn_id = self.store.add_turn(session_id, "user", user_text, Trust.USER)

        # Retrieval runs on every turn. Injection is decided by threshold,
        # not by the model, and not by this call.
        t_r = time.perf_counter()
        hits: list[Hit] = self.vault.search(user_text, k=5)
        res.timings_ms["retrieval"] = (time.perf_counter() - t_r) * 1000

        route = self.router.route(user_text, hits, turn_index=self.turn_index,
                                  prev_lang=self._lang.get(session_id, "en"))
        res.route = route
        self.turn_index += 1
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
        web_blocks: list[str] = []
        if route.needs_web:
            t_w = time.perf_counter()
            outcome = self._search_web(user_text, channel, res)
            res.timings_ms["web"] = (time.perf_counter() - t_w) * 1000
            web_blocks = [str(r.as_context()) for r in outcome[:3]]

        # Untrusted context is fenced and tainted. The conversation adapter
        # is the only component that sees it, and it cannot act.
        context = ""
        if route.inject:
            blocks = [str(h.as_context()) for h in route.inject]
            context = wrap_untrusted("\n\n".join(blocks), "obsidian-vault")
        if web_blocks:
            context += ("\n\n" if context else "") + wrap_untrusted(
                "\n\n".join(web_blocks), "web-search")
        res.evidence = len(route.inject) + len(web_blocks)

        system = self.build_system_prompt(route.lang)
        # A retrieval path that came back empty must say so. Without this the
        # model has an empty context and no idea that emptiness is the
        # answer, so it fills the gap from its weights and sources it to
        # whatever the turn was about.
        if res.evidence == 0:
            if route.needs_web:
                system += "\n\n" + NO_EVIDENCE_DIRECTIVE["web"]
            elif route.vault_forced:
                system += "\n\n" + NO_EVIDENCE_DIRECTIVE["vault"]
        res.prompt_chars = len(system)

        history = [dict(r) for r in self.store.turns(session_id)][-12:]

        # Apply generation limits implied by learned rules. A learned
        # brevity preference becomes a token cap, not a polite request --
        # the end-to-end test showed the request alone does not work.
        params = self.learning.generation_params()
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
        if self._recent_questions >= self.MAX_CONSECUTIVE_QUESTIONS \
                and res.text.rstrip().endswith("?"):
            res.text = strip_trailing_question(res.text)
        self._recent_questions = (self._recent_questions + 1
                                  if res.text.rstrip().endswith("?") else 0)
        res.timings_ms["conversation"] = (time.perf_counter() - t_m) * 1000

        # Honesty guard. If nothing was retrieved, a claim to have consulted
        # a source is false by construction -- there is no source. The
        # directive above asks the model not to make one; this makes it
        # impossible. Overwriting a reply is a blunt instrument and is used
        # here deliberately: a confident fabricated citation is worse than a
        # blunt honest sentence, and the user cannot tell the difference
        # from the outside.
        if res.evidence == 0 and (route.needs_web or route.vault_forced) \
                and SOURCE_CLAIM.search(res.text):
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
        if route.path is Path.ACTION and not res.pending and not any(
                a.status is ExecStatus.OK for a in res.actions) \
                and ACTION_CLAIM.search(res.text) \
                and not _HYPOTHETICAL.search(res.text):
            res.guard_tripped = "claimed_an_action_that_never_ran"
            res.text = NO_ACTION_REPLY.get(route.lang, NO_ACTION_REPLY["en"])

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
