# FINAL HANDOFF — Personal AI (local conversational LLM runtime)

**Repository:** `jwenifjiew783890/vicebase`
**Branch:** `claude/conversational-llm-architecture-a13xti`
**Project root:** `personal-ai/`
**Handoff assembled:** 2026-09-06

This folder is self-contained. You do not need the development chat session
to understand the project. Everything cited here is either in this folder or
at a path named explicitly.

---

## 0. How to read the evidence in this handoff

Every claim in every report carries one of four labels. They are not
decoration — the distinction is the point of the whole project.

| Label | Means |
|---|---|
| **MEASURED** | It ran here and produced this output. Raw output is in `evidence/`. |
| **RESEARCHED** | A published figure about someone else's hardware or speech. Not verified here. |
| **SIMULATED** | Produced by a simulation, not by the real system under real load. |
| **NOT ACTUALLY TESTED** | Stated so it is not mistaken for a result. |

**The single most important thing to know before trusting anything here:**
an earlier version of this project marked three requirements as passing on
the strength of green unit tests. All three components were **unreachable at
runtime** — the tests passed while the code never ran in a real
conversation. See `reports/07-SUPERSEDED-final-verification.md` and §3 of the
main report. Everything about how this project tests itself is a reaction to
that discovery.

---

## 1. What was built

A **personal AI runtime** for a single user, running a small local LLM,
targeting an RTX 4050 Laptop (6 GB VRAM), 16 GB RAM, Core i7. English,
Hindi and Hinglish, with Hindi as natural spoken Hindi rather than textbook
Hindi.

**Model:** Qwen3.5-4B-Q4_K_M (Apache-2.0), run under llama.cpp. Not
fine-tuned. §4 of the main report explains the choice and documents a
reversal (Gemma → Qwen) with its reason.

### The architectural claim, stated plainly

The original brief asked whether this is "a small conversational LLM" or "a
personal AI system built around a small conversational LLM". **Both
framings were rejected.** The accurate description, and the one the
codebase implements:

> A **deterministic personal-agent runtime**, in which a small LLM is the
> language interface and personality layer — and is the component trusted
> **least** with decisions.

Routing, permissions, memory writes and action validation are ordinary
code. The model understands and speaks. It does not decide. This is not a
hedge; it is the difference between a system that works at 4B and one that
needs 70B.

### The central engineering finding

**Categorical instructions work at 4B; calibrated ones do not.** Refined in
round 3: categorical prohibitions hold for *content* (don't invent, don't
fabricate a citation, don't use the third person) but **not for form**
(don't end with a question). A form instruction regresses to the model's
habits exactly the way a calibrated one does. §5 and §22.

---

## 2. Current architecture

```
user turn
   │
   ├─ router.py ........ deterministic. Casual? world question? memory
   │                     question? action? retraction? vault command?
   │                     language command? Model is not consulted.
   │
   ├─ retrieval ........ obsidian.py (BM25 + dense, RRF fusion, threshold
   │                     gated) │ web.py (9.0s total budget, all Tainted)
   │                     │ memory.py (four tiers)
   │
   ├─ orchestrator.py .. assembles the prompt, calls the model, then applies
   │                     four honesty guards in a fixed order:
   │                       1. capability denial
   │                       2. memory claim
   │                       3. source claim
   │                       4. claimed-but-unrun action  (after the planner)
   │
   ├─ gateway.py ....... any action crosses here or does not happen.
   │                     READ / WRITE / IRREVERSIBLE / DESTRUCTIVE
   │                     → ALLOW / CONFIRM / CONFIRM_TYPED / DENY
   │                     Voice escalates irreversible actions to typed.
   │
   └─ learning.py ...... evidence accumulation → rule promotion
       extract.py ...... first-person facts → bitemporal memory
```

**Memory is four tiers:** T0 working, T1 episodic, T2 semantic (bitemporal),
T3 procedural (capped at 40 rules). Facts are **superseded, never
overwritten** — `valid_from` / `valid_to` / `superseded_by`. Retiring a fact
is not deleting it; history stays queryable.

**Security is by type, not by prompt.** `trust.py` is 72 lines and holds the
model: retrieved content cannot write memory and cannot emit an action.
A `Tainted` string subclass tracks provenance through the system.

Full module-by-module detail: `code/CODE-MAP.md`.

---

## 3. What is actually working

MEASURED, with transcripts and raw output committed.

- **Conversation in English, Hindi and Hinglish.** 110 transcripts, zero
  assistant tells. Hindi is the strongest result in the project and required
  no fine-tuning. Hinglish mirrors the user's mix including the switch point
  mid-sentence.
- **Four honesty guards.** The system says it does not know, refuses to
  describe sources it does not have, and does not claim actions it did not
  run. Each guard exists because a real transcript showed the failure it
  prevents.
- **Bitemporal memory with supersession**, and since round 4 it learns facts
  **from conversation** rather than from an API call.
- **Cross-session memory**, verified with the real model — including the
  hard case: recalling two facts correctly and then honestly saying "no
  idea" to a third that was never stored, under exactly the recall pressure
  that produces confabulation.
- **Obsidian retrieval**, both directions: retrieves when the vault has the
  answer, says there is nothing when it does not.
- **Web fallback** — which was **not** working before round 3.
- **Tool/agent orchestration** — also **not** working before round 3
  (0 of 12 actions reached the gateway; now 11 of 12).
- **The capability gateway**, including `git.push` by voice → CONFIRM_TYPED,
  measured live.
- **Injection resistance**: DENY on every payload in the corpus, through
  three capabilities.
- **Anti-sycophancy**: held its position twice under direct contradiction,
  with vault evidence. Disagrees without being rude.

## 3b. What is NOT working, or not established

- **No GPU was ever used.** Every RTX 4050 latency number is RESEARCHED.
  On CPU it runs at 5.5–6.4 tok/s with 11–20 s TTFT, which nobody would
  use. What *is* established is that nothing outside the model is slow
  (routing, retrieval and gating are sub-20 ms combined).
- **No audio model was ever tested.** Voice *policy* is fully tested;
  Whisper/Parakeet WER, TTS naturalness and end-to-end voice latency are
  not. Code-switched Hindi-English ASR runs ~42% WER for monolingual models
  (RESEARCHED) and is the single biggest open risk in the design.
- **OpenCode is not installed.** The client is tested against a real local
  HTTP server, never against OpenCode itself.
- **The 180-day drift result is SIMULATED**, not measured.
- **The model is still a 4B model** and gets things wrong that no
  architecture fixes. The reports quote its failures rather than hiding
  them.

---

## 4. What was actually tested, and the results

All five figures below are MEASURED against the committed tree. Raw output
is in `evidence/`.

| What | Result | Raw output |
|---|---|---|
| Unit tests | **374 passed**, 3 skipped (opt-in live network) | `evidence/01-unit-tests.txt` |
| Frozen scenario checks | **183 / 183**, 100% | `evidence/02-scenario-harness.txt` |
| Mutation audit | **88 applied, 88 killed, 0 survived** | `evidence/05-mutation-audit-88.txt` |
| Extractor over every real turn | **373 turns → 4 facts, 0 invented, 0 erased** | `evidence/03-extractor-sweep.txt` |
| Real conversations | **110 transcripts, 373 user turns** | `evidence/04-transcript-tally.txt` + `transcripts/` |
| Documented failures | **46 found, 46 fixed** | `reports/02-CONVERSATION-FAILURES.md` |
| Completion bar | **28 YES · 3 PARTIAL/UNVERIFIED · 0 NO** | `status/COMPLETION-BAR.md` |

The three non-YES items are **all hardware**: no OpenCode install, no audio
device, no GPU. None is a design question and none can be resolved by
further work in this environment.

### Why the mutation audit is the number that matters

A green test suite cannot tell you whether a test would fail if the code it
tests were removed. The audit disables one defence at a time and **requires
at least one test to fail**. It repeatedly caught tests that passed for the
wrong reason — including three occasions where two defences each satisfied
the other's only test, so disabling either changed nothing (F18, F40, F44).

The standard the project now holds itself to is stronger than "every
defence has a test":

> **Every defence has a test that fails when that defence alone is
> removed.**

### The most instructive single result

The extractor sweep reported **0 retractions** across 373 turns. Zero is the
shape a false green takes — a sweep reports zero when nothing retracts *and*
when the call is broken. Checking which one it was found F46: the phrase
*"I no longer work at night"* returned `works_at`, the user's **employer**,
because "work at night" is "work at Acme" with a time where the company
goes. Changing his hours would have silently retired where he works.

**No conversation in this project would ever have caught it.** All 373 real
turns contain no fact retraction, so the sweep's zero was true and
uninformative. The bug lived entirely in that gap and surfaced only from
asking what the measurement would look like if it were broken.

---

## 5. What remains

Full list with reasoning: `status/TODO.md`. In priority order:

1. **Widen the fact extractor** — it covers seven predicates and is a
   keyhole by design.
2. **Run it on the 4050** — turns the biggest RESEARCHED number into a
   MEASURED one. About a day of work.
3. **Code-switched ASR evaluation** — not a fix, a measurement.
   `eval/asr_test.py` exists and has never been run.
4. **A classifier for "is this a question about the world"** — three
   list-based gates caught the same failure three times; a small model earns
   its keep here first. A labelled corpus already exists in
   `eval/transcripts/`.
5. **Statistical language ID** to replace the wordlist (~90% today).
6. **Selective honesty guards** — replace the offending sentence, not the
   whole reply.

Deliberately **not** on the list: fine-tuning, a bigger model, more prompt
engineering. The measured evidence says none of the three fixes what is
actually broken.

---

## 6. Known limitations

Full text: `status/LIMITATIONS.md` (twelve limitations, plus what a 4B model
cannot do at all). The four that would matter most in daily use:

1. **Latency on this hardware is not the latency you would get, and the
   number you care about is unproven.**
2. **Voice is untested exactly where it is hardest** — code-switched ASR.
3. **Fact extraction covers seven predicates.** Anything else you say is
   not stored, and you are not told that it wasn't.
4. **The router decides "is this a question about the world" with a list,
   and lists have holes.** F2, F23 and F43 are one failure caught by three
   successive gates.

---

## 7. Important files and where they are

### In this handoff

```
FINAL_HANDOFF/
  INDEX.md                      you are here
  reports/     8 reports + README explaining the status of each
  evidence/    5 raw command outputs + README
  transcripts/ 110 transcripts + JSON results + README
  status/      COMPLETION-BAR.md · LIMITATIONS.md · TODO.md
  code/        CODE-MAP.md — every module, test file and eval script
  specs/       PRODUCTION-PROMPTS.md · DEVELOPMENT-BRIEFS.md
```

### In the repository

| Path | What |
|---|---|
| `personal-ai/pai/` | The runtime — 14 modules, 5,736 lines |
| `personal-ai/tests/` | 374 tests across 16 files |
| `personal-ai/eval/` | 21 harnesses and measurement scripts |
| `personal-ai/eval/transcripts/` | The original 110 transcripts |
| `personal-ai/eval/evidence/` | Committed raw audit output |
| `personal-ai/docs/` | The original reports (unmodified originals) |
| `docs/` (repo root) | The two architecture/R&D documents |

The repository root also contains an **unrelated Next.js application**
(`app/`, `components/`, `package.json`). This project does not touch it.

### To reproduce any number here

```bash
cd personal-ai
python3 -m unittest discover -s tests -t .   # 374 tests, ~10s
python3 eval/harness.py                      # 183/183 scenario checks
python3 eval/extractor_sweep.py              # 373 turns
python3 eval/tally.py                        # counts transcripts on disk
python3 eval/mutation_audit.py               # 88 mutations, ~15 min
```

The mutation audit refuses to start on a dirty tree and leaves a
`.mutation-in-flight` breadcrumb naming the file it is currently rewriting.
Both safeguards exist because it corrupted the tree twice, by two different
doors (§13.3).

---

## 8. Chronological development phases

| Phase | What happened |
|---|---|
| **1. R&D evaluation** | 22 questions on feasibility. Rejected the core premise: you cannot trade knowledge away to buy conversational capacity. → `reports/03` |
| **2. Personal-AI design** | Four-tier memory, continuous learning, orchestration. Rejected both offered framings in favour of a deterministic runtime with the LLM trusted least. → `reports/04` |
| **3. Implementation** | The `pai/` runtime built against the 4050 target. Unit tests and the frozen scenario set. |
| **4. First "final" report** | → `reports/06`. Later superseded. |
| **5. Verification report** | → `reports/07`. Marked three requirements YES on green unit tests. **All three were false.** |
| **6. Round 1** | 11 real conversations. Found confabulation, emotional statements triggering web search, leaked reasoning traces, and that a longer persona is not a better one. |
| **7. Round 2** | The frozen twenty — 20 conversations, 69 turns, all 30 required probes embedded in realistic multi-turn conversation rather than asked as one-liners. The baseline. |
| **8. Round 3** | Same twenty, turn for turn, against fixed code, plus 8 new defence probes and a cross-session memory probe. **Discovered the three unreachable components.** |
| **9. Round 4** | Same twenty again. Found ten more defects (F29–F38), two of them self-inflicted. |
| **10. Round 4b** | Re-verified the fixes round 4 itself produced. Found nothing new. |
| **11. Mutation audit** | 86 → 88 mutations. Caught defence masking three times. Final result 88/88 in one pass. |
| **12. F46 + handoff** | The extractor sweep's "0 retractions" checked against itself, exposing a retraction that erased the wrong fact. Fixed, tested, mutated. This folder assembled. |

Round 4 was not the plan. Each round was run because the previous one's
evidence asked for it.

---

## 9. Every report included in this handoff

| File | Status | Lines | What it is |
|---|---|---:|---|
| `reports/01-FINAL-REPORT-R3.md` | **CURRENT — start here** | 2,108 | The authoritative report. 35 sections, §0–§34. |
| `reports/02-CONVERSATION-FAILURES.md` | **CURRENT** | 1,589 | All 46 failures (F1–F46 + G1), each quoted from a real transcript, with fix and regression test. |
| `reports/03-RD-EVALUATION-conversational-llm.md` | **CURRENT** | 680 | Brief 1. Feasibility, base model, datasets, STT/TTS, quantization. |
| `reports/04-DESIGN-personal-ai-architecture.md` | **CURRENT** | 519 | Brief 2. The architecture the codebase implements. |
| `reports/05-SUPERSEDED-conversation-quality.md` | SUPERSEDED | 569 | Round 1/2 quality analysis. Kept: its round-1 transcripts are the baseline. |
| `reports/06-SUPERSEDED-final-report-r1.md` | SUPERSEDED | 532 | The first "final" report. |
| `reports/07-SUPERSEDED-final-verification.md` | SUPERSEDED | 395 | **Kept deliberately** — three of its claims were later measured false. |
| `reports/08-project-README.md` | CURRENT | 68 | The runtime's own index. |
| `status/COMPLETION-BAR.md` | CURRENT | 152 | The 32-point bar, the 22 R&D questions, and the verdict. |
| `status/LIMITATIONS.md` | CURRENT | 126 | Twelve limitations + what 4B cannot do at all. |
| `status/TODO.md` | CURRENT | 51 | What remains, in priority order. |
| `code/CODE-MAP.md` | CURRENT | 121 | Every module, test file and eval script. |
| `specs/PRODUCTION-PROMPTS.md` | CURRENT | 162 | Every prompt the runtime sends, extracted from source. |
| `specs/DEVELOPMENT-BRIEFS.md` | CURRENT | 115 | The five briefs — **reconstruction, not transcript.** |
| `reports/README.md`, `evidence/README.md`, `transcripts/README.md` | CURRENT | — | Directory guides. |

---

## 10. What this handoff does not contain

Stated so nothing is inferred from silence:

- **No GPU measurements** — there was no GPU.
- **No ASR/WER measurements** — `eval/asr_test.py` was never run and there
  is no result file. Its docstring incorrectly said "MEASURED" until
  2026-09-06; that label is now corrected in the file itself.
- **No audio recordings or TTS output** — no audio device.
- **No OpenCode integration test** against real OpenCode.
- **No verbatim copy of the original chat instructions** — see the
  provenance warning at the top of `specs/DEVELOPMENT-BRIEFS.md`.
- **No model weights.** Qwen3.5-4B-Q4_K_M is ~2.6 GB and is not committed.

The reports also contain **negative results that were kept rather than
buried** — most notably §22, where a pre-generation instruction to stop
asking questions did nothing at all (question density 0.78 → 0.80, and
multi-question replies went *up*, 9 → 12). Only a post-hoc edit moved the
number. That is a documented failure of the approach, not a success.

---

## 11. Coverage map — the 23 requested categories

Each row names where that category actually lives. Where something was not
produced, the row says so rather than pointing at a substitute.

| # | Requested | Where it is |
|---|---|---|
| 1 | Final implementation report | `reports/01-FINAL-REPORT-R3.md` |
| 2 | All progress/status reports | `reports/05`, `06`, `07` (superseded, kept) + `status/` |
| 3 | Architecture / design decisions | `reports/03`, `reports/04`, §2 above, `code/CODE-MAP.md` |
| 4 | Testing reports and results | `evidence/01`, `02`, `05`; report §13 (methodology) |
| 5 | Conversation-quality testing | `reports/05`; report §14, §21, §31 |
| 6 | Actual transcripts | `transcripts/` — 110 files, 373 user turns |
| 7 | English / Hindi / Hinglish testing | Report §28; `transcripts/final2-4/`; `tests/test_language_and_memory.py` |
| 8 | Memory / personalization testing | Report §7, §12, §23; `evidence/03`; `tests/test_memory_learning.py`, `test_memory_sessions.py`, `test_extraction.py` |
| 9 | Anti-sycophancy testing | Report §15 row, completion bar rows 15–16; `tests/test_sycophancy_pressure.py`; transcript A05 |
| 10 | Security / injection testing | Report §9; `tests/test_gateway.py` (32 tests); `eval/data/injection_corpus.py` |
| 11 | Obsidian / retrieval testing | Report §25; `transcripts/defence*/V1.txt`, `V2.txt`; `tests/test_obsidian.py` |
| 12 | Router / orchestrator / gateway testing | `code/CODE-MAP.md`; `tests/test_honesty_and_retraction.py` (57), `test_gateway.py` (32), `test_adversarial.py` (29) |
| 13 | Voice / STT / TTS research + testing | Report §11 (policy MEASURED, models NOT TESTED); `reports/03` for the research; `tests/test_voice.py` |
| 14 | Hardware / VRAM / latency | Report §10 (latency), §30 (VRAM budget). **CPU measured, GPU RESEARCHED.** |
| 15 | Bugs discovered and how fixed | `reports/02-CONVERSATION-FAILURES.md` — all 46, each with transcript, fix and test |
| 16 | Regression tests | `personal-ai/tests/` — 374 tests; `evidence/01` |
| 17 | Adversarial tests | `eval/defence_probes.py`, `eval/mutation_audit.py` (88), `tests/test_adversarial.py`, `eval/extractor_sweep.py` |
| 18 | Failed tests and their resolutions | `reports/02`; `reports/07` (three claims later falsified); report §3 |
| 19 | Known limitations | `status/LIMITATIONS.md` |
| 20 | Remaining TODOs | `status/TODO.md` |
| 21 | Acceptance criteria + pass/fail | `status/COMPLETION-BAR.md` — 28 YES · 3 PARTIAL · 0 NO |
| 22 | Prompts / specifications / instructions | `specs/PRODUCTION-PROMPTS.md` (extracted from source), `specs/DEVELOPMENT-BRIEFS.md` (**reconstruction**) |
| 23 | Anything else needed to understand it | `code/CODE-MAP.md`, the four directory READMEs, §8 above (chronology) |

### Two rows worth reading twice

**Row 13 and row 14 are the honest weak points.** Voice policy is fully
tested and every audio *model* is untested. Latency is measured on CPU and
projected on GPU. Neither gap is closable in this environment, and both are
labelled at every mention rather than smoothed over.
