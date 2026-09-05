---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Planners

Turning a request into an ordered set of steps, and knowing when planning is worth its cost.

## When a planner is warranted

Only when the steps genuinely depend on the request. If the same three things always happen in
the same order, that is a **pipeline**, and writing it as code is faster, cheaper, testable and
debuggable. A planner that reliably produces the same plan is pure overhead with an outage
attached.

## Planning styles

| Style | How | Best for |
| --- | --- | --- |
| **Plan-then-execute** | Full plan first, then deterministic execution | Predictable cost, auditable, easy to debug |
| **Interleaved (ReAct)** | Think, act, observe, repeat | Genuinely unknown environments |
| **Hierarchical** | High-level plan, sub-plans per step | Complex tasks with natural decomposition |
| **Reactive** | No plan; respond to the current state | Simple, well-bounded tasks |

**Plan-then-execute is the right default.** The plan is inspectable before anything happens, the
cost is bounded up front, failures are attributable to a step, and the whole run can be replayed.
Interleaved planning is more capable and much harder to reason about; use it when the
environment genuinely cannot be predicted.

*This stack uses plan-then-execute for its n8n agents. It was adopted because the provider
rejected the tool-loop message shape, and kept because the determinism proved more valuable
than the flexibility.*

## What makes a plan usable

- **Steps are concrete and executable.** "Set up the database schema" is a step; "handle data"
  is not.
- **Each step names its inputs and its expected output.** Otherwise nothing can chain.
- **Dependencies are explicit**, so the executor knows what is sequential and what is parallel.
- **The plan is validated before execution** - do the named capabilities exist, are the required
  arguments present, is the step count within budget? A plan referencing a non-existent tool
  should fail at validation, not halfway through.
- **The plan is bounded.** A maximum number of steps, and a cost/time budget.

## Chaining between steps

The most common structural bug: **step 2 does not receive step 1's output.** The plan looks
right, every step reports success, and the final result is a placeholder built from nothing.

Make chaining structural rather than the planner's responsibility - the executor should supply
the previous step's output automatically, and a step should be able to say what it needs by
name. Relying on the planner to remember to pass data is relying on a probabilistic component
for a mechanical job.

> [!note] Measured in this project
> A planner that was supposed to reference earlier stage output produced empty context, so
> drafts were pure placeholders while every execution reported success. The fix was structural -
> the `Prepare Stage` step now supplies the previous output automatically rather than asking the
> planner to.

## Failure modes

- **Planning what does not need planning.** Overhead, latency, and a new failure mode for zero
  benefit.
- **Plans that reference non-existent capabilities.** Validate against the registry before
  running.
- **No replan on failure.** A rigid plan meeting a failed step either stops or continues into
  nonsense. Decide which, explicitly.
- **Unbounded step count**, so a confused planner runs until the budget or the patience is gone.
- **Plans that cannot be inspected.** If a human cannot read what is about to happen, nobody can
  approve it.
- **Losing the original goal** during long execution, after which the agent optimises the last
  step instead of the task.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Orchestrators|Orchestrators]]
- [[Coding Knowledge/04 - Agent Engineering/State Management|State Management]]
- [[Coding Knowledge/04 - Agent Engineering/Failure Recovery|Failure Recovery]]
- [[Coding Knowledge/03 - AI Engineering/Tool & Function Calling|Tool & Function Calling]]

## Sources

- Yao et al., "ReAct" (2022) - <https://arxiv.org/abs/2210.03629>. The chaining and determinism findings were measured in this project.
