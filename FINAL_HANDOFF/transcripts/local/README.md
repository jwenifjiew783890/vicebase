# Local conversation transcripts — real model, real replies

Produced by `personal-ai/eval/local_conversations.py` driving the full
runtime against actual weights. Every file carries its own header: test id,
category, UTC timestamp, model path, exact configuration, and hardware.

**Model:** Qwen3.5-4B-Q4_K_M.gguf (unsloth GGUF of Qwen/Qwen3.5-4B,
Apache-2.0, 2,740,937,888 bytes)
**Config:** `n_ctx=4096 n_threads=4 max_tokens=160 backend=llama.cpp/CPU
persona=BASE_PERSONA(v3)`
**Hardware:** CPU only. No GPU was present. 7.0–8.0 tok/s, TTFT 7.5–12.6 s.

## Three rounds, and why all three are kept

| Directory | What it is |
|---|---|
| `round1_before_fixes/` | **The failing run.** 22 conversations, before any fix. Kept because five defects are visible in it and deleting them would hide what was actually wrong. |
| `round2_after_fixes/` | The same 22 after fixing L1, L2, L3 (first attempt) and L5. Shows L2 and L5 fixed, L3 **not** fixed, and the residual E05 problem that only became visible once L1 was out of the way. |
| `round3_after_retry/` | Six conversations after replacing the failed L3 directive with a measured retry. Shows E04 going from 7 words to 115 with a worked example. |

Read them in that order and the failure-driven loop is legible without the
report: what broke, what was changed, what that changed, and what did not
move.

## The failures these transcripts contain

Named so nothing has to be inferred from silence.

| Round 1 | Outcome |
|---|---|
| **E05** "wait no, it's the 21st" → *"Got it, cancelled."* | Fixed in round 2, then a deeper problem appeared. Still failing — see the report. |
| **E07 t2** breakfast question ran a **web search** | Fixed. Round 2 answers locally. |
| **E04** "explain it properly, with an example" → 25 words, no example | Round 2 made it **worse** (7 words). Fixed in round 3 (115 words + worked example). |
| **P01** "main kis editor use karta hoon?" → *"Neovim use karta hoon"* ("**I** use Neovim") | Fixed. Round 2 answers in the third person. |
| **E09** "is 14:00 2pm?" → *"No, 14:00 is 2 PM."* | **Not fixed.** Proven to be the bare model: 2 contradictions in 4 with no runtime at all. |
| **H01** Hindi register natural, content degraded and repetitive | **Not fixed.** 4B capacity. |

## Reading the run log

```
AI:  [route=grounded lang=en vault=1 evidence=1 18w/2s ttft=11251ms 7.5tok/s]
```

`evidence=` is the one to watch. A confident, well-sourced-sounding reply
with `evidence=0` means the content was invented — three of the worst
defects in this project were invisible in the reply text alone and showed
up only here.

Other fields: `route=` fast/grounded/web/action · `guard=` an honesty guard
overwrote the reply · `learned=` a fact was written to memory ·
`q-retry=` / `lang-retry=` a bounded retry fired · `ran=` / `gate=` a
capability executed or was held at the gateway.
