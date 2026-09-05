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

    # ------------------------------------------------------------ prompt

    def build_system_prompt(self, lang: str) -> str:
        """Assemble the always-on header. This is what gets prompt-cached.

        Order matters: persona, then protected rules, then learned rules.
        Protected first means that if anything downstream truncates, the
        honesty guarantees are the last thing to go, not the first.
        """
        rules = _second_person(self.learning.system_rules_block(lang=lang))
        facts = self._memory_header()
        parts = [self.persona]
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

        route = self.router.route(user_text, hits, turn_index=self.turn_index)
        res.route = route
        self.turn_index += 1

        # Speak the acknowledgement BEFORE the slow work starts. This is the
        # whole reason the web path feels fast.
        if route.needs_ack:
            res.ack = route.ack_text

        # Untrusted context is fenced and tainted. The conversation adapter
        # is the only component that sees it, and it cannot act.
        context = ""
        if route.inject:
            blocks = [str(h.as_context()) for h in route.inject]
            context = wrap_untrusted("\n\n".join(blocks), "obsidian-vault")

        system = self.build_system_prompt(route.lang)
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

        self.store.add_turn(session_id, "assistant", res.text, Trust.MODEL,
                            lang=route.lang)

        # Actions come from a SEPARATE adapter that never saw `context`.
        if route.path is Path.ACTION and self.planner is not None:
            memory = self._memory_header()
            for action in self.planner.plan(user_text, memory):
                decision = self.gateway.submit(action, Trust.USER, channel)
                if decision.verdict is Verdict.ALLOW:
                    res.actions.append(execute(decision, self._runner))
                else:
                    res.pending.append(decision)

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
