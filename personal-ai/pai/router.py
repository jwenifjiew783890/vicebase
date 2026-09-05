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

# Explicit user overrides. These always win over any heuristic.
FORCE_WEB = re.compile(
    r"\b(search (the )?(web|internet|online)|google (it|this)|look (it|this) up online)\b"
    r"|\b(web (pe|par) (search|dekho)|internet (pe|par) dekho|google karo)\b",
    re.IGNORECASE)
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
    r"|^\s*(kya (hota|hoti|hote) (hai|hain)|kitne \w+ (hote|hoti) hain|"
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


@dataclass
class RouteConfig:
    # Injection and web-suppression are gated on RAW relevance, never on
    # the RRF fusion score -- see Hit.is_confident for why that distinction
    # matters. Injecting weak matches is worse than injecting nothing,
    # because the model will try to use whatever it is given.
    min_dense: float = 0.25       # cosine
    min_bm25: float = 1.5         # sqlite bm25, negated so higher is better
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
              uncertainty: float = 0.0) -> Route:
        """Decide the path for one user turn.

        vault_hits are supplied by the caller, who ran retrieval in parallel
        with this call. Retrieval is not gated on this decision -- only
        *injection* is.
        """
        lang = detect_language(user_text)
        r = Route(path=Path.FAST, lang=lang)

        forced_web = bool(FORCE_WEB.search(user_text))
        forbidden = bool(FORCE_NO_TOOL.search(user_text))

        # 1. Explicit user override beats every heuristic.
        if forbidden:
            r.reasons.append("user forbade tools")
            return r

        # 2. Small talk short-circuits. No retrieval, no gating, no latency.
        if SMALLTALK.match(user_text.strip()) and not forced_web:
            r.reasons.append("smalltalk fast path")
            return r

        # 3. Common-knowledge questions answer from the model's own weights.
        #    Checked before retrieval gating so a definitional question never
        #    drags in a vault note.
        volatile_now = bool(VOLATILE.search(user_text))
        personal_now = bool(PERSONAL.search(user_text))
        if (GENERAL_KNOWLEDGE.match(user_text.strip())
                and not personal_now and not volatile_now
                and not forced_web and not ACTION_INTENT.search(user_text)):
            r.reasons.append("general knowledge, answered internally")
            return r

        # 4. Action / delegation intent.
        if DELEGATE_INTENT.search(user_text):
            r.path, r.delegate = Path.ACTION, True
            r.reasons.append("delegation intent")
        elif ACTION_INTENT.search(user_text):
            r.path = Path.ACTION
            r.reasons.append("action intent")

        # 5. Vault injection by RELEVANCE THRESHOLD, not by model judgement.
        confident = [h for h in vault_hits
                     if h.dense_raw >= self.cfg.min_dense
                     or h.bm25_raw >= self.cfg.min_bm25]
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

        # 6. Web gating.
        volatile = volatile_now
        personal = personal_now
        strong_vault = (best_dense >= self.cfg.strong_dense
                        or best_bm25 >= self.cfg.strong_bm25)

        if forced_web:
            r.needs_web = True
            r.reasons.append("user forced web")
        elif volatile and not strong_vault:
            r.needs_web = True
            r.reasons.append("volatile query without strong vault answer")
        elif model_requested_web and not strong_vault:
            r.needs_web = True
            r.reasons.append("model requested web")
        elif uncertainty >= 0.7 and not strong_vault and not personal:
            r.needs_web = True
            r.reasons.append(f"high uncertainty {uncertainty:.2f}")

        if r.needs_web:
            r.path = Path.WEB

        # 7. Acknowledgement. Only when the wait is long enough to notice.
        if r.needs_web or r.delegate:
            r.needs_ack = True
            # Delegation is "on it", retrieval is "checking". Using the wrong
            # one makes the assistant sound like it misunderstood the task.
            kind = "work" if (r.delegate and not r.needs_web) else "check"
            r.ack_text = self.acks.pick(lang, turn_index, kind=kind)

        return r
