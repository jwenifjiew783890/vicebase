# Working in this repository

This is a **Python project**. It was previously a Next.js site; that
application has been removed. If you find instructions referring to Next.js,
React, npm or `node_modules`, they are stale — report them rather than
following them.

## What this is

A personal AI runtime built around a small local LLM (Qwen3.5-4B under
llama.cpp). The runtime lives in `personal-ai/`. See `README.md` for the
architecture and `FINAL_HANDOFF/INDEX.md` for the complete state.

## Rules that matter here

**1. Evidence labels are load-bearing.** Every claim in the docs carries
MEASURED, RESEARCHED, SIMULATED, or NOT ACTUALLY TESTED. Do not write
MEASURED unless you ran it and the output exists. A docstring that said
"MEASURED" on a harness that had never been run was the most misleading
line in this repository until it was corrected.

**2. A passing test is not evidence.** Every defence must have a test that
fails when *that defence alone* is removed. `eval/mutation_audit.py`
enforces this across 88 mutations. Three separate times, two defences each
satisfied the other's only test, so disabling either changed nothing — a
green suite cannot detect that.

**3. Do not edit source or commit while the mutation audit is running.** It
rewrites tracked files in place. It refuses to start on a dirty tree and
leaves a `.mutation-in-flight` breadcrumb naming the file it is currently
rewriting. Both safeguards exist because it corrupted the tree twice, by
two different doors.

**4. The LLM is trusted least.** Routing, permissions, memory writes and
action validation belong in deterministic code. If a fix can go in the
router, the gateway or the orchestrator rather than in a prompt, it goes
there — 41 of the 46 documented fixes did.

**5. Numbers drift.** Counts in prose go stale as the code moves. Verify
with `eval/tally.py`, the test runner, and the harness rather than trusting
a figure in a document — including a figure in this file.

## Before you change anything

```bash
cd personal-ai
python3 -m unittest discover -s tests -t .   # must stay green
python3 eval/harness.py                      # 183/183
```
