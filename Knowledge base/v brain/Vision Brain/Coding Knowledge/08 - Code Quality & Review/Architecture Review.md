---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# Architecture Review

Reviewing the decisions that are expensive to reverse, before they are made.

## What to review, and when

Review a decision when it is **expensive to reverse**: component boundaries, data ownership,
storage engine, communication style, consistency model, trust boundaries, deployment topology.
Not framework choice, folder layout, or library selection - those are cheap and argued about
disproportionately.

Review **before implementation**, when changing the design costs a conversation. After
implementation it costs a rewrite, and the sunk cost will win the argument.

## The questions

**Problem**
- What problem does this solve, and how do we know it is real? Numbers, not anticipation.
- What happens if we do nothing?
- Is there an existing component that already does most of this?

**Alternatives**
- What else was considered, and why was each rejected? *A proposal with no rejected alternatives
  has not been designed - it has been assumed.*
- What is the simplest thing that could work, and why is it insufficient?

**Trade-offs**
- What does this optimise for, and what is being sacrificed? Every architecture sacrifices
  something; a proposal that claims otherwise has not identified it yet.
- Where does it get worse as scale grows?

**Failure**
- What happens when each dependency is down, slow, or returns garbage?
- What is the blast radius of a failure here?
- Is there a degraded mode, and is it defined?
- What is the single point of failure? (There is one.)

**Data**
- Who owns each piece of data? Two writers is not a boundary.
- What is the consistency model, and does the application handle it explicitly?
- What is the migration path for the existing data?
- Can this be rolled back after it holds production data?

**Operations**
- How is it deployed, and how is it rolled back?
- How do we know it is working? What signal, what alert?
- Who operates it, and what do they need to know at 3 a.m.?

**Reversibility** - the most important question in the list
- If this is wrong in six months, what does undoing it cost?
- Can it be adopted incrementally, behind a flag, for a slice of traffic?

## Signals a proposal needs more work

- No numbers - "it will be slow" without a measurement.
- No alternatives considered.
- Solving a problem that has not occurred.
- The failure model is unstated.
- The migration is described as "then we switch over".
- No rollback.
- Complexity justified by a future requirement nobody has committed to.
- A new technology with no stated reason beyond preference.

## The output

An [[Coding Knowledge/09 - Engineering Practices/ADRs|ADR]]: the context, the decision, the
alternatives rejected and why, and the consequences accepted. The rejected alternatives are the
most valuable part - they are what stops the same debate recurring in a year, and what tells a
future reader whether the decision still holds.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Architecture Fundamentals|Architecture Fundamentals]]
- [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]]
- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]
- [[Coding Knowledge/10 - Engineering Experience/Architecture Failure Modes|Architecture Failure Modes]]

## Sources

- Practitioner synthesis. Michael Nygard on ADRs - <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>.
