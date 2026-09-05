"""Real local model adapter via llama.cpp.

Implements the ConversationAdapter and OrchestratorAdapter protocols that
orchestrator.py declares, so the same runtime that was tested with stubs
runs against actual weights with no changes above this line.

The two adapters share one loaded model but differ in everything that
matters: the conversation adapter sees untrusted retrieved content and is
sampled for natural speech; the orchestrator adapter never sees retrieved
content and is sampled near-greedily for structure.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .gateway import Action, REGISTRY


@dataclass
class GenStats:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    ttft_ms: float = 0.0
    total_ms: float = 0.0

    @property
    def tok_per_s(self) -> float:
        secs = (self.total_ms - self.ttft_ms) / 1000.0
        return self.completion_tokens / secs if secs > 0 else 0.0


class LlamaBackend:
    """Thin wrapper so the model is loaded once and shared."""

    def __init__(self, model_path: str, n_ctx: int = 4096,
                 n_threads: int | None = None, verbose: bool = False):
        from llama_cpp import Llama
        self.llm = Llama(model_path=model_path, n_ctx=n_ctx,
                         n_threads=n_threads, verbose=verbose, logits_all=False)
        self.model_path = model_path

    def chat(self, messages: list[dict], *, max_tokens: int = 300,
             temperature: float = 0.7, top_p: float = 0.9,
             stop: Sequence[str] | None = None,
             repeat_penalty: float = 1.05) -> tuple[str, GenStats]:
        t0 = time.perf_counter()
        first_at: float | None = None
        chunks: list[str] = []
        stream = self.llm.create_chat_completion(
            messages=messages, max_tokens=max_tokens, temperature=temperature,
            top_p=top_p, stop=list(stop or []), repeat_penalty=repeat_penalty,
            stream=True)
        for part in stream:
            delta = part["choices"][0].get("delta", {}).get("content")
            if delta:
                if first_at is None:
                    first_at = time.perf_counter()
                chunks.append(delta)
        total = (time.perf_counter() - t0) * 1000
        text = "".join(chunks).strip()
        stats = GenStats(
            prompt_tokens=sum(len(self.llm.tokenize(m["content"].encode()))
                              for m in messages),
            completion_tokens=len(self.llm.tokenize(text.encode())) if text else 0,
            ttft_ms=((first_at - t0) * 1000) if first_at else total,
            total_ms=total)
        return text, stats


# ---------------------------------------------------------------------------
# Conversation adapter
# ---------------------------------------------------------------------------

class LlamaConversation:
    """Speaks. Never emits actions. Sees untrusted content."""

    def __init__(self, backend: LlamaBackend, max_tokens: int = 300,
                 temperature: float = 0.7):
        self.backend = backend
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.last: GenStats | None = None

    def respond(self, system: str, history: Sequence[dict],
                user: str, context: str) -> str:
        msgs = [{"role": "system", "content": system}]
        for h in history:
            role = h["role"] if h["role"] in ("user", "assistant") else None
            if role and h["text"].strip():
                msgs.append({"role": role, "content": h["text"]})
        # Drop the current user turn if the caller already logged it.
        if msgs and msgs[-1]["role"] == "user" and msgs[-1]["content"] == user:
            msgs.pop()
        content = f"{context}\n\n{user}" if context else user
        msgs.append({"role": "user", "content": content})
        text, stats = self.backend.chat(
            msgs, max_tokens=self.max_tokens, temperature=self.temperature)
        self.last = stats
        return _strip_thinking(text)


_THINK = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


def _strip_thinking(text: str) -> str:
    """Remove reasoning blocks. They must never reach the user or TTS.

    The unterminated case matters and an earlier version got it wrong: when
    the model hits its token budget mid-thought there is no closing tag, and
    splitting on the tag returned the reasoning itself as the reply. Anything
    after an unclosed <think> is reasoning, not an answer, so it is dropped
    entirely -- the caller sees an empty string and can retry or fall back,
    which is strictly better than speaking the model's private notes aloud.
    """
    out = _THINK.sub("", text)
    lowered = out.lower()
    if "<think>" in lowered:
        # Keep only what precedes the unclosed tag.
        out = out[:lowered.index("<think>")]
    # A stray closing tag with no opener: keep what follows it.
    lowered = out.lower()
    if "</think>" in lowered:
        out = out[lowered.index("</think>") + len("</think>"):]
    return out.strip()


# ---------------------------------------------------------------------------
# Orchestrator adapter
# ---------------------------------------------------------------------------

PLANNER_SYSTEM = """You convert a user request into tool calls.

Reply with ONLY a JSON array. No prose, no markdown fence, no explanation.
Empty array [] if no tool is needed.

Each element: {"action": "<name>", "args": {...}}

Available actions and their required args:
%s

Rules:
- Use ONLY the action names listed above.
- Include every required arg.
- If the user is just talking, return [].
"""


def _catalogue() -> str:
    lines = []
    for name, cap in REGISTRY.items():
        args = ", ".join(f"{k}: {cap.schema[k].__name__}" for k in cap.required)
        lines.append(f'- {name}({args}) — {cap.description}')
    return "\n".join(lines)


class LlamaPlanner:
    """Proposes typed actions. Never speaks, never sees retrieved content.

    Sampled near-greedily: this output is parsed, not read. The gateway
    validates whatever comes out, so a malformed plan is a PARSE_ERR rather
    than a hazard.
    """

    def __init__(self, backend: LlamaBackend, max_tokens: int = 160):
        self.backend = backend
        self.max_tokens = max_tokens
        self.last_raw = ""
        self.last: GenStats | None = None

    def plan(self, user: str, memory: str) -> list[Action]:
        msgs = [
            {"role": "system", "content": PLANNER_SYSTEM % _catalogue()},
            {"role": "user", "content": user},
        ]
        raw, stats = self.backend.chat(msgs, max_tokens=self.max_tokens,
                                       temperature=0.0, top_p=1.0)
        self.last_raw, self.last = raw, stats
        return self._parse(_strip_thinking(raw), user)

    @staticmethod
    def _parse(raw: str, user: str) -> list[Action]:
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if not m:
            return []
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return []
        out: list[Action] = []
        for item in data if isinstance(data, list) else []:
            if isinstance(item, dict) and "action" in item:
                out.append(Action(str(item["action"]),
                                  dict(item.get("args") or {}),
                                  reason=f"user said: {user[:80]}"))
        return out
