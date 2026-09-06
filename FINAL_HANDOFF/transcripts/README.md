# Conversation transcripts — 110 files, 373 real user turns

**These are real model outputs.** Qwen3.5-4B-Q4_K_M (unsloth GGUF) running
under llama.cpp on CPU, driven through the full `pai/` runtime — memory,
router, gateway, retrieval, learning loop. Not a stub, not role-play, not a
simulation.

Verify the count yourself: `python3 eval/tally.py` counts files on disk
rather than trusting any document. Its output is committed at
`../evidence/04-transcript-tally.txt`.

## Directory map

| Directory | Files | What it is |
|---|---:|---|
| `v1/` | 3 | Round 1. Persona v1/v2 exploration. |
| `ab/` | 12 | A/B of two personas over identical conversations, plus `ab.json`. |
| `mandatory/` | 7 | Early runs of the mandatory conversation set. |
| `final/` | 4 | Round 2 partial. |
| `final2/` | 20 | **Round 2** — the frozen twenty, 69 turns. The baseline. |
| `final3/` | 20 | **Round 3** — the same twenty, turn for turn, against fixed code. |
| `final4/` | 20 | **Round 4** — the same twenty again. |
| `final4b/` | 2 | Round 4b — re-verifying the fixes round 4 itself produced. |
| `defence/` | 9 | Round-3 probes written specifically to attack the new defences. |
| `defence4/` | 9 | Round-4 defence probes. |
| `defence4b/` | 3 | Round-4b defence probes. |
| `langfix/` | 1 | An isolated language-handling fix. |
| `learning/` | — | `learning_e2e.json`, the end-to-end learning run. |
| `planner_reliability*.json` | — | The before/after measurement behind §3.1: 0/12 → 11/12. |

The mandatory twenty are **frozen** so rounds 2, 3 and 4 are directly
comparable turn for turn. The defence probes live in separate directories
precisely so they cannot contaminate that comparison.

## Reading a transcript

Each file carries the scenario, the turns, a bracketed run log, an explicit
failure criterion, and computed metrics. The run log matters as much as the
words:

```
AI:  [route=grounded lang=en vault=1 evidence=1 15w/1s ttft=16719ms 5.7tok/s]
```

Three of the worst findings in the project are **invisible in the reply
text alone** and only show up in that log — a reply can sound perfect while
`evidence=0` proves it was invented. That is why the log is preserved.

## Honest note on what these show

These transcripts contain the system's **failures as well as its
successes**, including replies that are wrong, near-nonsense, or
fabricated. They were not curated to look good. Several are cited in
`../reports/02-CONVERSATION-FAILURES.md` as evidence of defects.
