# Evidence — raw output, not summaries

Every file here is the unedited stdout of a command, with a header saying
which command produced it and when. Nothing in this directory is
hand-written.

| File | Command | Result |
|---|---|---|
| `01-unit-tests.txt` | `python3 -m unittest discover -s tests -t .` | **386 tests, OK, 3 skipped** |
| `02-scenario-harness.txt` | `python3 eval/harness.py` | **183 / 183 checks, 100%** |
| `03-extractor-sweep.txt` | `python3 eval/extractor_sweep.py` | **373 turns, 4 facts, 0 retractions** |
| `04-transcript-tally.txt` | `python3 eval/tally.py` | **110 transcripts, 373 user turns** |
| `05-mutation-audit-88.txt` | `python3 eval/mutation_audit.py` | 88 applied, 88 killed, 0 survived (before the local battery) |
| `06-mutation-audit-94.txt` | `python3 eval/mutation_audit.py` | **94 applied, 94 killed, 0 survived** (current) |

All five were produced against the committed tree.

## How to read the mutation audit

It disables one defence at a time and requires that **at least one test
fails**. A line reading `SURVIVED` means either a defence no test depends
on, or an anchor that drifted so the experiment never ran. Both are
defects. The audit prints which.

`KILLED` lines name the test that caught it, so you can see *which* test
depends on *which* defence — the thing a green test suite cannot tell you.

## The three skipped tests

Opt-in live-network tests. They are skipped by default so the suite runs
offline in ~10 seconds. They are not failures.

## What is NOT in this directory

- **No GPU measurements.** Everything ran on CPU. The RTX 4050 numbers in
  the reports are RESEARCHED projections.
- **No ASR/WER measurements.** `eval/asr_test.py` was never run.
- **No audio anything.** There is no audio device in this environment.

The 180-day drift result in the reports is **SIMULATED**, not measured, and
is labelled that way at every mention.
