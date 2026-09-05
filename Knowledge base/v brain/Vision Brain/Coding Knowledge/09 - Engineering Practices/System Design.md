---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# System Design

Going from a requirement to a design that will still be workable after contact with reality.

## The sequence

**1. Numbers first.** Users, requests per second, data volume, growth rate, read/write ratio,
latency target, consistency requirement. Design decisions follow from these; without them you are
choosing by taste. An order-of-magnitude estimate is enough, and enormously better than none.

**2. The simplest thing that could work.** Write it down even if it is obviously insufficient. It
is the baseline every alternative must beat, and surprisingly often it turns out to be adequate.

**3. Find where it breaks.** At what volume does the simple design fail, and which part fails
first? That is where the design effort belongs, and nowhere else.

**4. Address only that.** One targeted change - an index, a queue, a cache, a shard - and
re-examine. Adding every scaling mechanism at once produces a system nobody can operate for load
that never arrives.

**5. Model the data before the components.** Component boundaries that ignore data ownership
re-couple through the database, and the shared table quietly undoes the separation.

**6. Define the failure model.** For each dependency: what happens when it is down, slow, or
wrong? What is the degraded behaviour? This is the part most often skipped and most often the
cause of the first outage.

**7. Define observability.** How will you know it is working? What signal shows the problem
first? Decide this now, not after the incident.

## Estimating, roughly

Useful magnitudes to reason with:

| Operation | Order |
| --- | --- |
| Memory access | ~100 ns |
| SSD random read | ~100 us |
| Same-datacentre round trip | ~0.5 ms |
| Simple indexed database query | ~1 ms |
| Cross-continent round trip | ~150 ms |

And: 1 million requests/day is ~12/second average, but peak may be 5-10x that. A byte per row
per user adds up faster than expected at scale. These are for sanity-checking a design, not for
capacity planning.

## Design for the change you expect

You will guess wrong about the future, so optimise for **reversibility** rather than for
prediction. Prefer a decision you can undo cheaply: an adapter over a hard dependency, a feature
flag over a rewrite, a migration that rolls back, a boundary that permits swapping the
implementation.

Spend the "hard to reverse" budget only where it buys something specific.

## Sanity checks before committing

- What is the single point of failure? (Name it; there is one.)
- What is unbounded? (Queue, cache, table, loop, result set.)
- What happens on a retry after an unknown outcome?
- What is the migration path for existing data?
- How is this rolled back?
- Who operates it, and what do they need at 3 a.m.?
- What is the simplest version, and why is it not enough?

## Failure modes

- **Designing for imagined scale**, paying the operational cost forever.
- **Skipping the numbers**, so every choice is aesthetic.
- **Component boundaries without data ownership.**
- **No failure model**, so behaviour under partial failure is emergent.
- **Novel technology** chosen without a stated reason.
- **A design with no rejected alternatives** - which means it was assumed, not designed.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Architecture Fundamentals|Architecture Fundamentals]]
- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]
- [[Coding Knowledge/08 - Code Quality & Review/Architecture Review|Architecture Review]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]

## Sources

- Practitioner synthesis. Latency magnitudes derive from Jeff Dean's widely-circulated "numbers everyone should know" and are given as orders of magnitude only. Martin Kleppmann, *Designing Data-Intensive Applications* (2017) - cited, not reproduced.
