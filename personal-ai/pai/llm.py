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

    # Spoken when the model produces nothing usable. Deliberately short and
    # in-character rather than an error string, because this reaches TTS.
    FALLBACKS = {
        "en": "sorry, lost my thread there - say that again?",
        "hi": "arre, dhyan hat gaya - phir se bolo?",
        "hinglish": "sorry yaar, thread kho gaya - phir se bolo?",
    }

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
        out = _strip_thinking(text)

        # Stripping an unterminated reasoning block can leave nothing at all
        # (see F7). One retry with a larger budget and no thinking room,
        # then a short in-character fallback -- never an empty turn and
        # never an error string, because this text goes to TTS.
        if not out:
            retry, stats2 = self.backend.chat(
                msgs + [{"role": "assistant", "content": ""}],
                max_tokens=self.max_tokens + 120,
                temperature=max(0.3, self.temperature - 0.2))
            self.last = stats2
            out = _strip_thinking(retry)
        if not out:
            from .signals import detect_language
            out = self.FALLBACKS.get(detect_language(user), self.FALLBACKS["en"])
        return out


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


def _strip_fences(text: str) -> str:
    """Remove markdown code fences, keeping their contents."""
    text = _strip_thinking(text)
    return re.sub(r"```(?:json|javascript)?\s*|```", "", text).strip()


def _json_objects(text: str) -> list[dict]:
    """Every top-level {...} in the text that parses as a JSON object.

    A brace counter rather than a regex: `args` is itself an object, so
    `\{.*?\}` stops at the wrong brace and `\{.*\}` swallows several
    objects into one unparsable span.
    """
    out: list[dict] = []
    depth = start = 0
    in_str = escaped = False
    for i, ch in enumerate(text):
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth:
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        continue
                    if isinstance(obj, dict):
                        out.append(obj)
    return out


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
        """Extract actions from whatever shape the model actually emitted.

        MEASURED, and this is the reason the method looks like this.
        `eval/planner_reliability.py` put twelve unambiguous action requests
        to the 4B planner. Eleven produced correct, well-formed JSON:

            push this to main
              -> {"action": "git.push", "args": {...}}
            delete /tmp/scratch.txt
              -> {"action": "file.delete", "args": {"path": "/tmp/scratch.txt"}}

        and the previous implementation returned [] for every single one,
        because it searched for a JSON *array* and the model emitted a bare
        *object*. Score: 0/12 actions, 0/12 times the gateway was reached.

        The consequence was not a missing feature. The capability registry,
        the permission tiers, the confirmation rules, the voice rule and the
        audit log were all unreachable in normal use -- every one of them
        unit-tested and green, and none of them ever handed anything to
        validate. That is exactly the failure the mandatory conversation set
        was written to catch: A06 asked for a push to main on the voice
        channel, got a chatty reply, and exercised nothing.

        So this accepts what the model actually produces: an array, a bare
        object, several objects in a row, and any of those inside a markdown
        fence. It stays strict about what it does with them -- names and
        argument types are still the gateway's business, not this parser's.
        """
        text = _strip_fences(raw)
        items: list[dict] = []

        m = re.search(r"\[.*\]", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(0))
                items = [d for d in data
                         if isinstance(d, dict) and "action" in d]
            except json.JSONDecodeError:
                items = []
        # The array branch also fires on an array NESTED inside a single
        # action -- browser.act carries a `steps` list -- and comes back
        # with the steps instead of the action. Requiring "action" above
        # and falling through here is what makes that case parse.
        if not items:
            items = _json_objects(text)

        out: list[Action] = []
        for item in items:
            if "action" not in item:
                continue
            args = dict(item.get("args") or {})
            # Some outputs flatten the arguments to the top level:
            #   {"action": "file.delete", "path": "/tmp/old.log"}
            # Lifting them is safe -- the gateway validates names and types
            # afterwards, so a wrong key becomes a typed refusal, not a
            # hazard.
            for k, v in item.items():
                if k not in ("action", "args") and k not in args:
                    args[k] = v
            out.append(Action(str(item["action"]), args,
                              reason=f"user said: {user[:80]}"))
        return out
