# Personal AI — a local conversational runtime

A personal AI system for a single user, built around a small local LLM
running on consumer hardware. English, Hindi and Hinglish.

**Target hardware:** RTX 4050 Laptop (6 GB VRAM), 16 GB RAM, Core i7
**Model:** Qwen3.5-4B-Q4_K_M (Apache-2.0) under llama.cpp, not fine-tuned

---

## The architectural claim

> A **deterministic personal-agent runtime**, in which a small LLM is the
> language interface and personality layer — and is the component trusted
> **least** with decisions.

Routing, permissions, memory writes and action validation are ordinary
code. The model understands and speaks. It does not decide. That is the
difference between a system that works at 4B and one that needs 70B.

## Current state — MEASURED

| | |
|---|---|
| Unit tests | **374 passed**, 3 skipped (opt-in live network) |
| Frozen scenario checks | **183 / 183** |
| Mutation audit | **88 applied, 88 killed, 0 survived** |
| Real conversations | **110 transcripts, 373 user turns** |
| Documented failures | **46 found, 46 fixed** |
| Completion bar | **28 YES · 3 PARTIAL · 0 NO** |

The three non-YES items are all hardware: no GPU, no audio device, no
OpenCode install. Every RTX 4050 latency figure and every ASR/WER figure in
the reports is **RESEARCHED**, not measured — see the limitations.

## Start here

- **[`FINAL_HANDOFF/INDEX.md`](FINAL_HANDOFF/INDEX.md)** — the complete,
  self-contained handoff: what was built, what works, what was tested,
  what remains, and where everything lives.
- [`personal-ai/docs/FINAL-REPORT-R3.md`](personal-ai/docs/FINAL-REPORT-R3.md)
  — the authoritative report, 35 sections.
- [`personal-ai/docs/CONVERSATION-FAILURES.md`](personal-ai/docs/CONVERSATION-FAILURES.md)
  — all 46 failures, each quoted from a real transcript.
- [`docs/conversational-llm-architecture.md`](docs/conversational-llm-architecture.md)
  and [`docs/personal-ai-architecture.md`](docs/personal-ai-architecture.md)
  — the R&D evaluation and the design it produced.

## Layout

```
personal-ai/
  pai/         the runtime -- 14 modules, 5,736 lines
  tests/       374 tests across 16 files
  eval/        21 harnesses; transcripts/ and evidence/
  docs/        reports, including superseded ones kept on purpose
docs/          the R&D evaluation and architecture design
FINAL_HANDOFF/ portable record of the whole project
```

## Running it

Pure Python standard library. No package manager, no build step. A real
model is needed only for the conversation harnesses; everything below runs
without one.

```bash
cd personal-ai
python3 -m unittest discover -s tests -t .   # 374 tests, ~10s
python3 eval/harness.py                      # 183/183 scenario checks
python3 eval/extractor_sweep.py              # extractor over 373 real turns
python3 eval/tally.py                        # counts transcripts on disk
python3 eval/mutation_audit.py               # 88 mutations, ~15 min
```

For live inference, `pip install llama-cpp-python` and point the adapter at
a GGUF. `pai/llm.py` imports `llama_cpp` lazily, so the suite runs without it.

## How to read the evidence

Every claim in the reports carries one of four labels, and the distinction
is the point of the project:

**MEASURED** — it ran here · **RESEARCHED** — a published figure, not
verified here · **SIMULATED** — from a simulation, not the real system ·
**NOT ACTUALLY TESTED** — stated so it is not mistaken for a result.

An earlier version of this project marked three requirements as passing on
the strength of green unit tests. All three components were unreachable at
runtime. That discovery is why the mutation audit exists and why the
superseded reports are kept rather than deleted.

## Licence

MIT — see [`LICENSE`](LICENSE).
