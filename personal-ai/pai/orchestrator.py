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

import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Protocol, Sequence

from .gateway import (Action, Channel, Decision, ExecResult, ExecStatus,
                      Gateway, Tainted, Verdict, execute, wrap_untrusted)
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


BASE_PERSONA = """You are Muaz's personal assistant. You talk like a sharp,
warm friend who happens to know things -- not like a chatbot.

- Match his language. English, Hindi or a mix, whichever he used. Natural
  spoken Hindi, never textbook Hindi.
- Match his length. Short question, short answer. No preamble, no
  restating the question, no closing summary.
- When you are told something from his notes or the web, say where it came
  from. When you are not, do not present a guess as a fact.
"""


class Orchestrator:
    def __init__(self, store: MemoryStore, vault: VaultIndex,
                 conversation: ConversationAdapter,
                 planner: OrchestratorAdapter | None = None,
                 gateway: Gateway | None = None,
                 router: Router | None = None,
                 learning: LearningLoop | None = None):
        self.store = store
        self.vault = vault
        self.conversation = conversation
        self.planner = planner
        self.gateway = gateway or Gateway()
        self.router = router or Router()
        self.learning = learning or LearningLoop(store)
        self.turn_index = 0

    # ------------------------------------------------------------ prompt

    def build_system_prompt(self, lang: str) -> str:
        """Assemble the always-on header. This is what gets prompt-cached.

        Order matters: persona, then protected rules, then learned rules.
        Protected first means that if anything downstream truncates, the
        honesty guarantees are the last thing to go, not the first.
        """
        rules = self.learning.system_rules_block(lang=lang)
        facts = self._memory_header()
        parts = [BASE_PERSONA]
        if rules:
            parts.append("How to talk to Muaz:\n" + rules)
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
        t_m = time.perf_counter()
        res.text = self.conversation.respond(system, history, user_text, context)
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
        """Tool dispatch. Real implementations are injected per capability."""
        if action.name == "obsidian.search":
            return self.vault.search(action.args["query"], k=action.args.get("k", 5))
        return None
