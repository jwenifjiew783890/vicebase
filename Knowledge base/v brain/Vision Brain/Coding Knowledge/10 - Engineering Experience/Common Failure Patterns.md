---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Common Failure Patterns

Shapes that recur across languages, stacks and decades. Recognising the shape is most of the diagnosis.

## Amplification

A small problem becomes a large one because the system multiplies it.

- **Retry storm** - each layer retries, so three layers of three attempts is 27 calls to a
  struggling dependency.
- **Thundering herd** - many clients act simultaneously after a cache expiry, a deploy, or a
  reconnect.
- **Fan-out tail** - with 100 parallel calls, the dependency's p99 becomes the caller's typical
  case.
- **Feedback loop** - a health check fails under load, an instance is removed, the remaining
  instances take more load and fail too.

The defence is always the same: backoff, jitter, caps, circuit breakers, and load shedding.

## Silence

The failure that reports success. The most expensive class, because nothing prompts anyone to
look.

- Swallowed exception, ignored return code, unhandled promise
- Empty result treated as an empty answer rather than a retrieval failure
- A pipeline stage producing nothing, causing downstream stages to be skipped while every step
  reports success
- A success test that is wrong - `error === undefined` when success returns `error: null`
- A test matcher that matches zero tests, so the pipeline is green and empty

**Defence: assert on the outcome, not on the absence of an exception.** Check the artefact
exists, the count is non-zero, the content is non-empty.

## Unbounded growth

Fine for a week, an incident at month three. Cache with no eviction, list that only appends,
log with no rotation, table with no retention, queue with no limit, retry with no cap.

**Defence: every collection has a bound and a removal policy, decided when it is created.**

## The unknown outcome

A timeout is not a failure - it is *unknown*. Designs treating it as failure produce duplicate
charges, duplicate messages and stuck workflows.

**Defence: idempotency keys, natural keys, conditional writes.**

## Boundary confusion

Two components disagreeing about a boundary's meaning.

- Off-by-one: empty, one, exactly at the limit, one past
- Timezone at a storage or display boundary
- Encoding at an I/O boundary
- Absent versus empty versus null versus zero
- Inclusive versus exclusive ranges
- `$json` meaning "the previous node's output" where "the workflow input" was intended

**Defence: state the contract explicitly at every boundary, and test the boundary values.**

## Hidden coupling

Two things that appear independent and are not.

- A shared database table treated as a private one
- A shared cache with an unversioned key shape
- Implicit ordering between components
- A shared mutable global
- Two services deployed together "because they always are"

**Symptom: a change in one place breaks something apparently unrelated.**

## Resource exhaustion under partial failure

Everything is fine until one dependency is *slow* - not down. Threads, connections and memory
accumulate waiting for it, and the whole service dies from something that was still returning
200s.

**Defence: timeouts, bulkheads, circuit breakers. Slow is the case nobody tests, and it is worse
than down.**

## Time

Local time, DST, leap years, clock skew, monotonic versus wall clock, expiry, and "this will
surely finish quickly". Time-related failures are notable for arriving without any change.

**Defence: UTC internally, monotonic clocks for durations, and explicit alerts on every expiry.**

## The state that only exists once

A configuration made by hand, a certificate on one machine, a script on someone's laptop, a
database with no backup. Invisible until it is gone.

**Defence: if it is not in version control or reproducible from something that is, it does not
exist.**

---

## See also

- [[Coding Knowledge/05 - Failure Patterns|Failure Patterns]]
- [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- Practitioner judgement, corroborated by the public postmortems cited in [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]. The silent-failure examples were measured in this project.
