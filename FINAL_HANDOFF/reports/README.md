# Reports — status of each

Files 01–04 are **current**. Files 05–07 are **superseded and deliberately
kept**: they contain claims that were later measured to be false, and
deleting them would hide the most instructive failure in the project.

| # | File | Status | What it is |
|---|---|---|---|
| 01 | `01-FINAL-REPORT-R3.md` | **CURRENT — start here** | The authoritative report. 2,108 lines, 35 sections (§0–§34). |
| 02 | `02-CONVERSATION-FAILURES.md` | **CURRENT** | All 46 documented failures (F1–F46, plus G1), each quoted from a real transcript, with the fix and its regression test. |
| 03 | `03-RD-EVALUATION-conversational-llm.md` | **CURRENT** | Brief 1: the R&D feasibility evaluation, 22 questions. Base model selection, dataset strategy, STT/TTS, quantization. |
| 04 | `04-DESIGN-personal-ai-architecture.md` | **CURRENT** | Brief 2: the personal-AI architecture. Contains the reframing that the whole codebase implements. |
| 05 | `05-SUPERSEDED-conversation-quality.md` | SUPERSEDED | Round 1/2 quality analysis. Kept because its round-1 transcripts are the baseline everything later is compared against. |
| 06 | `06-SUPERSEDED-final-report-r1.md` | SUPERSEDED | The first "final" report. Superseded by 01, which corrects three of its claims. |
| 07 | `07-SUPERSEDED-final-verification.md` | SUPERSEDED | **The important one to understand.** Marked three requirements YES on the strength of passing unit tests. All three components were unreachable at runtime. |
| 08 | `08-project-README.md` | CURRENT | The runtime's own README / index. |

## Why 07 is kept

It claimed:

- item 8, "Tool/agent orchestration — YES"
- item 18, "No hallucination when retrieval fails — YES"
- item 23, "Dangerous voice actions confirmed — YES"

All three were false. The unit tests passed and the components were never
reached by a real conversation: the planner parser rejected the model's
actual output format (0 of 12 actions reached the gateway), the web path
dispatched nothing (so the model fabricated and cited the internet), and
the voice/irreversible scenario tested nothing at all.

§3 of report 01 documents what was actually happening and what fixed it.
This is the project's central methodological lesson, and it is the reason
the mutation audit exists.

## Reading order for someone new

1. `01` §0–§2 — how to read the evidence labels, and the headline numbers
2. `01` §3 — the three false claims, and why they were false
3. `01` §5 — the central engineering finding about 4B models
4. `01` §15 — the twelve limitations
5. `01` §32 — the 32-point completion bar
6. `02` — the failures, when you want detail on any specific one
