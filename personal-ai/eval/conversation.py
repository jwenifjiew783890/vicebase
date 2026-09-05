"""Real conversation runner: drives the orchestrator against actual weights
and records full transcripts.

Produces the transcript format the acceptance criteria ask for, plus the
per-turn measurements (TTFT, tokens/sec, route, latency) that make the
qualitative judgements checkable.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Sequence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pai.gateway import Channel, Gateway
from pai.learning import LearningLoop, PipelineConfig
from pai.memory import MemoryStore
from pai.obsidian import VaultIndex, TfidfEmbedder
from pai.orchestrator import Orchestrator
from pai.router import Router
from pai.signals import detect_language


@dataclass
class Turn:
    user: str
    ai: str
    route: str
    lang: str
    ack: str = ""
    injected: int = 0
    actions: list = field(default_factory=list)
    pending: list = field(default_factory=list)
    ttft_ms: float = 0.0
    total_ms: float = 0.0
    tok_s: float = 0.0
    out_tokens: int = 0
    words: int = 0
    sentences: int = 0
    evidence: int = 0
    guard: str = ""
    lang_retry: bool = False
    lang_obeyed: bool = True
    cancelled: list = field(default_factory=list)


@dataclass
class Transcript:
    test_id: str
    scenario: str
    turns: list[Turn] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        L = [f"TEST #{self.test_id}", f"Scenario:", f"  {self.scenario}", ""]
        for t in self.turns:
            L.append(f"USER:\n  {t.user}")
            meta = [f"route={t.route}", f"lang={t.lang}"]
            if t.ack:
                meta.append(f"ack={t.ack!r}")
            if t.injected:
                meta.append(f"vault={t.injected}")
            if t.actions:
                meta.append("ran=" + ",".join(a for a in t.actions))
            if t.pending:
                meta.append("gate=" + ",".join(p for p in t.pending))
            if t.evidence:
                meta.append(f"evidence={t.evidence}")
            if t.cancelled:
                meta.append("cancelled=" + ",".join(t.cancelled))
            if t.guard:
                meta.append(f"GUARD={t.guard}")
            if t.lang_retry:
                meta.append("lang-retry="
                            + ("obeyed" if t.lang_obeyed else "STILL WRONG"))
            meta.append(f"{t.words}w/{t.sentences}s")
            meta.append(f"ttft={t.ttft_ms:.0f}ms")
            meta.append(f"{t.tok_s:.1f}tok/s")
            L.append(f"AI:  [{' '.join(meta)}]\n  {t.ai}")
            L.append("")
        return "\n".join(L)


def count_words(s: str) -> int:
    return len(re.findall(r"[\wऀ-ॿ]+", s))


def count_sentences(s: str) -> int:
    parts = [p for p in re.split(r"[.!?।]+", s) if p.strip()]
    return max(1, len(parts)) if s.strip() else 0


DEFAULT_VAULT = {
 "Projects/ViceBase.md": """# ViceBase
## Auth decisions
We moved from passwords to passkeys in ViceBase. Internal codename is
Thornbury. Decision taken after the security review in February.
See [[Passkey Rollout]].
## Deployment
Deploys go through Vercel on merge to main. Staging is deployed first and
soaks for an hour.
""",
 "Projects/Passkey Rollout.md": """# Passkey Rollout
Phase 1 ships in March covering web. Phase 2 covers the mobile client.
Blocker: Safari 16 fallback.
""",
 "Notes/Thesis.md": """# Thesis
Chapter 3 covers retrieval evaluation. Deadline is 14 November.
Supervisor is Dr Raghavan.
""",
}


class Harness:
    """One user, one persistent memory, many sessions."""

    def __init__(self, conversation, planner=None, vault_notes=None,
                 evidence_threshold: int = 3, seed_facts=None, persona=None):
        self.store = MemoryStore()
        self.vault = VaultIndex(TfidfEmbedder())
        for p, t in (vault_notes or DEFAULT_VAULT).items():
            self.vault.add_note(p, t)
        self.vault.build_vectors()
        self.learning = LearningLoop(
            self.store, config=PipelineConfig(evidence_threshold=evidence_threshold))
        self.conversation = conversation
        self.orch = Orchestrator(self.store, self.vault, conversation, planner,
                                 gateway=Gateway(), router=Router(),
                                 learning=self.learning, persona=persona)
        from pai.trust import Trust
        for s, p, o in (seed_facts or []):
            self.store.assert_fact(s, p, o, Trust.USER)

    def converse(self, test_id: str, scenario: str, session: str,
                 user_turns: Sequence[str],
                 channel: Channel = Channel.TEXT) -> Transcript:
        tr = Transcript(test_id, scenario)
        for text in user_turns:
            res = self.orch.handle(session, text, channel)
            stats = getattr(self.conversation, "last", None)
            tr.turns.append(Turn(
                user=text, ai=res.text, route=res.route.path.value,
                lang=res.route.lang, ack=res.ack,
                injected=len(res.route.inject),
                actions=[f"{a.action.name}[{a.status.value}]" for a in res.actions],
                pending=[f"{d.action.name}->{d.verdict.name}" for d in res.pending],
                ttft_ms=getattr(stats, "ttft_ms", 0.0),
                total_ms=getattr(stats, "total_ms", 0.0),
                tok_s=getattr(stats, "tok_per_s", 0.0),
                out_tokens=getattr(stats, "completion_tokens", 0),
                words=count_words(res.text), sentences=count_sentences(res.text),
                evidence=res.evidence, guard=res.guard_tripped,
                cancelled=list(res.cancelled),
                lang_retry=res.language_retry,
                lang_obeyed=res.language_obeyed))
        return tr

    # convenience for memory/learning tests
    def new_session(self) -> str:
        return f"s{int(time.time()*1000)%100000}"

    def active_rules(self):
        return self.store.active_rules()

    def review_queue(self):
        return self.learning.review_queue()
