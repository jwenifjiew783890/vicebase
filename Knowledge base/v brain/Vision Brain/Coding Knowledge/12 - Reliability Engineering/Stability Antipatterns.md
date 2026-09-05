---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Stability Antipatterns

Structures that reliably produce outages. Recognising the shape is what lets you see the outage before it happens.

> [!info] Provenance
> The antipattern taxonomy below originates in **Michael Nygard, *Release It!*** — a copyrighted
> book with **no reuse licence**. The names are the standard technical vocabulary the industry
> uses; **every description here is our own prose**, and no text, list or figure from the book is
> reproduced. The diagnostic questions, the local examples and the mapping to fixes are **our
> synthesis**.

## Why a taxonomy helps

These are not bugs — each one is a *structure* that behaves correctly until load, latency or a
failure arrives, at which point it converts a local problem into a global one. Naming them makes
them visible during design and review, which is far cheaper than meeting them in production.

## The antipatterns

**Integration points.** Every call to another system is a place your system can be hurt: it can
fail, it can be slow, it can return something malformed, it can accept the connection and never
respond. This is the single largest source of instability in most systems, and the number of
integration points is a reasonable first estimate of how much can go wrong. *Fix*: timeouts,
circuit breakers, bounded retries, and a defined behaviour for each dependency being **slow** as
well as absent.

**Chain reactions.** Instances share a workload, so when one dies its share moves to the
survivors — which brings them closer to the same failure. A single fault propagates through a
homogeneous pool one instance at a time. *Fix*: bulkheads, capacity headroom, and removing the
common cause (usually a resource leak that every instance shares).

**Cascading failure.** A failure crosses a layer boundary: the failing dependency takes down its
callers, which take down theirs. *Fix*: circuit breakers, timeouts, and liveness checks that do
not depend on downstream health.

**Blocked threads.** The most common way a service dies without crashing. Every request thread
ends up waiting — on a lock, on a connection pool, on an unbounded remote call — and the process
is alive, healthy by any shallow check, and serving nobody. *Fix*: never block indefinitely, use
timeouts on every acquisition, and prefer higher-level concurrency primitives over hand-rolled
locking.

**Slow responses.** Worse than errors, because the caller keeps waiting and holding resources.
A dependency that fails fast lets you recover; one that takes thirty seconds takes your capacity
with it. *Fix*: fail fast yourself when you cannot meet your own latency budget, rather than
serving a response nobody is still waiting for.

**Unbounded result sets.** A query with no limit, written when the table had a hundred rows.
It works for a year and then returns a million rows and exhausts memory — usually on the day
someone's account grows. *Fix*: a limit on every query and every API response, enforced
server-side rather than requested politely by the client.

**Self-denial attacks.** The system, or its own organisation, generates a traffic spike: an email
to every user with a deep link, a cron job that starts every client at the same second, a cache
that expires everything simultaneously. *Fix*: jitter, staggering, and telling engineering before
marketing presses send.

**Scaling effects.** A relationship that works one-to-one breaks when one side grows. A shared
resource sized for a handful of clients, or an N-squared communication pattern, is fine in
staging and fatal at production scale. *Fix*: identify the relationships that scale
multiplicatively before they do.

**Unbalanced capacities.** One tier can generate far more load than the next can absorb. The
front end scales elastically; the database behind it does not. Under a spike, the elastic tier
faithfully forwards more traffic than the fixed tier can survive. *Fix*: back-pressure, bounded
concurrency toward the smaller tier, and load shedding at the boundary.

**Dogpile / thundering herd.** Many clients act at the same instant — after a deploy, a
restart, a synchronised cache expiry, or a reconnection storm. *Fix*: jittered timers, staggered
restarts, single-flight cache repopulation.

**Force multiplier.** Automation applies a mistake everywhere, immediately and correctly. The
tool is working exactly as designed while it removes the fleet. *Fix*: bound how much any
automated action may affect at once, require confirmation past a threshold, and automate
diagnosis before remediation. *This is why the Cloudflare and AWS incidents in
[[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]
were global within seconds.*

## Diagnostic questions *(our synthesis)*

Use these in design and review — each maps to one antipattern above:

1. How many integration points does this add, and what does each do when it is **slow**?
2. If one instance dies, what happens to the others?
3. Can any thread here block without a timeout?
4. Is there a query or response that is unbounded?
5. Does anything here start at the same moment across many clients?
6. Which tier can generate more load than the next one can absorb?
7. If this automation is wrong, how much does it affect before anyone notices?

## Where the fixes live

The counter-patterns are documented elsewhere in this domain rather than duplicated here:

- Timeouts, circuit breakers, bulkheads, back-pressure —
  [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]] and
  [[Coding Knowledge/01 - Software Engineering/Design Patterns|Design Patterns]]
- Load shedding, criticality, degraded modes —
  [[Coding Knowledge/12 - Reliability Engineering/Capacity & Load Management|Capacity & Load Management]]
- The mechanism behind each fix —
  [[Coding Knowledge/10 - Engineering Experience/Proven Fixes|Proven Fixes]]

## Seen in this stack *(measured)*

- **Integration points and slow responses**: the NVIDIA endpoint returning 504s held one call for
  302 seconds. Bounded to 61 seconds by `timeout` and `maxRetries`.
- **Blocked threads, in miniature**: an unbounded Obsidian folder listing timed out and the
  agent halted silently with every step reporting success.
- **Force multiplier**: force-killing the Docker daemon during cleanup caused ~20 minutes of
  downtime — automation and blunt tooling amplifying a routine action.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Capacity & Load Management|Capacity & Load Management]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/10 - Engineering Experience/Common Failure Patterns|Common Failure Patterns]]
- [[Coding Knowledge/05 - Failure Patterns|Failure Patterns]]

## Sources

- Taxonomy and pattern names from Michael Nygard, *Release It!* (2nd ed., 2018) - **copyrighted, no reuse licence**. Descriptions are entirely our own prose; nothing from the book is reproduced. Cascading-failure dynamics also informed by Google, *Site Reliability Engineering* - <https://sre.google/books/> (**no reuse licence**, restated). Diagnostic questions and local examples are ours; the measurements are from this project.
