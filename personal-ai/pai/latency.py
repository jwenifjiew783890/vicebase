"""Latency budget model for the voice pipeline on the target laptop.

Target hardware: RTX 4050 Laptop (6 GB VRAM), 16 GB RAM, Core i7.

The metric that matters is TIME TO FIRST AUDIO -- how long after the user
stops speaking before they hear something. Decode tokens/sec is the number
everyone quotes and the wrong one: a pipeline can decode at 60 tok/s and
still feel broken if prefill, endpointing or TTS startup dominate.

Human conversational gaps average ~200ms. Under 1s reads as attentive,
1-2s as thoughtful, over 2.5s as broken.

All figures below are estimates from published benchmarks for this class of
hardware, not measurements on the user's machine. They are here to size the
architecture and to identify which component dominates -- which turns out
to be TTS startup, not the LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Stage:
    name: str
    ms: float
    parallel: bool = False   # overlapped with something else, so free
    note: str = ""


@dataclass
class Budget:
    label: str
    stages: list[Stage]

    @property
    def critical_path_ms(self) -> float:
        return sum(s.ms for s in self.stages if not s.parallel)

    @property
    def hidden_ms(self) -> float:
        return sum(s.ms for s in self.stages if s.parallel)

    def verdict(self) -> str:
        t = self.critical_path_ms
        if t < 1000:
            return "responsive"
        if t < 1800:
            return "acceptable"
        if t < 2500:
            return "sluggish"
        return "broken"

    def render(self) -> str:
        w = max(len(s.name) for s in self.stages)
        lines = [f"{self.label}"]
        for s in self.stages:
            tag = "  (parallel)" if s.parallel else ""
            lines.append(f"  {s.name:<{w}}  {s.ms:6.0f} ms{tag}"
                         + (f"   # {s.note}" if s.note else ""))
        lines.append(f"  {'-' * (w + 12)}")
        lines.append(f"  {'TIME TO FIRST AUDIO':<{w}}  "
                     f"{self.critical_path_ms:6.0f} ms   [{self.verdict()}]")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Component estimates (RTX 4050 6GB / i7 / 16GB)
# ---------------------------------------------------------------------------

VAD_ENDPOINT     = 220    # Silero VAD + semantic endpointing, tuned
STT_FINALISE     = 150    # Qwen3-ASR-0.6B streaming, tail after endpoint
VAULT_RETRIEVAL  = 35     # sqlite-vec + FTS5 hybrid, CPU
MEMORY_ASSEMBLE  = 10     # rule block from SQLite, prompt-cached
LLM_PREFILL_CACHED = 130  # ~300 new tokens; system header is cache-hit
LLM_FIRST_TOKEN  = 35
TOKENS_TO_CLAUSE = 15     # tokens needed before the first TTS chunk
DECODE_TOK_S     = 45     # Qwen3.5-4B Q4_K_M on 4050, conservative

TTS_FIRST_AUDIO = {
    # Kokoro-82M: fast, CPU-viable, but weak Hindi.
    "kokoro":   120,
    # IndicF5: flow-matching. Strong Hindi, single-engine Hinglish, but
    # startup cost is the dominant term in the whole pipeline.
    "indicf5":  700,
    # Sarvam Bulbul v3 (cloud API): sub-250ms streaming, single-pass
    # Hinglish, but leaves the machine.
    "sarvam":   250,
}

WEB_SEARCH = 1800         # search + fetch + extract + rerank
ESCALATE_8B = 900         # load-resident 8B first token
DELEGATE_OPENCODE = 4000  # agent accepts the task and reports back


def _decode_ms(tokens: int = TOKENS_TO_CLAUSE, tok_s: float = DECODE_TOK_S) -> float:
    return 1000.0 * tokens / tok_s


def budget_fast(tts: str = "kokoro") -> Budget:
    """Casual conversation. Nothing retrieved, nothing escalated."""
    return Budget(f"FAST PATH  (smalltalk, tts={tts})", [
        Stage("VAD + endpointing", VAD_ENDPOINT, note="dominates perceived responsiveness"),
        Stage("STT finalise", STT_FINALISE),
        Stage("vault retrieval", VAULT_RETRIEVAL, parallel=True, note="runs anyway, not injected"),
        Stage("memory assemble", MEMORY_ASSEMBLE),
        Stage("LLM prefill (cached)", LLM_PREFILL_CACHED),
        Stage("LLM first token", LLM_FIRST_TOKEN),
        Stage("decode to first clause", _decode_ms()),
        Stage("TTS first audio", TTS_FIRST_AUDIO[tts]),
    ])


def budget_grounded(tts: str = "kokoro") -> Budget:
    """Vault context injected. Retrieval was parallel; prefill grows."""
    return Budget(f"GROUNDED  (vault injected, tts={tts})", [
        Stage("VAD + endpointing", VAD_ENDPOINT),
        Stage("STT finalise", STT_FINALISE),
        Stage("vault retrieval", VAULT_RETRIEVAL, parallel=True),
        Stage("memory assemble", MEMORY_ASSEMBLE),
        Stage("LLM prefill (+1.5k ctx)", LLM_PREFILL_CACHED + 260),
        Stage("LLM first token", LLM_FIRST_TOKEN),
        Stage("decode to first clause", _decode_ms()),
        Stage("TTS first audio", TTS_FIRST_AUDIO[tts]),
    ])


def budget_web(tts: str = "kokoro") -> Budget:
    """Web search. The wait is real, so it is MASKED by speaking first."""
    return Budget(f"WEB  (masked by acknowledgement, tts={tts})", [
        Stage("VAD + endpointing", VAD_ENDPOINT),
        Stage("STT finalise", STT_FINALISE),
        Stage("route decision", 1),
        Stage("ACK decode (3 tokens)", _decode_ms(3)),
        Stage("TTS first audio (ack)", TTS_FIRST_AUDIO[tts]),
        Stage("web search", WEB_SEARCH, parallel=True, note="user is hearing the ack"),
        Stage("answer prefill + decode", LLM_PREFILL_CACHED + 400 + _decode_ms(),
              parallel=True),
    ])


# Optimisations that buy back time on the critical path. Each is cheap to
# implement and none of them touch the model.
VAD_ENDPOINT_TUNED = 150   # semantic endpointing instead of a fixed silence gap
CLAUSE_TOKENS_TUNED = 8    # split on commas/danda, not only sentence ends


def budget_optimised(tts: str, grounded: bool = True) -> Budget:
    """Same pipeline with endpointing and clause-splitting tuned."""
    ctx = 260 if grounded else 0
    return Budget(
        f"OPTIMISED {'grounded' if grounded else 'fast'} (tts={tts})", [
            Stage("VAD + endpointing (tuned)", VAD_ENDPOINT_TUNED),
            Stage("STT finalise", STT_FINALISE),
            Stage("vault retrieval", VAULT_RETRIEVAL, parallel=True),
            Stage("memory assemble", MEMORY_ASSEMBLE),
            Stage("LLM prefill", LLM_PREFILL_CACHED + ctx),
            Stage("LLM first token", LLM_FIRST_TOKEN),
            Stage("decode to first clause", _decode_ms(CLAUSE_TOKENS_TUNED)),
            Stage("TTS first audio", TTS_FIRST_AUDIO[tts]),
        ])


def choose_tts(measured_first_audio_ms: dict[str, float],
               target_ms: float = 1500.0,
               allow_cloud: bool = False) -> tuple[str, str]:
    """Pick the TTS engine from MEASURED first-audio times on real hardware.

    The estimates in this module size the architecture; they do not decide
    it. Run the measurement, then call this.

    Ordering rationale: a single engine handling both languages beats any
    routing scheme, because switching engines mid-conversation changes the
    voice audibly and a companion assistant with an unstable voice reads as
    broken. So a local single-engine option is preferred even at some
    latency cost, and language-routing is the last resort, not the first.
    """
    def fits(name):
        v = measured_first_audio_ms.get(name)
        return v is not None and _budget_with(v) <= target_ms

    if fits("indicf5"):
        return "indicf5", "local, single engine, strong Hindi, meets target"
    if allow_cloud and fits("sarvam"):
        return "sarvam", ("cloud, single-pass Hinglish; NOTE: response text "
                          "leaves the machine and may contain vault content")
    # Compare BUDGETS, not raw engine latency -- an earlier version compared
    # the engine's ms against a whole-pipeline threshold and accepted a
    # 1600 ms engine that puts the pipeline at 2.5 s.
    indic_budget = _budget_with(measured_first_audio_ms.get("indicf5", 1e9))
    if indic_budget <= target_ms + 400:
        return "indicf5", (f"local single engine, {indic_budget:.0f} ms "
                           f"slightly over {target_ms:.0f} ms target, accepted")
    return "split", ("last resort: Kokoro for pure-English turns, IndicF5 "
                     "otherwise. Voice identity will shift audibly between "
                     "languages -- verify this is tolerable before shipping")


def _budget_with(tts_ms: float) -> float:
    return (VAD_ENDPOINT_TUNED + STT_FINALISE + MEMORY_ASSEMBLE
            + LLM_PREFILL_CACHED + 260 + LLM_FIRST_TOKEN
            + _decode_ms(CLAUSE_TOKENS_TUNED) + tts_ms)


def all_budgets(tts: str = "kokoro") -> list[Budget]:
    return [budget_fast(tts), budget_grounded(tts), budget_web(tts)]


VRAM_MB = {
    "qwen3.5-4b-q4_k_m weights": 2500,
    "kv cache 8k @ q8":           420,
    "cuda context + runtime":     420,
    "qwen3-asr-0.6b int8":        700,
    "draft model 0.8b q4":        520,
    "desktop/display reserve":    450,
}


def vram_report(include_draft: bool = True, include_stt_on_gpu: bool = True,
                total_mb: int = 6144) -> dict:
    items = dict(VRAM_MB)
    if not include_draft:
        items.pop("draft model 0.8b q4")
    if not include_stt_on_gpu:
        items.pop("qwen3-asr-0.6b int8")
    used = sum(items.values())
    return {"items": items, "used_mb": used, "total_mb": total_mb,
            "free_mb": total_mb - used, "fits": used <= total_mb}


if __name__ == "__main__":
    print("OPTIMISED CRITICAL PATH BY TTS ENGINE")
    for tts in ("kokoro", "sarvam", "indicf5"):
        for grounded in (False, True):
            b = budget_optimised(tts, grounded)
            print(f"  {b.label:44} {b.critical_path_ms:6.0f} ms  [{b.verdict()}]")
    print()
    print("=" * 66)
    for tts in ("kokoro", "sarvam", "indicf5"):
        print()
        for b in all_budgets(tts):
            print(b.render()); print()
        print("=" * 66)
    print("\nVRAM on 6144 MB (RTX 4050 Laptop):")
    for cfg, kw in [("LLM + STT + draft", {}),
                    ("LLM + STT, no draft", {"include_draft": False}),
                    ("LLM only, STT on CPU",
                     {"include_draft": False, "include_stt_on_gpu": False})]:
        r = vram_report(**kw)
        status = "FITS" if r["fits"] else "OVER BUDGET"
        print(f"  {cfg:26} {r['used_mb']:5} MB used, "
              f"{r['free_mb']:5} MB free  [{status}]")
