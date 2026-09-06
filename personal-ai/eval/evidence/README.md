# Raw output from the verification runs

The transcripts in `eval/transcripts/` are committed so that every claim
about the model can be checked against what it actually said. These are the
same idea for the runs that check the *tests* rather than the model.

- `mutation_audit_88.txt` — the full 88-mutation pass cited in
  §31c of `docs/FINAL-REPORT-R3.md`: 88 applied, 88 killed, 0 survived,
  baseline 0 failures. One uninterrupted run against the committed code.
  Reproduce with `python3 eval/mutation_audit.py` (~15 minutes; it refuses
  to start on a dirty tree, and leaves a `.mutation-in-flight` breadcrumb
  naming the file it is currently rewriting).

A line reading `SURVIVED` in any of these is a defence with no test that
depends on it, or an anchor that has drifted and could not run the
experiment. Both are defects. The audit prints which.
