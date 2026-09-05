# Conversation Quality Report

**System under test:** Qwen3.5-4B-Q4_K_M (unsloth GGUF), llama.cpp CPU,
4 threads, n_ctx 4096, driven through the full `pai/` runtime — memory,
router, gateway, retrieval, learning loop.

**This is a real model.** Not a stub, not role-play, not a simulation.
2.6 GB of weights downloaded from HuggingFace and run locally.

---

## 0. Evidence classification

Every claim in this report carries one of these labels. Nothing researched
is presented as measured.

| Label | Meaning |
|---|---|
| **MEASURED** | Observed by running code in this environment |
| **RESEARCHED** | From published sources; not reproduced here |
| **SIMULATED** | Produced by a model of the system, not the system |
| **NOT TESTED** | Could not be exercised here; stated as unknown |

### What is MEASURED

- Conversational behaviour of Qwen3.5-4B-Q4_K_M across real multi-turn
  conversations in English, Hindi and Hinglish
- Response length, question rate, generic-assistant phrasing, filler use,
  language matching, cross-turn repetition, opener variety
- Routing decisions on real utterances
- Model load time, time-to-first-token, tokens/sec **on 4 CPU cores**
- Hindi ASR word error rate on real human speech with ground truth
- 126 unit tests, 135 frozen scenario checks, 180-day drift simulation

### What is NOT TESTED

- **Everything on the RTX 4050.** No GPU in this environment. All CPU
  timings are CPU timings and must not be read as laptop timings.
- **TTS.** No audio devices, no audio tooling, no TTS model installed.
  Naturalness, time-to-first-audio and Hinglish voice switching are
  entirely unverified.
- **Live voice interaction** — endpointing, barge-in, interruption
  handling, code-switched ASR on conversational speech.
- **The fine-tuned model.** Everything here is the *stock* base model with
  a system prompt. No LoRA, no SFT, no DPO. This is the Phase-0 baseline.

---

## 1. Test inventory

| Category | Conversations | Turns | Status |
|---|---|---|---|
| Casual English | 1 | 4 | MEASURED |
| Casual Hindi | 1 | 4 | MEASURED |
| Hinglish | 1 | 3 | MEASURED |
| Persona A/B (v1 vs v2) | 12 | ~44 | MEASURED |
| Learning loop end-to-end | 1 | 8 | MEASURED |
| Cross-session memory | — | — | MEASURED (plumbing, no model) |
| Hindi ASR | 10 samples | — | MEASURED |
| Voice / TTS | 0 | 0 | **NOT TESTED** |

---

## 2. Round 1 — what actually happened

### Transcript 001 — cold open, casual English

```
USER: hey
AI:   hey                                              [1 word]

USER: not much, just got back
AI:   glad you're back.                                [4 words]

USER: yeah it was alright
AI:   alright. what's on your mind?                    [6 words]

USER: i'm bored honestly
AI:   bored? try watching that new thriller Muaz mentioned, or just
      scroll through the news for 5 mins before lying down.   [20 words]
```

**Worked.** Genuinely conversational. "hey" → "hey" is the correct answer
and most assistants cannot produce it. Zero generic-assistant phrasing.

**Failed.** Turn 4 invented a personal memory. There is no thriller
anywhere in the vault, memory, or prompt. It also referred to the user in
the third person while speaking to him. → **F1**

### Transcript 002 — casual Hindi

```
USER: kya haal hai
AI:   Bhai, sab badhiya. Tu?                           [4 words]

USER: yaar kya kar raha hai
AI:   Bas logon se baat kar raha hoon aur kaam ki update dekh raha hoon.
      Kya haal hai?                                    [17 words]

USER: bas timepass
AI:   Arre haan, bas timepass karna hi sabse normal hai. Thoda break
      chahiye?                          [12 words, lang misdetected as en]

USER: aaj bahut thak gaya hoon
AI:   [route=web  ack='ek sec, let me check']
      Aa jaata hai, baar-baar kaam padhne ya logon se baat karne ke baad.
      Kya abhi koi specific kaam hai jise dhund raha hai, ya sirf
      chillana hai?                                    [28 words]
```

**Worked.** *"Bhai, sab badhiya. Tu?"* is exactly how a person talks. Not
textbook, not Sanskritised, not translated. This is the single most
encouraging result in the whole exercise — natural Hindi came free from the
stock model with no fine-tuning.

**Failed.**
- Turn 4 routed to **web search** because the user said he was tired. → **F2**
- Turn 3 language misdetected as English → wrong TTS voice. → **F3**
- A question on **100% of turns**. → **F4**
- Turn 4's content is also semantically loose ("sirf chillana hai" —
  "just want to shout?").

### Transcript 003 — Hinglish with a real thought

```
USER: yaar mujhe lag raha hai ye idea actually kaam kar sakta hai, but ek
      problem hai
AI:   Yaar, batao problem kya hai? Agar idea sahi hai toh roadblocks alag
      se handle hote hain.                             [16 words]

USER: problem ye hai ki latency bahut zyada hogi
AI:   Latency ka matlab hai response time bahut lamba ho jayega. Agar user
      wait karega, toh engagement toot sakta hai. Kya ye latency network
      ki wajah se hai ya model architecture ki?        [31 words]

USER: hmm, tu kya sochta hai
AI:   Sach baat ye hai: latency badhna ek dealbreaker hai agar idea
      real-time use karne wala hai. ... toh user experience "broken" lagta
      hai (Source: General UX principles).
      Tera idea kaam kar sakta hai, lekin sirf tab jab latency ko fix
      karein. ...                                      [79 words]
```

**Worked.** Register mirroring is excellent. Turn 2's clarifying question
("network ki wajah se hai ya model architecture ki?") is a genuinely useful
question, not filler.

**Failed.**
- Length grew **16 → 31 → 79 words**, the longest reply to the shortest
  prompt. → **F5**
- **Invented a citation**: `(Source: General UX principles)`. → **F6**

### Round 1 aggregate — MEASURED over 11 real turns

| Metric | Value | Read |
|---|---|---|
| mean words/reply | 19.8 | reasonable |
| max words | 79 | too long for the prompt that caused it |
| generic-assistant phrases | **0** | excellent |
| question rate | **73%** | a tic |
| language match | 91% | good, one miss |
| cross-turn repetition | 0.06 | excellent |
| opener variety | 100% | excellent |
| honest "I don't know" | 0 | untested in round 1 |

**The pattern.** None of the six failures is the model failing to be
*fluent*. All six are failures of *discipline* — inventing detail,
over-asking, over-growing, over-citing. That is consistent with the thesis
that conversational polish at 4B is a prompt-and-post-training problem, not
a capacity problem.

---

## 3. Latency — MEASURED, and what it does and does not tell you

Over the same 11 real turns, on **4 CPU cores**:

| | median | min | max |
|---|---|---|---|
| time-to-first-token | **11,419 ms** | 9,628 | 22,910 |
| decode | **5.8 tok/s** | 0.8 | 6.3 |

The 22.9 s outlier is the web-routed turn, which also paid for the
acknowledgement generation.

**What this does NOT tell you.** These are CPU numbers. The target is an
RTX 4050. `pai/latency.py` models that GPU at 45 tok/s decode and
130–390 ms prefill — roughly 7× the decode rate measured here, and far
faster prefill, since prefill is compute-bound and that is what a GPU is
for. Those figures remain **RESEARCHED**. Nothing in this environment can
verify them.

**What it does tell you.** Two things worth keeping:

1. **The architecture's latency behaviour is visible and correct even at
   5.8 tok/s.** The fast path did no retrieval and no tool call; the web
   path emitted its acknowledgement before the slow work. The
   *ordering* is right, which is the part the design controls.

2. **Prefill dominates.** TTFT was 10–14 s while decode contributed only a
   few seconds for short replies. That is the same shape the GPU model
   predicts, and it is why prompt caching of the system header is not a
   micro-optimisation — it is the main lever.

---

## 4. What is wired, and what is only declared

An honesty point that matters for reading everything above. The capability
registry declares 18 tools with schemas, permission tiers and audit
coverage. **Three have real backends** in this environment:

| Capability | Backend | Status |
|---|---|---|
| `obsidian.search` | hybrid BM25 + dense over the test vault | **wired** |
| `obsidian.read` | vault chunk lookup | **wired** |
| `memory.recall` | SQLite fact query | **wired** |
| `web.search`, `web.fetch` | — | declared, **no backend** |
| `code.delegate` (OpenCode) | — | declared, **no backend** |
| `browser.act`, `computer.control` | — | declared, **no backend** |
| `shell.run`, `file.delete`, `git.push`, … | — | declared, **no backend** |

So: routing, schema validation, taint checking, permission tiering,
confirmation flow and audit logging are exercised end to end against a real
model. **Execution is not**, except for vault and memory reads.

This was itself a defect worth fixing. Unimplemented capabilities used to
return `None`, which the gateway typed as `EMPTY` — and `EMPTY`'s guidance
tells the model *"say you could not find it, do NOT answer from memory."*
That is a false statement when the truth is the tool does not exist. They
now raise, typing as `EXEC_ERR` with the reason.

---

## 5. Persona A/B — v1 vs v2 on identical conversations

**Why the comparison is valid.** llama.cpp uses a fixed default seed, and
v1 conversations 001–003 reproduced their round-1 metrics **exactly**
(001: 7.8 mean words; 002: 15.2 mean / 100% question rate; 003: 42.0 mean /
79 max). Identical inputs, identical sampling — the only variable is the
persona text.

**v1 baseline (480 chars) — all six cases, MEASURED**

| case | what it probes | mean words | question rate | max |
|---|---|---|---|---|
| 001 | casual EN | 7.8 | 50% | 20 |
| 002 | casual HI | 15.2 | 100% | 28 |
| 003 | Hinglish | 42.0 | 67% | 79 |
| 004 | brevity after correction | **95.0** | 0% | **122** |
| 008 | honest unknown | 24.7 | 100% | 29 |
| 009 | disagreement | 48.0 | 0% | 62 |

**v2 (1583 chars, a clause per defect) — MEASURED**

| case | mean words | question rate | max | verdict |
|---|---|---|---|---|
| 001 | 7.8 → **13.0** | 50% → **75%** | 20 → 27 | **worse** |
| 002 | 15.2 → 14.5 | 100% → **100%** | 28 → 22 | flat |
| 003 | 42.0 → **23.0** | 67% → **33%** | 79 → **33** | **better** |
| 004 | 95.0 → **35.5** | 0% → 0% | 122 → **48** | **much better** |

### The finding, and my own wrong first reading

After two cases I concluded persona instructions were simply a weak lever at
4B. Case 003 then produced a large clean win. **The correct reading is
regression toward the mean.**

v2's LENGTH clause says *"default to one or two sentences."* That
**lengthens** a one-word reply ("hey" → a sentence) and **shortens** a
95-word one. It pulls every reply toward the same middle:

| case | v1 mean | v2 mean | change |
|---|---|---|---|
| 001 | 7.8 | 13.0 | **+67%** |
| 002 | 15.2 | 14.5 | −5% |
| 003 | 42.0 | 23.0 | −45% |
| 004 | 95.0 | 35.5 | **−63%** |

The effect is **monotonic across all four cases**: the longer v1's replies
were, the more v2 shortened them, with a fixed point at roughly **15
words**. (Correlation between v1 length and the v2 change is −1.000, though
with n=4 that number is degenerate — the pattern, not the coefficient, is
the evidence, and it has a clear mechanism.)

The instruction was the wrong *shape*: **absolute where the behaviour should
be relative**. v1 actually said "match his length" and got 7.8 words on
casual turns; it simply had no brake on growth. The right rule combines
both — mirror his length, and never grow across a conversation.

**On the single most important case this is a large win.** Case 004 is where
the user said *"arre nahi, itna bada answer mat do. simple bol."* v1
ignored it and averaged 95 words; v2 averaged 35.5 and capped at 48. The
correction still is not fully obeyed — 35 words is not "simple bol" — but
the gap closed by nearly two thirds.

**One thing did not move at all.** Question rate on case 002 stayed at
**100% under both personas**, despite v2 stating in plain English "Do not
end every message with a question." A direct, unambiguous negative
instruction had zero measured effect. That is the clearest single argument
in this exercise for post-training over prompting — and it is consistent
with the mechanism that a negative instruction raises the salience of the
forbidden thing.

### The asymmetry that matters most

| Fix made in | Held? |
|---|---|
| Deterministic code — routing (F2), language ID (F3), reasoning leak (F7), prompt assembly (F8/F9), tool honesty | **All held** |
| Persona instruction — brevity (F5), questions (F4), invention (F1), citations (F6) | **Partial or reversed** |

This is the practical argument for the architecture's central claim: keep
as much behaviour as possible in code, and treat the model as the language
layer rather than the control layer.

**Persona v3** (318 chars, positively phrased, *relative* length rule) was
written as the counter-hypothesis. It is **untested** — a hypothesis, not a
recommendation.

---

## 6. Learning loop, end to end

*Filled in from `eval/transcripts/learning/`.*

---

## 7. Hindi ASR — MEASURED

*Filled in from `eval/transcripts/asr_hi.json`.*

---

## 8. Acceptance criteria

*Assessed below against measured evidence only.*

---

## 9. Verdict

*Below.*
