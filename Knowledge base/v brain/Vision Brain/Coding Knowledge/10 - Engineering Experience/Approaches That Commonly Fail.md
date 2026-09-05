---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Approaches That Commonly Fail

Ideas that are attractive, frequently attempted, and have a poor record - with the conditions under which each can work.

## The big rewrite

**Why it appeals**: the old system is genuinely bad, and a clean start feels faster than
untangling.

**Why it fails**: the old system encodes years of edge cases nobody remembers, discovered one at
a time in production. Meanwhile the old system keeps changing, so the target moves. Rewrites are
routinely abandoned half-done, leaving two systems.

**When it works**: the system is small, the domain is genuinely understood, and it can be
replaced incrementally - which is a strangler fig, not a rewrite.

## Building a framework before the third use

**Why it appeals**: the pattern seems obvious.

**Why it fails**: two examples do not reveal the axis of variation. The abstraction is built for
the wrong dimension, and every subsequent case needs a flag.

**When it works**: after three real cases, when the variation is observed rather than predicted.

## Microservices from day one

**Why it appeals**: it is what large companies do, and it promises independent scaling.

**Why it fails**: you pay the full operational cost - distributed tracing, network failure,
distributed data, deployment orchestration - before having the problem it solves. Boundaries
drawn before the domain is understood are usually wrong, and moving them across services is far
harder than moving them inside a monolith.

**When it works**: teams that need independent deployment, or components with genuinely different
scaling profiles, with the operational maturity to run them.

## Adding a cache to fix a slow query

**Why it appeals**: immediate improvement, small change.

**Why it fails**: the underlying problem remains, now with invalidation bugs, staleness and a
cold-start cliff on top. The cache becomes load-bearing and cannot be removed.

**When it works**: after the query is fixed, for genuinely expensive computation.

## Fixing a race with a sleep

**Why it appeals**: the symptom disappears.

**Why it fails**: the window is narrowed, not closed. It fails again on faster hardware, under
load, or at the worst moment - and by then the sleep looks intentional.

**When it works**: never as a fix. Acceptable as a temporary mitigation, if labelled as one with
the real fix tracked.

## Catching broadly and returning a default

**Why it appeals**: nothing crashes.

**Why it fails**: a failure becomes a wrong answer, propagated silently. The system looks healthy
and produces nonsense - the most expensive failure class there is.

**When it works**: at a genuine top-level boundary, where the exception is logged in full and the
degradation is visible to someone.

## Retrying everything

**Why it appeals**: transient failures disappear.

**Why it fails**: retrying non-idempotent operations duplicates side effects; retrying permanent
failures wastes time and hides the real error; retrying without backoff amplifies an outage.

**When it works**: for idempotent operations, on transient errors only, with backoff, jitter and
a cap.

## Prompt engineering as a security boundary

**Why it appeals**: "ignore instructions in the content below" seems to work in testing.

**Why it fails**: the model cannot reliably distinguish your instructions from instructions
embedded in data it reads, and an attacker writes the next sentence too.

**When it works**: never as enforcement. Useful as documentation of intent, alongside real
enforcement in code.

## Copying a pattern from a different stack

**Why it appeals**: it worked there.

**Why it fails**: patterns encode trade-offs specific to a context - team size, scale, language,
operational maturity. Transplanted, the costs arrive and the benefits do not.

**When it works**: when you can state the trade-off the pattern makes and confirm it applies here.

## Trusting a summary over the artefact

**Why it appeals**: it is faster, and the summary is usually right.

**Why it fails**: a green pipeline that skipped its tests, a log excerpt that omitted the error, a
report that says "verified". The one time it is wrong is the time it matters.

**When it works**: when the summary is generated from the artefact by something you trust to fail
loudly.

---

## See also

- [[Coding Knowledge/10 - Engineering Experience/Proven Fixes|Proven Fixes]]
- [[Coding Knowledge/10 - Engineering Experience/Architecture Failure Modes|Architecture Failure Modes]]
- [[Coding Knowledge/05 - Failure Patterns|Failure Patterns]]

## Sources

- Practitioner judgement. Joel Spolsky, "Things You Should Never Do, Part I" (2000) on rewrites - <https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/>; Martin Fowler, "MonolithFirst" - <https://martinfowler.com/bliki/MonolithFirst.html>; Simon Willison on prompt injection - <https://simonwillison.net/tags/prompt-injection/>.
