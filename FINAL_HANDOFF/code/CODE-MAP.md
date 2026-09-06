# Code map

Every file, what it does, and where the evidence for it lives. Line counts
and docstrings are extracted from the source, not transcribed.

All paths are relative to the repository root. The runtime lives in
`personal-ai/`. The repository previously also held an unrelated Next.js
site at the root (`app/`, `components/`, `data/`, `public/`, `types/` and
the Node toolchain); it was removed on 2026-09-06 and the repository is now
Python only. See `../../CLEANUP_REPORT.md`. Nothing in this project ever
depended on it.

---

## `personal-ai/pai/` — the runtime (14 modules, 5,736 lines)

The single most important thing to understand about this design:

> **The LLM is the component trusted least.** Routing, permissions, memory
> writes and action validation are ordinary deterministic code. The model
> understands and speaks; it does not decide.

| Module | Lines | Role |
|---|---:|---|
| `orchestrator.py` | 1188 | Turn lifecycle, persona assembly, the four honesty guards, retries |
| `router.py` | 671 | Every deterministic routing decision, before the model is called |
| `gateway.py` | 597 | Capability registry, permission tiers, taint tracking, execution |
| `memory.py` | 574 | Four-tier memory; bitemporal facts; rule cap; decay |
| `learning.py` | 463 | Evidence accumulation, rule promotion, `RULE_EFFECTS` |
| `obsidian.py` | 355 | Heading-aware chunking, BM25 + dense retrieval, RRF fusion |
| `signals.py` | 354 | Feedback detection (EN/HI/Hinglish), language identification |
| `llm.py` | 315 | llama.cpp adapters; planner output parsing |
| `latency.py` | 252 | Latency budget model for the voice pipeline |
| `web.py` | 245 | Web search with a hard total time budget; everything `Tainted` |
| `opencode.py` | 242 | Deterministic task briefs; refuses to guess missing fields |
| `voice.py` | 213 | Semantic endpointing, clause chunking for TTS, barge-in |
| `extract.py` | 195 | First-person fact extraction; retraction patterns |
| `trust.py` | 72 | Provenance levels; `may_write_memory` / `may_emit_action` |

### The parts worth reading first

**`trust.py`** is 72 lines and holds the whole security model. Content
carries a provenance level (RETRIEVED / AGENT / MODEL / USER / SYSTEM).
Retrieved content cannot write memory and cannot emit an action. That is
enforced by type, not by prompt.

**`router.py`** decides, before any model call: is this casual talk, a
question about the world, a memory question, an action request, a
retraction, an explicit vault command, a language command? Each decision is
a regex or a list, and §15.5 of the final report is honest that lists have
holes — three separate failures (F2, F23, F43) were the same failure caught
by three successive gates.

**`orchestrator.py`** runs one turn and applies four honesty guards in a
fixed order: capability denial, memory claim, source claim, then (after the
planner) claimed-but-unrun action. When a guard fires it replaces the whole
reply — a deliberate and sometimes wrong trade, documented as limitation 7.

**`gateway.py`** is where an action becomes real. Permission tiers
(READ / WRITE / IRREVERSIBLE / DESTRUCTIVE) map to verdicts
(ALLOW / CONFIRM / CONFIRM_TYPED / DENY). A request arriving by voice
escalates IRREVERSIBLE and DESTRUCTIVE to a **typed** confirmation.

---

## `personal-ai/tests/` — 374 tests, 3 skipped

The 3 skips are opt-in live-network tests. Everything else runs offline in
about 10 seconds.

| File | Tests | Covers |
|---|---:|---|
| `test_honesty_and_retraction.py` | 57 | The four honesty guards; retraction handling |
| `test_memory_learning.py` | 37 | Memory store and learning loop, adversarially |
| `test_gateway.py` | 32 | Capability gateway, hostile inputs |
| `test_language_and_memory.py` | 32 | Language commands, in-session style, memory questions |
| `test_adversarial.py` | 29 | Things that go wrong in the real world, not in the design |
| `test_extraction.py` | 24 | Fact extraction and retraction (includes F46) |
| `test_llm_adapters.py` | 24 | Adapter layer, no model needed |
| `test_question_restraint.py` | 24 | Consecutive-question restraint |
| `test_voice.py` | 22 | Endpointing, chunking, barge-in, voice confirmation rule |
| `test_obsidian.py` | 20 | Chunking and hybrid retrieval |
| `test_scenarios.py` | 18 | Runs the frozen scenario set inside the regression suite |
| `test_web.py` | 15 | Taint, latency bounds, honest emptiness |
| `test_opencode.py` | 14 | Tested against a **real local HTTP server** |
| `test_planner_parsing.py` | 13 | Built from **verbatim 4B output**, not invented JSON |
| `test_sycophancy_pressure.py` | 7 | Does the tripwire fire under realistic pressure |
| `test_memory_sessions.py` | 6 | Does last session's content reach this session's prompt |

---

## `personal-ai/eval/` — harnesses and measurement

| Script | Lines | What it does | Ran here? |
|---|---:|---|---|
| `mutation_audit.py` | 546 | 88 mutations; disables each defence and requires a test to fail | **YES — 88/88** |
| `harness.py` | 223 | The frozen scenario set | **YES — 183/183** |
| `convmetrics.py` | 193 | Automated conversational quality metrics |  YES |
| `conversation.py` | 187 | Transcript harness; drives the orchestrator against real weights | YES |
| `run_conversations.py` | 182 | Runs real conversations, records transcripts | YES |
| `simulate.py` | 175 | 180-day drift simulation | YES — **SIMULATED**, not measured |
| `mandatory_conversations.py` | 157 | The frozen twenty conversations | YES |
| `defence_probes.py` | 144 | Probes the new defences with the real model | YES |
| `learning_e2e.py` | 129 | End-to-end learning against the real model | YES |
| `ab_report.py` | 108 | Turns `ab.json` into the report's comparison | YES |
| `round_report.py` | 108 | Emits the round-2 vs round-3 comparison from data | YES |
| `asr_test.py` | 104 | Hindi ASR WER harness | **NO — never run, no result file** |
| `ab_persona.py` | 101 | A/B two personas on identical conversations | YES |
| `cross_session_probe.py` | 97 | Memory across sessions, real model | YES |
| `planner_reliability.py` | 81 | How often the 4B planner emits a valid action | YES |
| `demo.py` | 81 | End-to-end walkthrough with a stub model | YES |
| `recompute_metrics.py` | 80 | Recomputes stored runs under current metrics | YES |
| `tools_e2e.py` | 70 | Real-model tool and agent conversation | YES |
| `extractor_sweep.py` | 64 | The extractor over all 373 real turns | **YES — 373/4/0** |
| `tally.py` | 26 | Counts transcripts on disk rather than trusting a document | YES |
| `smoke_model.py` | 23 | Model loads, generates, and how fast | YES |

### A trap for the next reader

`eval/asr_test.py` **has never been run.** Its docstring said "MEASURED"
until 2026-09-06, which was wrong and is now corrected in the file itself.
There is no `eval/transcripts/asr_hi.json`. Every ASR/WER number in every
report is **RESEARCHED** — published figures about other people's speech.
This is the single biggest untested risk in the design.
