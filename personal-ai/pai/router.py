"""Turn routing: deciding what happens before the model speaks.

The design goal is that the common case costs nothing. Most conversational
turns need no retrieval, no tool, and no escalation, and any architecture
that taxes those turns to serve the rare ones will feel slow no matter how
fast the model is.

Three decisions, in order of cost:

  RETRIEVE OBSIDIAN -- always, in parallel, ~30ms. A score THRESHOLD, not
  the model, decides whether the result is injected. This removes an
  unreliable judgement from a 4B model entirely and is the single largest
  simplification available.

  SEARCH THE WEB -- gated. Deterministic pre-checks set a prior; the model
  may request it; an uncertainty signal can force it. Costs 1-3s, so it
  MUST be masked by an immediate spoken acknowledgement.

  ESCALATE -- to a bigger model or a specialist agent. Costs seconds.
  Also masked.

Nothing here calls a model. That is the point: routing is deterministic so
it is fast, testable, and cannot be talked out of its decisions.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Sequence

from .obsidian import Hit
from .signals import detect_language


class Path(str, Enum):
    FAST      = "fast"        # conversation only, nothing else runs
    GROUNDED  = "grounded"    # vault context injected
    WEB       = "web"         # web search, acknowledgement first
    ACTION    = "action"      # a tool/agent is involved
    ESCALATE  = "escalate"    # bigger model


# --------------------------------------------------------------------------
# Deterministic pre-checks
# --------------------------------------------------------------------------

# Signals that the answer depends on something current or verifiable, which
# the model must not answer from memory.
VOLATILE = re.compile(
    r"\b(latest|current|today|todays|tonight|tomorrow|yesterday|right now|"
    r"this (week|month|year)|recent|news|price|weather|version|release|"
    r"who won|score|stock|rate)\b"
    r"|\b20\d\d\b"
    r"|\b(aaj|abhi|kal|parso|taza|abhi ka|latest wala)\b"
    r"|आज|अभी|कल|ताज़ा|नवीनतम",
    re.IGNORECASE | re.UNICODE)

# Signals that the answer is personal/project specific -> vault.
PERSONAL = re.compile(
    r"\b(my|our|mine|i wrote|i noted|we decided|the project|our plan|"
    r"my notes?|the doc|the spec|the design|assignment)\b"
    r"|\b(mera|meri|mere|hamara|hamari|apna|apni|maine likha|humne decide)\b"
    r"|मेरा|मेरी|हमारा|अपना",
    re.IGNORECASE | re.UNICODE)

# A temporal word alone does not mean the user wants information.
# Found in conversation test 002: "aaj bahut thak gaya hoon" ("I'm very
# tired today") matched VOLATILE on "aaj" and triggered a WEB SEARCH with
# "ek sec, let me check". The user shared how they felt and the assistant
# went to Google. Volatility now requires the turn to actually be seeking
# information -- a question, an interrogative, or an explicit request.
# Requiring an explicit interrogative was too strict: "current price of
# bitcoin" and "latest release notes for llama.cpp" are noun-phrase queries
# with no question mark and no wh-word, and they are exactly what people
# say. So the logic is inverted -- a volatile marker counts UNLESS the turn
# is clearly the user talking about themselves.
REQUEST_VERB = re.compile(
    r"\?"
    r"|^\s*(what|who|when|where|which|how|why|is|are|was|were|do|does|did|"
    r"can|could|will|would|should)\b"
    r"|\b(tell me|show me|find|look up|search|give me|i want|i need|"
    r"any news|check)\b"
    r"|\b(kya|kaun|kab|kahan|kaise|kyun|kyu|batao|bata|dhundo|chahiye|"
    r"pata karo|dekho|check karo)\b"
    r"|क्या|कौन|कब|कहाँ|कैसे|क्यों|बताओ|ढूंढो|चाहिए",
    re.IGNORECASE | re.UNICODE)

FIRST_PERSON = re.compile(
    r"\b(i|i'?m|i'?ve|me|my|mine|we|our)\b"
    r"|\b(main|mai|maine|mujhe|mera|meri|mere|hum|humne|hamara)\b"
    r"|मैं|मुझे|मेरा|मेरी|हम",
    re.IGNORECASE | re.UNICODE)

# Statements about the speaker's own state are never search triggers, even
# when they contain a temporal word.
SELF_STATE = re.compile(
    r"\b(i'?m|i am|i feel|feeling|i'?ve been|im)\s+\w*\s*"
    r"(tired|exhausted|bored|sad|happy|angry|stressed|fine|ok|good|bad|done)"
    r"|\b(thak gaya|thak gayi|thak|bore ho|bored ho|pareshan|khush|udaas|"
    r"mood nahi|mann nahi|neend|so raha|so rahi)\b"
    r"|थक गया|थक गयी|बोर हो|परेशान|खुश|उदास",
    re.IGNORECASE | re.UNICODE)


def _is_information_request(text: str) -> bool:
    """Does a volatile marker in this turn mean the user wants a lookup?

    No when the user is describing their own state or narrating something
    about themselves without asking for anything.
    """
    if SELF_STATE.search(text):
        return False
    if FIRST_PERSON.search(text) and not REQUEST_VERB.search(text):
        return False
    return True


# Words that cannot be the SUBJECT of a web search. Temporal markers,
# demonstratives, pronouns and generic placeholder nouns all refer to
# something the two of you already share; none of them names a thing the
# internet could be asked about.
_NOT_A_SUBJECT = {
    # temporal
    "latest", "current", "today", "todays", "tonight", "tomorrow",
    "yesterday", "now", "recent", "aaj", "abhi", "kal", "parso", "taza",
    # demonstratives / back-references
    "that", "this", "those", "these", "it", "one", "thing", "stuff",
    "wo", "woh", "ye", "yeh", "us", "is", "wala", "wali", "vala", "vali",
    "iska", "uska", "isko", "usko", "same",
    # generic placeholder nouns
    "kaam", "cheez", "chiz", "baat", "task", "work", "job", "item",
    # function words that survive tokenisation
    "the", "a", "an", "of", "for", "about", "ka", "ki", "ke", "se", "me",
    "mein", "wala", "hai", "tha", "thi", "kya", "what", "which", "was",
    "check", "kar", "karo", "dekh", "dekho", "batao", "bata", "please",
    "mera", "meri", "mere", "my", "our", "hamara",
}


def _has_searchable_subject(text: str) -> bool:
    """Is there anything here the web could actually be asked about?

    Found in adversarial conversation A04 turn 3. "kal wala kaam"
    ("yesterday's task") matched VOLATILE on "kal", passed the
    information-request check because it contains no first-person marker,
    and routed to a WEB SEARCH -- announced with "one sec, dekhta hoon".
    A three-word back-reference to a shared conversation is the exact
    opposite of a web query. The turn needs a clarifying question, not
    Google.

    Deliberately NOT a length check: "bitcoin price" is two words and is a
    perfectly good query, while "kal wala kaam" is three words and is not.
    What separates them is whether any word names a subject.
    """
    words = re.findall(r"[\w.\-]+", text.lower())
    return any(w not in _NOT_A_SUBJECT and len(w) > 1 for w in words)


# Explicit user overrides. These always win over any heuristic.
FORCE_WEB = re.compile(
    r"\b(search (the )?(web|internet|online)|google (it|this)|look (it|this) up online)\b"
    r"|\b(web (pe|par) (search|dekho)|internet (pe|par) dekho|google karo)\b",
    re.IGNORECASE)
# Explicit instruction to consult the personal vault. This is a COMMAND,
# not a hint, and it must beat the relevance threshold in one direction
# only: it forces the grounded path so the turn is answered from the vault
# or honestly reported as absent. It never forces low-relevance chunks INTO
# the prompt -- that was F18, and injecting junk is how the assistant ended
# up talking about a thesis deadline during a question about C.
#
# Found in mandatory conversation M10 turn 3. "Meri Obsidian mein check kar
# auth ke baare mein kya likha hai" ("check my Obsidian for what it says
# about auth") routed FAST with zero retrieval, and the model answered
# "meri paas uska access nahi hai" -- it claimed to have no vault access,
# which is false. The vault was never consulted because nothing in the
# router recognised the command.
FORCE_VAULT = re.compile(
    r"\b(obsidian|my (vault|notes?)|the vault|in my notes?)\b"
    r"|\b(mere?|meri) (notes?|vault|obsidian)\b"
    r"|\b(notes? me[in]?|vault me[in]?|obsidian me[in]?)\b"
    r"|नोट्स|वॉल्ट",
    re.IGNORECASE | re.UNICODE)

# A question about the shared history. Never a web query, whatever
# temporal word it happens to contain.
#
# MEASURED, M07 t2: "Kal maine jo bola tha yaad hai?" ("remember what I
# said yesterday?") matched VOLATILE on "kal" and routed to a WEB SEARCH,
# announced with "ruko, checking".
MEMORY_QUERY = re.compile(
    r"\b(do you )?remember\b|\b(you|we) (said|told|discussed|talked|agreed)\b"
    r"|\bi (said|told you|mentioned)\b|\blast (time|week|night)\b"
    r"|\bwhat did (i|we|you) (say|tell|decide)\b"
    r"|\byaad (hai|h|hai\?|nahi)\b|\byaad\b"
    r"|\b(maine|tumne|humne|hamne) .{0,24}(bola|kaha|bataya|batayi|discuss)"
    r"|\bpehle (bataya|bola|kaha|discuss)"
    r"|याद है|मैंने कहा|तुमने कहा",
    re.IGNORECASE | re.UNICODE)


# An explicit instruction to switch language. This is an ORDER, and the
# language it is WRITTEN in is not the language it ASKS for -- "Now speak
# English" is an English sentence and "Acha ab Hindi mein bol" is a Hindi
# one, and both were previously routed by the language of the sentence
# rather than by what it demanded.
#
# MEASURED, mandatory conversation M08 -- the probe that exists for exactly
# this behaviour -- where all four turns failed. "Now speak English." was
# answered in Hindi. "Acha ab Hindi mein bol" produced "main already
# English mein hi reply kar raha hoon", which was both wrong and written in
# Hinglish.
#
# The match sets a session-sticky override that outranks per-turn
# detection until the user changes it again. An order is categorical;
# treating it as one more input to a heuristic was the mistake.
LANGUAGE_COMMAND = [
    ("hi", re.compile(
        r"\b(speak|talk|reply|answer|write|say (it|that))\s+(in\s+)?hindi\b"
        r"|\bhindi\s+(?:me|mein|men|mai|main)\s*(bol|bolo|bat|baat|likh|reply|jawab)"
        r"|\bhindi\s+(?:me|mein|men|mai|main)\b"
        r"|हिंदी में", re.IGNORECASE | re.UNICODE)),
    ("hinglish", re.compile(
        r"\b(speak|talk|reply|answer|write)\s+(in\s+)?hinglish\b"
        r"|\bhinglish\s+(?:me|mein|men|mai|main)\b"
        r"|\bmix\s+(?:me|mein|men|mai|main)\s*(bol|baat)", re.IGNORECASE | re.UNICODE)),
    ("en", re.compile(
        r"\b(speak|talk|reply|answer|write|say (it|that))\s+(in\s+)?english\b"
        r"|\benglish\s+(?:me|mein|men|mai|main)\s*(bol|bolo|bat|baat|likh|reply|jawab)"
        r"|\benglish\s+(?:me|mein|men|mai|main)\b"
        r"|अंग्रेज़ी में|इंग्लिश में", re.IGNORECASE | re.UNICODE)),
]


def language_command(text: str) -> str | None:
    """Which language is the user ORDERING, if any?

    Hinglish is checked before Hindi and English because "Hinglish mein
    baat kar" contains neither "hindi" nor "english" as a whole word, but a
    looser pattern would match it twice.
    """
    for lang, pattern in LANGUAGE_COMMAND:
        if pattern.search(text):
            return lang
    return None


# Retraction. The user is calling something OFF. This is the one pattern in
# the router that exists for safety rather than quality, so it is checked
# before everything else and it never reaches the planner.
#
# Found in mandatory conversation M11 turn 2. After "Delete this.", the user
# said "Wait, don't do that." -- and the assistant replied "Okay, keep
# going. What's next?". Nothing in the system treated a retraction as a
# retraction; it was just another turn, and the model picked a continuation
# phrasing. If a pending destructive action had existed, nothing would have
# cancelled it.
RETRACTION = re.compile(
    r"\b(wait,? (no|don'?t|stop)|don'?t do (that|it)|do not do (that|it)|"
    r"never ?mind|nvm|forget (it|that)|cancel (that|it)?|stop|abort|"
    r"undo (that|it)|hold on,? (no|don'?t)|scratch that|belay that)\b"
    r"|\b(ruko|ruk ja|mat karo?|mat kar|rehne do|rehne de|chhod do|chod do|"
    r"cancel kar|band kar|rok do|rok)\b"
    r"|रुको|मत करो|रहने दो|छोड़ दो|रोक",
    re.IGNORECASE | re.UNICODE)

FORCE_NO_TOOL = re.compile(
    r"\b(just answer|don'?t search|no search|from memory|off the top)\b"
    r"|\b(search mat karo|bas batao|khud batao)\b",
    re.IGNORECASE)

# Definitional / common-knowledge questions. These are exactly the things
# the model SHOULD answer from its own weights: "what is a for loop",
# "how many days in a week", "what does AM mean". Retrieving for them wastes
# latency and, worse, drags an unrelated note into context that the model
# will then try to use.
#
# This is the deliberate "keep basic knowledge internal" boundary. It fires
# only when no personal or volatile marker is present -- "what is my auth
# design" and "what is the latest version" both fall through to retrieval.
GENERAL_KNOWLEDGE = re.compile(
    r"^\s*(what('?s| is| are| does)|define|explain what|meaning of|"
    r"how (many|much|do|does) \w+|why (do|does|is|are))\b"
    # Declarative tag-questions. Found in conversation M06: "Python is
    # faster than C, right?" starts with a noun, missed the short-circuit,
    # fell through to retrieval, and pulled the Thesis note into a general
    # knowledge answer ("If you're working on your thesis deadline with
    # Dr. Raghavan...").
    r"|^[^?]{3,60}\b(is|are|was|were|can|does|do)\b[^?]{0,60},?\s*"
    r"(right|correct|yeah|no|na|hai na)\s*\?\s*$"
    # Hindi general-knowledge forms. Not start-anchored beyond a short
    # prefix: "din me kitne ghante hote hain" begins with "din me", and a
    # strictly anchored pattern missed it (found by the isolated
    # general-knowledge test).
    r"|^\s*(?:\w+\s+){0,3}(kya (hota|hoti|hote) (hai|hain)|"
    r"kitne? \w+ (hote|hoti|hota) (hai|hain)|"
    r"\w+ (ka|ki) matlab (kya )?(hai|hota hai)|\w+ kya (hai|hota hai))\b"
    r"|क्या (होता|होती|होते) है|का मतलब क्या",
    re.IGNORECASE | re.UNICODE)


# Turns that are pure conversation. Fast path, nothing else runs.
SMALLTALK = re.compile(
    r"^\s*(hi|hey|hello|yo|sup|good (morning|evening|night)|"
    r"how'?s it going|how are you|what'?s up|thanks|thank you|ok|okay|cool|"
    r"nice|lol|haha|bye|see you|gn|gm)\b[\s!.?]*$"
    r"|^\s*(haan|haan bhai|kya haal|kaise ho|theek hai|thik hai|acha|accha|"
    r"arre|arey|sun|suno|namaste|shukriya|bye bhai)\b[\s!.?]*$"
    r"|^\s*(हाँ|ठीक है|नमस्ते|शुक्रिया|कैसे हो|क्या हाल)\b[\s।!.?]*$",
    re.IGNORECASE | re.UNICODE)

# Intent to act, as opposed to intent to know.
ACTION_INTENT = re.compile(
    r"\b(open|launch|start|run|execute|build|deploy|push|commit|send|"
    r"create|delete|install|fix|implement|refactor|write (the )?code)\b"
    r"|\b(khol|chala|banao|bhej|likh do|kar do|band karo)\b"
    r"|खोलो|चलाओ|बनाओ|भेजो|कर दो",
    re.IGNORECASE | re.UNICODE)

# Work that a 4B model should hand off rather than attempt.
DELEGATE_INTENT = re.compile(
    r"\b(opencode|write (a|the|this) (feature|module|test|script)|"
    r"my assignment|do the assignment|refactor|debug (this|the)|"
    r"fix the (bug|test|build)|"
    r"implement (the|this|a|an)(\s+\w+){0,3}\s+(feature|api|endpoint|module|"
    r"page|component|service|handler|route|screen)|"
    r"(build|add|write) (the|this|a|an)(\s+\w+){0,3}\s+(feature|endpoint|module))\b"
    r"|\b(assignment kar|code likh|feature bana)\b",
    re.IGNORECASE | re.UNICODE)


# Words too common to signal topical relevance.
_STOP = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "do", "does",
    "did", "and", "or", "but", "if", "of", "to", "in", "on", "at", "for",
    "with", "that", "this", "it", "its", "as", "by", "from", "than", "then",
    "so", "not", "no", "yes", "you", "your", "i", "me", "my", "we", "our",
    "what", "how", "why", "when", "where", "which", "who", "right", "ok",
    "hai", "hain", "ka", "ki", "ke", "ko", "se", "me", "mein", "aur", "ya",
    "kya", "toh", "bhi", "hi", "wo", "ye", "main", "mera", "meri",
}


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[\w\u0900-\u097f]+", text.lower())
            if len(w) > 2 and w not in _STOP}


def _shares_content_word(query: str, hit) -> bool:
    """Does the retrieved chunk actually mention anything the query did?"""
    q = _content_words(query)
    if not q:
        return False
    body = f"{hit.chunk.heading_path} {hit.chunk.text}"
    return bool(q & _content_words(body))


@dataclass
class RouteConfig:
    # Injection and web-suppression are gated on RAW relevance, never on
    # the RRF fusion score -- see Hit.is_confident for why that distinction
    # matters. Injecting weak matches is worse than injecting nothing,
    # because the model will try to use whatever it is given.
    min_dense: float = 0.25       # cosine
    min_bm25: float = 1.5         # sqlite bm25, negated so higher is better
    # A relevance floor independent of the embedder's calibration: the top
    # hit must share at least one meaningful content word with the query.
    #
    # Found in M06: asked "Python is faster than C, right?", the stand-in
    # embedder scored an unrelated Thesis note above the dense threshold and
    # the model dutifully worked it into the answer. Score thresholds depend
    # on the embedder; lexical overlap does not.
    require_lexical_overlap: bool = True
    # A vault answer strong enough to make a web search unnecessary.
    strong_dense: float = 0.45
    strong_bm25: float = 4.0
    # CALIBRATION CAVEAT: these numbers were tuned against the stand-in
    # TF-IDF embedder on a small test vault. Score distributions differ
    # substantially by embedding model and by corpus size. They MUST be
    # re-tuned against the real embedder on the real vault -- sweep the
    # threshold against the eval set and pick the knee. Shipping these
    # values unmodified will over- or under-retrieve.
    max_context_chunks: int = 4
    ack_latency_ms: int = 600      # if projected wait exceeds this, speak first


@dataclass
class Route:
    path: Path
    inject: list[Hit] = field(default_factory=list)
    needs_web: bool = False
    needs_ack: bool = False
    ack_text: str = ""
    escalate: bool = False
    delegate: bool = False
    # The user explicitly named the vault. Injection still obeys the
    # relevance threshold; this only guarantees the vault is CONSULTED and
    # that an empty result is reported honestly instead of improvised.
    vault_forced: bool = False
    # The user is calling something off. Nothing may be planned or executed
    # on this turn, and any pending action is cancelled.
    retract: bool = False
    # A delegation request that has everything OpenCode needs to start.
    # Only a ready delegation may be acknowledged with "on it".
    delegate_ready: bool = False
    # A question about the shared conversation history. Answered from the
    # store; never from the web.
    memory_query: bool = False
    # The user explicitly ordered this language. The caller should make it
    # stick for the rest of the session rather than re-detecting each turn.
    lang_locked: bool = False
    lang: str = "en"
    reasons: list[str] = field(default_factory=list)

    def why(self) -> str:
        return "; ".join(self.reasons)


# Acknowledgements. Deliberately a small set, chosen by language, and the
# caller is expected to vary them -- see AckPolicy below, which exists
# because a fixed phrase repeated every time is the fastest way to make an
# assistant feel scripted.
# Acknowledgements, split by WHAT the assistant is about to do. Saying
# "let me check" before starting a twenty-minute coding task is a small
# thing that reads as wrong immediately -- checking and doing are different
# promises. Found in the end-to-end demo.
ACKS = {
    "check": {
        "en": ["one sec, checking", "let me look that up",
               "hang on, checking that"],
        "hi": ["ek second, dekhta hoon", "ruko, check karta hoon",
               "abhi dekhta hoon"],
        "hinglish": ["ek sec, let me check", "ruko, checking",
                     "one sec, dekhta hoon"],
    },
    "work": {
        "en": ["on it", "starting that now", "alright, kicking that off"],
        "hi": ["theek hai, shuru karta hoon", "chalo, kar deta hoon",
               "abhi lagta hoon ispe"],
        "hinglish": ["on it, abhi start karta hoon", "theek hai, kar deta hoon",
                     "chalo, kicking it off"],
    },
}


class AckPolicy:
    """Prevents conversational filler from becoming a verbal tic.

    The user asked for "ek second" and "hmm" to feel alive rather than
    scripted. Two rules do that: never use the same phrase twice in a row,
    and do not acknowledge at all when the wait is short enough that the
    acknowledgement is itself the delay.
    """

    def __init__(self, cooldown_turns: int = 3):
        self.cooldown = cooldown_turns
        self._recent: list[str] = []

    def pick(self, lang: str, turn_index: int = 0, kind: str = "check") -> str:
        pool = ACKS.get(kind, ACKS["check"]).get(lang, ACKS[kind]["en"])
        fresh = [p for p in pool if p not in self._recent]
        choice = (fresh or pool)[turn_index % len(fresh or pool)]
        self._recent.append(choice)
        if len(self._recent) > self.cooldown:
            self._recent.pop(0)
        return choice

    def reset(self) -> None:
        self._recent.clear()


class Router:
    def __init__(self, config: RouteConfig | None = None):
        self.cfg = config or RouteConfig()
        self.acks = AckPolicy()

    def route(self, user_text: str, vault_hits: Sequence[Hit] = (),
              turn_index: int = 0, model_requested_web: bool = False,
              uncertainty: float = 0.0, prev_lang: str = "en") -> Route:
        """Decide the path for one user turn.

        vault_hits are supplied by the caller, who ran retrieval in parallel
        with this call. Retrieval is not gated on this decision -- only
        *injection* is.
        """
        # A turn with no language evidence of its own (a bare "hmm", "ok")
        # inherits the conversation's language rather than defaulting to
        # English -- see _NEUTRAL in signals.py and conversation A01.
        lang = detect_language(user_text, default=prev_lang or "en")
        # An explicit order outranks detection, in both directions: it sets
        # the language for this turn AND is reported so the caller can make
        # it stick.
        ordered = language_command(user_text)
        if ordered:
            lang = ordered
        r = Route(path=Path.FAST, lang=lang)
        r.lang_locked = bool(ordered)

        forced_web = bool(FORCE_WEB.search(user_text))
        forbidden = bool(FORCE_NO_TOOL.search(user_text))
        forced_vault = bool(FORCE_VAULT.search(user_text))
        memory_q = bool(MEMORY_QUERY.search(user_text))

        # 0. Retraction outranks every other rule, including the explicit
        #    overrides below. "Wait, don't do that" must not be able to
        #    start anything, and it must be able to stop something.
        if RETRACTION.search(user_text):
            # The flag is set unconditionally: cancellation must not depend
            # on the rest of the sentence. Only the SHORT-CIRCUIT is
            # conditional -- "cancel that, and open opencode instead"
            # cancels AND then asks for something new, and dropping the
            # second half would be its own failure.
            r.retract = True
            r.reasons.append("user retracted")
            if not (ACTION_INTENT.search(user_text)
                    or DELEGATE_INTENT.search(user_text)):
                return r

        # 1. Explicit user override beats every heuristic.
        if forbidden:
            r.reasons.append("user forbade tools")
            return r

        # 2. Small talk short-circuits. No retrieval, no gating, no latency.
        if SMALLTALK.match(user_text.strip()) and not forced_web \
                and not forced_vault:
            r.reasons.append("smalltalk fast path")
            return r

        # 4. Common-knowledge questions answer from the model's own weights.
        #    Checked before retrieval gating so a definitional question never
        #    drags in a vault note.
        volatile_now = bool(VOLATILE.search(user_text))
        personal_now = bool(PERSONAL.search(user_text))
        if (GENERAL_KNOWLEDGE.match(user_text.strip())
                and not personal_now and not volatile_now
                and not forced_web and not forced_vault
                and not ACTION_INTENT.search(user_text)):
            r.reasons.append("general knowledge, answered internally")
            return r

        # 5. Action / delegation intent.
        if DELEGATE_INTENT.search(user_text):
            r.path, r.delegate = Path.ACTION, True
            r.reasons.append("delegation intent")
        elif ACTION_INTENT.search(user_text):
            r.path = Path.ACTION
            r.reasons.append("action intent")

        # 6. Vault injection by RELEVANCE THRESHOLD, not by model judgement.
        confident = [h for h in vault_hits
                     if h.dense_raw >= self.cfg.min_dense
                     or h.bm25_raw >= self.cfg.min_bm25]
        if self.cfg.require_lexical_overlap:
            # Overlap is required only for MARGINAL hits. A strongly-dense
            # hit is trusted without it -- demanding shared words from every
            # hit would reject exactly the semantically-relevant,
            # lexically-disjoint matches that dense retrieval exists to
            # find ("what did we decide about auth" -> "passkey decision").
            # Caught by test_strong_hit_is_injected when the first version
            # of this gate applied to everything.
            confident = [h for h in confident
                         if h.dense_raw >= self.cfg.strong_dense
                         or h.bm25_raw >= self.cfg.strong_bm25
                         or _shares_content_word(user_text, h)]
        best_dense = max((h.dense_raw for h in vault_hits), default=0.0)
        best_bm25 = max((h.bm25_raw for h in vault_hits), default=0.0)
        if confident:
            r.inject = sorted(confident, key=lambda h: -h.score)[: self.cfg.max_context_chunks]
            if r.path is Path.FAST:
                r.path = Path.GROUNDED
            r.reasons.append(
                f"vault relevant (dense={best_dense:.2f} bm25={best_bm25:.2f})")
        elif vault_hits:
            r.reasons.append(
                f"vault weak (dense={best_dense:.2f} bm25={best_bm25:.2f}), not injected")

        # 6b. The user named the vault explicitly. Take the grounded path
        #     whatever the threshold said. When nothing cleared the bar the
        #     path is still GROUNDED with an EMPTY injection, which is the
        #     state the orchestrator turns into "nothing in your notes about
        #     that" -- the honest answer, and the one the model would not
        #     have produced on its own (M10 turn 3).
        if forced_vault:
            r.vault_forced = True
            if r.path is Path.FAST:
                r.path = Path.GROUNDED
            r.reasons.append("user named the vault explicitly")

        # 7. Web gating. A temporal word only counts when the turn is
        #    actually asking for information and is not the user describing
        #    their own state.
        volatile = (volatile_now and _is_information_request(user_text)
                    and _has_searchable_subject(user_text))
        personal = personal_now
        strong_vault = (best_dense >= self.cfg.strong_dense
                        or best_bm25 >= self.cfg.strong_bm25)

        if memory_q and not forced_web:
            # A question about the two of you is answered from the store or
            # not at all.
            r.memory_query = True
            r.reasons.append("memory question, web suppressed")
        elif forced_vault and not forced_web:
            # "check my notes for X" is a vault instruction. Reading it as a
            # volatile web query as well is how M10 turn 3 and turn 4 ended
            # up answering an Obsidian question from a search engine.
            r.reasons.append("vault named explicitly, web suppressed")
        elif forced_web:
            r.needs_web = True
            r.reasons.append("user forced web")
        elif volatile and not strong_vault:
            r.needs_web = True
            r.reasons.append("volatile query without strong vault answer")
        elif model_requested_web and not strong_vault \
                and _has_searchable_subject(user_text):
            r.needs_web = True
            r.reasons.append("model requested web")
        elif uncertainty >= 0.7 and not strong_vault and not personal \
                and _has_searchable_subject(user_text):
            r.needs_web = True
            r.reasons.append(f"high uncertainty {uncertainty:.2f}")

        if r.needs_web:
            r.path = Path.WEB

        # 8. Acknowledgement. Only when the wait is long enough to notice
        #    AND something is actually about to happen.
        #
        #    The second condition is not decoration. Measured in mandatory
        #    conversation M10 turn 1 ("OpenCode khol."), M10 turn 2 and M11
        #    turn 3 ("Mera assignment kar de."): every one of them emitted
        #    "on it, abhi start karta hoon" / "chalo, kicking it off" and
        #    then, in the same turn, asked a clarifying question and started
        #    nothing. actions=[] and pending=[] in the run log confirm it --
        #    the assistant announced work it never began, three times out of
        #    three. An acknowledgement is a promise; promising and then
        #    asking "which assignment?" is worse than not speaking at all.
        #
        #    build_brief is deterministic, model-free and already knows the
        #    difference, so the router can consult it before it promises.
        #    NOTE: the delegation flag itself stays TRUE. The request IS a
        #    delegation; it is simply not ready to start. Clearing the flag
        #    was the first attempt and six frozen scenario checks caught it
        #    immediately -- callers read `delegate` to know what the user
        #    asked for, not whether it can begin.
        if r.delegate:
            from .opencode import build_brief
            r.delegate_ready = build_brief(user_text).is_actionable
            if not r.delegate_ready:
                r.reasons.append("delegation incomplete, ack withheld")

        if r.needs_web or (r.delegate and r.delegate_ready):
            r.needs_ack = True
            # Delegation is "on it", retrieval is "checking". Using the wrong
            # one makes the assistant sound like it misunderstood the task.
            kind = "work" if (r.delegate and not r.needs_web) else "check"
            r.ack_text = self.acks.pick(lang, turn_index, kind=kind)

        return r
