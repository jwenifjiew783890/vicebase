---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# ADRs

Architecture Decision Records: writing down why, so the decision survives the person who made it.

## The problem they solve

Code shows *what* was done. It never shows what was considered and rejected, or which constraint
forced an odd choice. So a year later someone sees an unusual design, assumes it was a mistake,
"fixes" it, and rediscovers the original constraint the hard way.

An ADR is a short, immutable record of one decision and its reasoning.

## Format

Keep it to one page. Longer records do not get written, and do not get read.

```markdown
# ADR-0007: Use plan-then-execute instead of an agent tool loop

Date: 2026-09-03
Status: Accepted

## Context
The provider rejects LangChain's tool-result message shape with
"content.0 Input should be a valid dictionary or instance of Content".
Agent tool loops are also unbounded in cost and hard to audit.

## Decision
Capabilities produce a plan; the workflow executes the steps
deterministically; the model interprets the results.

## Alternatives considered
- Agent tool loop - rejected: incompatible with the provider, and
  unbounded cost.
- A different provider - rejected: this one is the approved endpoint.

## Consequences
+ Predictable cost, auditable, failures attributable to a step
+ Works with the provider as it is
- Less flexible on genuinely open-ended tasks
- Chaining between steps must be handled explicitly by the executor
```

## Rules

- **One decision per record.**
- **Numbered sequentially**, never renumbered.
- **Immutable.** A decision that is superseded gets a *new* ADR that references the old one, and
  the old one's status becomes `Superseded by ADR-0012`. Editing history destroys the value.
- **In the repository**, next to the code, so it is versioned with it and found by the people
  who need it.
- **Written when the decision is made**, not reconstructed later.

## What deserves one

Anything expensive to reverse or surprising to a newcomer:

- Choosing a database, a queue, a protocol, a framework
- A component boundary, or a decision not to split
- A consistency or failure model
- A security boundary
- A significant deviation from convention
- A deliberate limitation ("we do not support X, because...")
- **A rejected option that will look attractive again** - this is one of the most valuable kinds

Not: routine implementation choices, or anything trivially reversible.

## The most valuable sections

**Alternatives considered** and **Consequences (negative)**.

The first stops the same argument recurring, and tells a future reader whether the decision was
informed. The second is what makes an ADR honest - a record listing only benefits is marketing,
and it will be trusted less than it should be, or more.

## Failure modes

- **Written after the fact**, rationalising rather than recording.
- **Only the decision, no reasoning** - the useful half missing.
- **Edited when circumstances change**, destroying the record of what was believed at the time.
- **Too long**, so nobody writes the next one.
- **Stored away from the code**, so nobody finds them.
- **No negative consequences listed.**

---

## See also

- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]
- [[Coding Knowledge/08 - Code Quality & Review/Architecture Review|Architecture Review]]
- [[Coding Knowledge/01 - Software Engineering/Documentation|Documentation]]

## Sources

- Michael Nygard, "Documenting Architecture Decisions" (2011) - <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>. The worked example is a real decision from this project.
