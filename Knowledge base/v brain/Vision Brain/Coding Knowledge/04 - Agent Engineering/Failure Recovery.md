---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Failure Recovery

What the agent does when a step fails. The difference between a system and a demo.

## Classify the failure first

Different failures need opposite responses, and treating them uniformly is the core mistake.

| Class | Example | Response |
| --- | --- | --- |
| **Transient** | Timeout, 503, rate limit | Retry with backoff |
| **Permanent** | 400, file not found, invalid arguments | Do not retry; fix or report |
| **Permission** | Denied by policy | Stop. Report. Never work around it |
| **Ambiguity** | The request was under-specified | Ask, or state the assumption |
| **Capability** | The task needs something unavailable | Report honestly; do not simulate it |
| **Partial** | Three of five steps succeeded | Decide: continue, roll back, or report partial |

**Retrying a permanent failure** is the most common wasted-loop bug. **Working around a
permission failure** is the most dangerous response of all - if the agent is denied and finds
another route, the permission system has been defeated by the thing it was constraining.

## Partial failure is the hard case

Steps 1-3 succeeded and produced side effects; step 4 failed. Options:

- **Compensate** - undo the effects in reverse order. Requires each step to define an undo, and
  requires that undo to be possible.
- **Continue degraded** - complete what can be completed, report clearly what did not.
- **Stop and report** - safest and often correct.

Whatever the choice, **the side effects that already happened must be reported**. The worst
outcome is a failure report that omits the three files already written.

## Reporting honestly

This is the part most often done badly, and it matters more than the recovery itself.

- **Say what failed and at which step**, not "the task failed".
- **Say what was completed**, including side effects.
- **Say what was not attempted.**
- **Never present a partial result as complete.** A draft assembled from missing context is not
  a draft; it is a placeholder, and saying so is the whole value of the report.
- **Never claim verification that did not happen.** "I did not run the tests" is a useful fact;
  "tests pass" when they were not run is actively harmful, because it removes the reader's
  reason to check.

## Silent failure is the enemy

The worst failure mode is the one that reports success. It happens when:

- a stage produces nothing and the pipeline skips the rest while marking every step successful
- an error is caught and converted to a default value
- an empty result is treated as an empty answer rather than as a retrieval failure
- a success test is written wrongly - such as `error === undefined` when success returns
  `error: null`

*All four were observed in this project.* The defence is to **assert on the outcome, not on the
absence of an exception**: check that the expected artefact exists, that the count is non-zero,
that the content is non-empty. Then a silent failure becomes a loud one.

## Design rules

- **Bound every step** with a timeout and a retry cap.
- **Make steps idempotent**, so retry is safe.
- **Record side effects as they happen**, not at the end.
- **Fail closed on permissions**, always.
- **Escalate to a human** on repeated failure rather than looping.
- **Keep the failure in the state**, so a replan does not repeat the same approach.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Feedback Loops|Feedback Loops]]
- [[Coding Knowledge/04 - Agent Engineering/State Management|State Management]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/05 - Failure Patterns|Failure Patterns]]

## Sources

- Practitioner synthesis. All four silent-failure examples were measured in this project and are recorded in `D:\n8n\workflows\AGENT-REGISTRY.md`.
