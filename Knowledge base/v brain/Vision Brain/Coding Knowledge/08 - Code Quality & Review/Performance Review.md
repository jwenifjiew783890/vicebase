---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# Performance Review

Spotting in review what will be slow later, without turning every review into a premature optimisation argument.

## What is worth raising in review

Only two things reliably are:

1. **Complexity that changes with scale** - the code is fine at today's volume and will not be.
2. **Unbounded anything** - a query, a loop, a buffer, a response.

Micro-optimisation belongs in a profiler session, not a review. Raising it in review costs
attention and usually buys nothing.

## The high-signal patterns

**A query inside a loop.** The N+1 pattern. Invisible at 10 items, fatal at 10,000. This is the
single most common performance defect worth catching in review.

**A network call inside a loop.** Same shape, worse constant.

**Loading a whole collection to use part of it.** `SELECT *` then filtering in application code;
reading a whole file to get the first line; fetching all rows to count them.

**An unbounded query.** No `LIMIT`, no pagination, on a table that grows.

**A missing index** on a new foreign key, or on a column the change introduces a filter for.

**A list membership test inside a loop** - accidental O(n^2). Use a set.

**String concatenation in a loop** - quadratic in many languages.

**A new synchronous call on the request path** - especially email, an external API, or image
processing. Should it be queued?

**A cache with no eviction or no TTL.**

**A blocking call inside async code**, which stalls the entire event loop.

**A transaction held across a network call**, which holds locks for the duration.

## The questions to ask

- **What is the expected size here?** Ten, ten thousand, or ten million? The author usually
  knows and has not written it down.
- **What happens at 100x?** If the answer is "it gets slow", that may be fine; if it is "it
  falls over", that is a finding.
- **Is this on the request path?** Latency budget matters there and often does not elsewhere.
- **Is there a bound?** Every collection, query, loop and buffer should have one.
- **What did you measure?** For a change *claiming* a performance improvement, the before/after
  numbers are the review.

## What not to raise

- Micro-optimisations with no measurement behind them.
- Readability sacrificed for unproven speed - that is a regression in the thing that matters
  more.
- Speculative scaling for volumes that are not plausible.
- Style preferences dressed as performance ("this loop should be a comprehension").

**The reviewer's job here is to catch the algorithmic and unbounded cases**, and to insist that
any claimed optimisation is backed by numbers. Everything else is the profiler's job.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Database Problems|Database Problems]]

## Sources

- Practitioner synthesis. Complexity and N+1 patterns are standard; the review-scope guidance is judgement.
