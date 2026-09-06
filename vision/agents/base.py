"""What an agent is, and what it is not allowed to get away with.

The rule this file exists to enforce: **a step is a thing that happened.**
An agent may not report a step it did not execute, and may not report
success it did not observe. Every Step carries the actual result of an
actual operation, and `AgentResult.ok` is computed from those steps rather
than asserted by the agent.

That is the difference between an agent harness and a story about one.
"""
from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


@dataclass
class Step:
    """One real operation, with what it actually returned."""
    action: str                  # "web.search", "file.read", "shell.run"
    detail: str = ""             # human-readable: the query, the path
    ok: bool = True
    output: str = ""             # what came back, truncated for display
    error: str = ""
    ms: float = 0.0
    started_at: float = field(default_factory=time.time)

    def as_dict(self) -> dict:
        return {"action": self.action, "detail": self.detail, "ok": self.ok,
                "output": self.output[:4000], "error": self.error,
                "ms": round(self.ms, 1)}


@dataclass
class AgentResult:
    summary: str = ""
    detail: str = ""
    steps: list[Step] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)
    needs_confirmation: dict | None = None

    @property
    def ok(self) -> bool:
        """Computed, never asserted. An agent that ran nothing did not
        succeed, and an agent whose steps failed did not succeed however
        confident its summary sounds."""
        return bool(self.steps) and all(s.ok for s in self.steps)

    @property
    def ran(self) -> int:
        return len(self.steps)

    def as_dict(self) -> dict:
        return {"ok": self.ok, "summary": self.summary, "detail": self.detail,
                "steps": [s.as_dict() for s in self.steps],
                "artifacts": self.artifacts,
                "needs_confirmation": self.needs_confirmation}


@dataclass
class AgentContext:
    """What an agent is given. Deliberately narrow.

    An agent gets the store, the vault and the gateway -- never the raw
    conversation model and never unrestricted OS access. Anything dangerous
    goes through `gateway`, which applies the same permission tiers and
    confirmation rules the conversational path uses.
    """
    store: Any = None
    vault: Any = None
    gateway: Any = None
    llm: Any = None              # optional: for synthesis, not for control
    session_id: str = "default"
    emit: Callable[[dict], None] | None = None   # live progress to the UI

    def progress(self, message: str, **extra) -> None:
        if self.emit:
            self.emit({"type": "agent_progress", "message": message, **extra})


class Agent(Protocol):
    name: str
    description: str
    def run(self, task: str, ctx: AgentContext) -> AgentResult: ...


class BaseAgent:
    """Convenience base: gives subclasses a `step()` that cannot lie.

    `step` runs the callable, times it, records what came back, and marks
    the step failed if it raised. An agent cannot record a successful step
    without something actually having succeeded.
    """
    name = "base"
    description = ""
    dangerous = False

    def __init__(self):
        self._steps: list[Step] = []

    def step(self, action: str, detail: str, fn: Callable[[], Any],
             ctx: AgentContext | None = None) -> Any:
        s = Step(action=action, detail=detail)
        t0 = time.perf_counter()
        try:
            out = fn()
            s.output = "" if out is None else str(out)
            s.ok = True
            return out
        except Exception as exc:
            s.ok = False
            s.error = f"{type(exc).__name__}: {exc}"
            s.output = traceback.format_exc(limit=3)
            return None
        finally:
            s.ms = (time.perf_counter() - t0) * 1000
            self._steps.append(s)
            if ctx:
                ctx.progress(f"{self.name}: {action} {detail}"[:160],
                             ok=s.ok, action=action)

    def result(self, summary: str, detail: str = "", **kw) -> AgentResult:
        r = AgentResult(summary=summary, detail=detail, steps=list(self._steps), **kw)
        self._steps = []
        return r
