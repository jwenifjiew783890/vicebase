---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Reliability

Designing for the fact that dependencies fail, networks partition, and machines restart mid-operation.

## The premise

Every remote call has four outcomes, not two: success, failure, **timeout with unknown state**,
and success-that-the-caller-never-learned-about. Designs that only handle the first two produce
duplicate charges, lost writes and stuck workflows.

## The mechanisms

**Timeouts, everywhere.** A call without a timeout inherits whatever the library defaults to,
often "forever". Set them from measured latency, not from optimism: `p99 x 2` is a reasonable
default. Bound the *total* attempt budget too, not just the per-attempt one.

**Retries, carefully.** Retry only idempotent operations, or non-idempotent ones protected by an
idempotency key. Always exponential backoff with jitter, always a cap, always a maximum
attempt count. Never retry a 4xx that means "your request is wrong".

**Circuit breaker.** After a threshold of failures, stop calling and fail immediately; probe
periodically. Protects both caller (threads not consumed waiting) and callee (not being pounded
while degraded).

**Bulkhead.** Separate pools per dependency, so a slow one cannot exhaust the resources needed
by the healthy ones.

**Graceful degradation.** Decide in advance what a reduced service looks like: stale cache,
fewer results, a queued action, a clear "this feature is temporarily unavailable". Almost always
better than a 500.

**Back-pressure and load shedding.** When saturated, reject fast and cheaply rather than
accepting work you cannot finish. Queueing everything turns a slowdown into a collapse.

**Health checks that mean something.** Separate **liveness** (should I be restarted?) from
**readiness** (should I receive traffic?). A health check that only returns 200 from the web
layer will happily report health while the database is unreachable.

**Graceful shutdown.** On SIGTERM: stop accepting new work, finish or safely abandon in-flight
work, flush, then exit. Without it, every deploy drops requests.

## Correctness under retry

- Make operations **idempotent** by design: natural keys, conditional writes, upserts, or an
  explicit idempotency key with a stored result.
- Beware the **dual write** - updating a database and publishing a message as two operations.
  One will fail eventually. Use the outbox pattern.
- **At-least-once delivery is the norm**; consumers must tolerate duplicates.

## Failure modes

- **Retry amplification.** Three layers each retrying three times is 27 calls to a struggling
  dependency.
- **The cascading timeout.** An inner timeout longer than the outer one means the caller gives
  up while the work continues, wasting the resource and confusing the state.
- **Fallback that hides the failure.** Silently serving stale or empty data with no signal;
  the system looks healthy while being wrong.
- **The retry that is not idempotent.** Duplicate side effects, discovered by users.
- **Health check that passes during a real outage.** Or one so deep that a transient blip
  restarts every instance at once.
- **Untested failure paths.** The recovery code that has never run is not known to work.
  Test it deliberately.

## Reliability targets

State the target as an objective with a measurement window (an SLO), and accept that 100% is
neither achievable nor worth its cost. The value of naming a target is that it makes the
trade-off explicit: an error budget converts "should we ship this risky change?" from an
argument into an arithmetic question.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Service Level Objectives|Service Level Objectives]]
- [[Coding Knowledge/12 - Reliability Engineering/Capacity & Load Management|Capacity & Load Management]]
- [[Coding Knowledge/01 - Software Engineering/Observability|Observability]]
- [[Coding Knowledge/01 - Software Engineering/Design Patterns|Design Patterns]]
- [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring|Monitoring]]

## Sources

- Michael Nygard, *Release It!* (2nd ed., 2018) - stability patterns; cited, not reproduced. Google, *Site Reliability Engineering* - <https://sre.google/books/> (readable online, cited only). AWS Builders' Library, "Timeouts, retries and backoff with jitter" - <https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/>.
