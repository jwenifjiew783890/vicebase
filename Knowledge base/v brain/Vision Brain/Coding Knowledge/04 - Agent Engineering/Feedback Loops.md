---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Feedback Loops

Acting on the result of acting. The mechanism that makes agents useful, and the one that makes them run away.

## The shape

```
act -> observe -> evaluate -> adjust -> act
```

The value is that the agent does not need to be right first time. The danger is that every loop
without a bound is a system that can consume unlimited time and money while appearing busy.

## The three kinds

**Verification loops** - act, check the result mechanically, retry if wrong. Highest value by
far, because the check is deterministic: compile the code, run the test, validate the schema,
re-query the record. Prefer these over anything model-judged.

**Critique loops** - a model reviews its own or another's output against criteria. Useful for
open-ended work. Genuinely improves quality for one or two rounds and then plateaus or
oscillates; self-critique is also biased toward its own prior output.

**Environmental loops** - act on the world, observe the change, continue. Necessary for real
tasks and the most dangerous, because the actions are irreversible.

## Bounding, which is not optional

Every loop needs **all** of these:

- **Maximum iterations** - a hard cap, typically 3-5 for critique, more for verification.
- **A wall-clock and cost budget** - iterations alone do not bound a loop whose steps grow.
- **A progress test** - if the last two iterations produced no measurable improvement, stop. A
  loop that is not converging will not converge with more turns.
- **A defined terminal state** - what "done" means, and what happens when the cap is reached
  without it. Returning the best attempt *with an honest note that it did not converge* is the
  correct behaviour; returning it silently as if complete is not.

## Making the feedback useful

The quality of a loop is the quality of its signal.

- **Specific beats general.** "Test `test_parse_empty` failed: expected `[]`, got `None` at
  line 42" is actionable; "the code has issues" is not.
- **Include the actual output**, not a description of it.
- **Say what changed** between iterations, so the agent does not repeat a failed approach.
- **Keep a record of what has already been tried and rejected** in the state - without it, loops
  oscillate between two wrong answers indefinitely.

## Human in the loop

Route to a human for: irreversible actions, anything outside the permitted scope, low
confidence, and repeated failure. Design the interruption to be cheap - a clear question with
the context needed to answer it, not a dump of the transcript.

A loop that never asks and a loop that asks constantly are both failures. The threshold should
be **consequence-based**: cheap and reversible, proceed; expensive or irreversible, ask.

## Failure modes

- **No iteration cap.** The unbounded invoice.
- **Feedback that does not discriminate.** A judge that says "looks good" to everything.
- **Oscillation** between two states because prior attempts are not remembered.
- **Optimising the metric, not the goal** - passing the test by special-casing it.
- **Loops on non-idempotent actions**, duplicating side effects with each pass.
- **Silently returning a non-converged result** as though it were finished.
- **Self-critique treated as verification.** A model agreeing with itself is not evidence.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Evaluation Loops|Evaluation Loops]]
- [[Coding Knowledge/04 - Agent Engineering/Failure Recovery|Failure Recovery]]
- [[Coding Knowledge/04 - Agent Engineering/Self-Improvement|Self-Improvement]]

## Sources

- Shinn et al., "Reflexion" (2023) - <https://arxiv.org/abs/2303.11366>; Madaan et al., "Self-Refine" (2023) - <https://arxiv.org/abs/2303.17651>. Bounding requirements are practitioner judgement.
