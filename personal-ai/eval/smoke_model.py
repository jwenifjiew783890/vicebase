"""Quick check that the model loads, generates, and how fast."""
import os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from pai.llm import LlamaBackend, LlamaConversation, _strip_thinking

MODEL = sys.argv[1] if len(sys.argv) > 1 else "/tmp/models/Qwen3.5-4B-Q4_K_M.gguf"
t0 = time.time()
b = LlamaBackend(MODEL, n_ctx=2048, n_threads=4)
print(f"load: {time.time()-t0:.1f}s")

for label, msgs, mt in [
    ("EN short", [{"role":"system","content":"You are a warm, brief friend. One or two sentences."},
                  {"role":"user","content":"hey, what's up"}], 60),
    ("HI short", [{"role":"system","content":"You are a warm, brief friend. Reply in natural spoken Hindi (Devanagari or roman), one or two sentences."},
                  {"role":"user","content":"yaar kya kar raha hai"}], 60),
]:
    t = time.time()
    out, st = b.chat(msgs, max_tokens=mt, temperature=0.7)
    out = _strip_thinking(out)
    print(f"\n[{label}] ttft={st.ttft_ms:.0f}ms tok/s={st.tok_per_s:.1f} "
          f"out_tok={st.completion_tokens} wall={time.time()-t:.1f}s")
    print(f"  {out!r}")
