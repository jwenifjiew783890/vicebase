---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# State Management

What is carried between steps, and why a transcript is the wrong thing to carry.

## Transcript versus state

The naive design accumulates the conversation and passes it along. It grows without bound,
buries the important parts among the chatter, and eventually gets truncated - usually removing
the original goal, because that is the oldest thing in it.

The better design maintains an **explicit state object** and rebuilds the prompt from it:

```
goal                 the original request, verbatim, never dropped
constraints          what must hold
facts_established    what has been determined, with provenance
decisions_made       what was chosen and why
steps_completed      what ran, with outcomes
current_step         where we are
open_questions       what is unresolved
artifacts            files written, IDs created, external effects
```

The transcript becomes a log for humans; the state is what drives behaviour.

## Rules

**1. The goal is immutable and always present.** Every prompt includes it. This single rule
prevents the most damaging agent failure - confidently completing the wrong task after
truncation.

**2. Every fact carries provenance.** Where it came from, when, how confident. Without this,
model-invented facts and observed facts are indistinguishable, and a hallucination becomes
permanent state.

**3. State transitions are explicit.** An agent should be in a named state with defined
transitions, not in an emergent condition inferred from history. This makes "why did it do
that?" answerable.

**4. Side effects are recorded.** Files written, records created, messages sent. Needed for
resumption, for reporting, and for cleanup after a failure.

**5. State is serialisable and inspectable.** If a run cannot be paused, dumped, read by a human
and resumed, it cannot be debugged in production.

**6. Bound every collection in the state.** `facts_established` with no cap will consume the
context as surely as a transcript did.

## Passing state between steps

Do not rely on the model to carry values forward. Make it structural: the executor supplies the
previous step's output to the next step, by name.

> [!warning] Measured in this project
> In a multi-hop capability, `$json` at a prompt node is the **previous node's** output, not the
> workflow input. Knowledge read as `$json.knowledge` therefore rendered empty with no error
> anywhere - the retrieved standards silently vanished. Reading from the **named trigger**
> instead is correct in both single-hop and multi-hop shapes.
>
> The general lesson: **know what "the input" refers to at every point in a pipeline**, and
> prefer explicit named references over positional or implicit ones.

## Concurrency and durability

- If steps can run in parallel, decide what they may write. Two steps updating one field is a
  lost update.
- For long-running or resumable work, persist state after each step, keyed by a run ID.
- Make step execution **idempotent**, so a resumed run does not repeat side effects.

## Failure modes

- **Unbounded history** growing until truncation removes the goal.
- **Implicit state** inferred from the transcript - unreadable and unreproducible.
- **State the model can rewrite freely**, so a hallucination becomes a recorded fact.
- **No provenance**, making contradictions unresolvable.
- **Non-serialisable state**, so a run cannot be resumed or inspected.
- **Side effects not recorded**, so a retry duplicates them.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]
- [[Coding Knowledge/03 - AI Engineering/Agent Memory|Agent Memory]]
- [[Coding Knowledge/04 - Agent Engineering/Planners|Planners]]
- [[Coding Knowledge/04 - Agent Engineering/Failure Recovery|Failure Recovery]]

## Sources

- Practitioner synthesis. The `$json` scoping failure was measured in this project and is recorded in `D:\n8n\workflows\_generate.py`.
