"""Vision: one assistant, composed of the parts that already work.

This is the only object the application talks to. It owns the persistent
store, the vault, the model, the conversational orchestrator and the agent
harness, and it decides -- deterministically -- whether a turn is
conversation or work.

What it deliberately does NOT do is re-implement any of that. The router,
the capability gateway, the trust levels and the four honesty guards are
the parts of this project that were hardened by 54 documented failures, and
they are used here unchanged.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import config
from .dispatch import classify
from .agents.base import AgentContext
from .agents.registry import get as get_agent, describe as describe_agents
from . import agents as _agents  # noqa: F401  (populates the registry)
from .agents import builtin as _builtin  # noqa: F401
from .jobs import JobStore
from .mcp import McpRegistry


@dataclass
class Reply:
    text: str = ""
    session_id: str = "default"
    route: str = "fast"
    lang: str = "en"
    agent: str | None = None
    agent_result: dict | None = None
    evidence: int = 0
    guard: str = ""
    learned: list = field(default_factory=list)
    ms: float = 0.0
    spoken: bool = False

    def as_dict(self) -> dict:
        return {"text": self.text, "session_id": self.session_id,
                "route": self.route, "lang": self.lang, "agent": self.agent,
                "agent_result": self.agent_result, "evidence": self.evidence,
                "guard": self.guard, "learned": [list(l) for l in self.learned],
                "ms": round(self.ms, 1)}


class Vision:
    def __init__(self, *, db_path: str | None = None,
                 vault_path: str | None = None, load_llm: bool = True):
        config.ensure_dirs()
        from .core.memory import MemoryStore
        from .core.gateway import Gateway
        from .core.router import Router
        from .core.learning import LearningLoop
        from .core.obsidian import VaultIndex, TfidfEmbedder
        from .core.orchestrator import Orchestrator

        self.db_path = db_path or str(config.DB_PATH)
        self.store = MemoryStore(self.db_path)          # persistent, on disk
        self.gateway = Gateway()
        self.router = Router()
        self.learning = LearningLoop(self.store)
        self.vault = VaultIndex(TfidfEmbedder())
        self.vault_path: str | None = None
        self.vault_notes = 0
        self._lock = threading.Lock()

        self.llm = None
        self.conversation = None
        self.planner = None
        self.llm_error: str | None = None
        if load_llm:
            self._load_llm()

        self.orch = Orchestrator(self.store, self.vault, self.conversation,
                                 self.planner, gateway=self.gateway,
                                 router=self.router, learning=self.learning)

        # Agents that can run for minutes get a job rather than a request.
        self.jobs = JobStore(self.db_path, self._run_job)
        # Plugins: every connected MCP server and the tools it exposes.
        self.mcp = McpRegistry()

        path = vault_path or config.OBSIDIAN_VAULT
        if path:
            self.connect_vault(path)

    # Agents whose work routinely outlasts a chat round-trip. Everything
    # else answers inline, because turning a two-second lookup into a job
    # makes the assistant feel slower, not more capable.
    LONG = {"crew", "research", "browser", "coding"}

    def _run_job(self, agent_name: str, task: str, job) -> dict:
        """Executed on a job thread. Progress goes to the job log."""
        def emit(ev: dict) -> None:
            msg = ev.get("message") or ev.get("type", "")
            if msg:
                self.jobs.note(job, str(msg))
        ctx = AgentContext(store=self.store, vault=self.vault,
                           gateway=self.gateway, mcp=self.mcp,
                           llm=self._raw_llm if self.conversation else None,
                           session_id=job.session_id, emit=emit)
        agent = get_agent(agent_name)
        if agent is None:
            return {"ok": False, "summary": f"no agent named {agent_name!r}"}
        return agent.run(task, ctx).as_dict()

    # ------------------------------------------------------------- model
    def _load_llm(self) -> None:
        from .core.llm import LlamaBackend, LlamaConversation, LlamaPlanner
        if not Path(config.LLM_PATH).exists():
            self.llm_error = f"model not found at {config.LLM_PATH}"
            return
        try:
            kw = {}
            if config.LLM_GPU_LAYERS:
                kw["n_gpu_layers"] = config.LLM_GPU_LAYERS
            self.backend = LlamaBackend(config.LLM_PATH, n_ctx=config.LLM_CTX,
                                        n_threads=config.LLM_THREADS, **kw)
            self.conversation = LlamaConversation(self.backend,
                                                  max_tokens=config.LLM_MAX_TOK)
            self.planner = LlamaPlanner(self.backend, max_tokens=140)
            self.llm_error = None
        except Exception as exc:
            self.llm_error = f"{type(exc).__name__}: {exc}"

    def _raw_llm(self, prompt: str, max_tokens: int = 300) -> str:
        """A plain completion, for agents that need synthesis.

        Agents get this rather than the conversation adapter: they are not
        having a conversation and must not inherit the persona, the memory
        header or the retrieved context.
        """
        if self.conversation is None:
            return ""
        out, _ = self.backend.chat(
            [{"role": "system", "content": "You are a precise assistant. "
              "Answer only what is asked, with no preamble."},
             {"role": "user", "content": prompt}],
            max_tokens=max_tokens, temperature=0.4)
        from .core.llm import _strip_thinking
        return _strip_thinking(out)

    # ------------------------------------------------------------- vault
    def connect_vault(self, path: str) -> dict:
        """Index a real directory of markdown notes."""
        p = Path(path).expanduser()
        if not p.is_dir():
            return {"ok": False, "error": f"not a directory: {p}"}
        from .core.obsidian import VaultIndex, TfidfEmbedder
        idx = VaultIndex(TfidfEmbedder())
        n = 0
        for md in sorted(p.rglob("*.md")):
            try:
                idx.add_note(str(md.relative_to(p)),
                             md.read_text(encoding="utf-8", errors="replace"),
                             md.stat().st_mtime)
                n += 1
            except Exception:
                continue
        idx.build_vectors()
        with self._lock:
            self.vault = idx
            self.orch.vault = idx
            self.vault_path = str(p)
            self.vault_notes = n
        return {"ok": True, "path": str(p), "notes": n,
                "chunks": len(idx.chunks)}

    # ------------------------------------------------------------- turn
    def respond(self, session_id: str, text: str,
                emit: Callable[[dict], None] | None = None,
                *, channel: str = "text", background: bool = True) -> Reply:
        t0 = time.perf_counter()
        d = classify(text)

        if d.agent:
            if emit:
                emit({"type": "agent_start", "agent": d.agent,
                      "task": d.task, "reason": d.reason})
            # Work that routinely outlasts a chat round-trip becomes a job:
            # the user gets an id and a live log instead of a frozen tab,
            # and the result is still there after a restart.
            if background and d.agent in self.LONG:
                agent = get_agent(d.agent)
                payload = d.utterance if getattr(
                    agent, "wants_utterance", False) else d.task
                job = self.jobs.start(d.agent, payload, session_id)
                if emit:
                    emit({"type": "job_started", "job": job.as_dict()})
                return Reply(
                    text=(f"Working on it -- {d.agent} is running as job "
                          f"{job.id}. I'll keep the log updated."),
                    session_id=session_id, route="job", agent=d.agent,
                    agent_result={"ok": True, "summary": "job started",
                                  "job_id": job.id, "steps": []},
                    ms=(time.perf_counter() - t0) * 1000)
            ctx = AgentContext(store=self.store, vault=self.vault,
                               gateway=self.gateway, mcp=self.mcp,
                               llm=self._raw_llm if self.conversation else None,
                               session_id=session_id, emit=emit)
            agent = get_agent(d.agent)
            # Agents that act on an instruction need the verb; agents that
            # search are better off without it. `wants_utterance` says which.
            payload = d.utterance if getattr(agent, "wants_utterance", False) else d.task
            res = agent.run(payload, ctx)
            spoken = self._narrate(res, text)
            from .core.trust import Trust
            self.store.add_turn(session_id, "user", text, Trust.USER)
            self.store.add_turn(session_id, "assistant", spoken, Trust.MODEL)
            return Reply(text=spoken, session_id=session_id, route="agent",
                         agent=d.agent, agent_result=res.as_dict(),
                         ms=(time.perf_counter() - t0) * 1000)

        if self.conversation is None:
            return Reply(
                text=("I can't talk yet -- no language model is loaded. "
                      f"({self.llm_error})"),
                session_id=session_id, route="error",
                ms=(time.perf_counter() - t0) * 1000)

        from .core.gateway import Channel
        ch = Channel.VOICE if channel == "voice" else Channel.TEXT
        with self._lock:
            r = self.orch.handle(session_id, text, ch)
        return Reply(text=r.text, session_id=session_id,
                     route=r.route.path.value, lang=r.route.lang,
                     evidence=r.evidence, guard=r.guard_tripped,
                     learned=list(r.learned),
                     ms=(time.perf_counter() - t0) * 1000)

    def _narrate(self, res, original: str) -> str:
        """Turn an agent result into something a person would say.

        The narration is derived from the result, never from the request:
        if the agent failed, this says so. An assistant that reports
        success because the user asked for success is the failure mode this
        whole project is about.
        """
        if res.needs_confirmation:
            return (f"{res.summary} Say 'confirm' if you want me to do it "
                    f"anyway.")
        if not res.ok:
            failed = [s for s in res.steps if not s.ok]
            if not failed:
                # Nothing was attempted. That is a capability reporting that
                # it cannot run here, not a thing that was tried and broke,
                # and "it didn't work: nothing ran" reads like the latter.
                return f"{res.summary} {res.detail}".strip()
            return f"{res.summary} It didn't work: {failed[0].error}"
        return res.summary if not res.detail else f"{res.summary}\n\n{res.detail}"

    # ------------------------------------------------------------- status
    def status(self) -> dict:
        facts = list(self.store.db.execute(
            "SELECT COUNT(*) c FROM facts WHERE valid_to IS NULL"))[0]["c"]
        turns = list(self.store.db.execute(
            "SELECT COUNT(*) c FROM turns"))[0]["c"]
        return {
            "llm": {"path": config.LLM_PATH,
                    "loaded": self.conversation is not None,
                    "error": self.llm_error},
            "memory": {"db": self.db_path, "facts": facts, "turns": turns,
                       "rules": len(self.store.active_rules())},
            "vault": {"path": self.vault_path, "notes": self.vault_notes,
                      "chunks": len(self.vault.chunks)},
            "agents": describe_agents(),
            "plugins": self.mcp.describe(),
            "mcp_tools": [t.as_dict() for t in self.mcp.tools()],
        }
