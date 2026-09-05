# Personal AI

A personal AI system built around a small conversational LLM
(Qwen3.5-4B-Q4_K_M, Apache-2.0), for English, Hindi and Hinglish, targeting
an RTX 4050 laptop with 6 GB of VRAM.

**Start here: [`docs/FINAL-REPORT-R3.md`](docs/FINAL-REPORT-R3.md)** — the
full report, with every claim labelled MEASURED / RESEARCHED / SIMULATED /
NOT TESTED, including three corrections to claims made in an earlier
version of it.

## The layout

    pai/trust.py          provenance + the privilege invariant
    pai/memory.py         four-tier store (bitemporal T2, capped T3)
    pai/signals.py        feedback detection + language ID, EN / HI / Hinglish
    pai/learning.py       candidate -> evidence -> review -> promote -> decay
    pai/gateway.py        permission tiers, taint tracking, injection defence
    pai/obsidian.py       heading-aware chunking + hybrid BM25/dense retrieval
    pai/router.py         every deterministic routing decision
    pai/orchestrator.py   turn lifecycle, persona, honesty guards
    pai/llm.py            llama.cpp adapters + planner parsing
    pai/web.py            web search with a hard time budget
    pai/opencode.py       deterministic task briefs
    pai/voice.py          endpointing, clause chunking, barge-in

Stdlib only (Python 3.11, sqlite3 + FTS5) for the deterministic core. No
torch, no numpy: it runs on the target laptop without a dependency tree,
and the model-facing pieces sit behind interfaces so the whole turn
lifecycle is testable without inference.

## Running things

    python3 -m unittest discover -s tests            # the test suite
    python3 eval/mutation_audit.py                   # is the suite real?
    python3 eval/harness.py                          # the frozen scenarios
    python3 eval/simulate.py                         # 180-day drift

With a model at `/tmp/models/Qwen3.5-4B-Q4_K_M.gguf`:

    python3 eval/mandatory_conversations.py --persona v3 --out eval/transcripts/run
    python3 eval/defence_probes.py                   # attack the defences
    python3 eval/cross_session_probe.py              # memory, real model
    python3 eval/planner_reliability.py              # does the gateway get reached?

`eval/mutation_audit.py` refuses to start on a working tree with
uncommitted changes under `pai/`, because it rewrites those files and a
crash mid-mutation would otherwise leave a defence silently disabled.

## Documents

| file | what it is |
|---|---|
| `docs/FINAL-REPORT-R3.md` | the report |
| `docs/CONVERSATION-FAILURES.md` | all 39 failures, each quoted from the transcript that produced it |
| `docs/conversational-llm-architecture.md` | the original R&D answer |
| `docs/personal-ai-architecture.md` | the system design |
| `eval/transcripts/` | every conversation, verbatim |

## The one-paragraph version

Almost nothing that was wrong with this system was wrong with the model.
Of 39 documented failures, 34 were fixed in deterministic code outside the
weights. Three defences — the permission gateway, the web path, and the
voice confirmation rule — were fully implemented, unit-tested, green, and
**never once reached at runtime**; the only thing that found them was
running twenty real conversations and reading what came back.
