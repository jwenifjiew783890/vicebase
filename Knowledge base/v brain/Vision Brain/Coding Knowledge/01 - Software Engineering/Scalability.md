---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Scalability

What breaks first as load grows, and which of the standard moves actually helps.

## Start by naming the axis

"Scalable" is meaningless without saying *along what*: requests per second, concurrent users,
data volume, write rate, fan-out, item size, or tenants. Systems that scale beautifully on one
axis fall over on another. Establish the current number and the target number before designing
anything - a system needing 10x is a tuning problem; 1000x is an architecture problem.

## The order things break

Roughly, and reliably enough to plan by:

1. **A single hot resource** - one database, one lock, one leader, one queue partition.
2. **Connection and thread pools** - exhausted long before CPU is.
3. **The N+1 pattern** - per-item queries or per-item network calls.
4. **Memory per request** - loading a whole result set to return ten rows.
5. **Serialisation and copying** - JSON encode/decode dominating at high rates.
6. **Coordination** - locks, distributed transactions, consensus round-trips.
7. **Tail latency** - the p99 that becomes the average once fan-out multiplies it.

## The moves, in order of cost

**Do less work.** Remove the query, cache the result, batch the calls, return fewer fields,
paginate. Almost always the biggest win per hour spent.

**Index correctly.** A missing index is the most common "scaling problem" and it is not one.

**Cache.** Effective and dangerous: now you have invalidation, staleness and a cold-start
cliff. See [[Coding Knowledge/05 - Web & Application Engineering/Caching|Caching]].

**Scale vertically.** Underrated. A bigger machine is cheap compared with distributing state,
and modern hardware is very large.

**Scale horizontally, stateless first.** Easy when instances share nothing; the difficulty is
always the state behind them.

**Shard.** Splits the hot resource, but the shard key is close to irreversible and cross-shard
queries and transactions become hard or impossible.

**Go asynchronous.** Move work off the request path into a queue. Converts a latency problem
into a throughput and back-pressure problem, which is usually the better problem.

**Read replicas / CQRS.** Separate read and write paths. Buys read scale, costs replication lag
that the application must now tolerate visibly.

## Amdahl and Little, briefly

- **Amdahl's law**: the serial fraction bounds your speedup. If 5% of the work cannot be
  parallelised, 20x is the ceiling no matter how many workers you add.
- **Little's law**: `concurrency = arrival rate x latency`. Halving latency halves the
  concurrency needed to serve the same rate - which is why latency work often *is* capacity work.

## Failure modes

- **Optimising the wrong layer.** Rewriting a service in a faster language while an unindexed
  query dominates.
- **Unbounded queues.** They convert overload into out-of-memory rather than into back-pressure.
  Bound the queue and shed load deliberately.
- **Retry storms.** Under load, retries add load. Backoff, jitter and circuit breakers are
  scalability mechanisms, not just reliability ones.
- **Cache stampede.** Expiry causes every request to miss at once and hit the origin
  simultaneously. Use jittered TTLs and single-flight.
- **Ignoring the tail.** With a fan-out of 100, the p99 of a dependency becomes the common case
  for the caller.
- **Premature distribution.** Distributed systems have a hard floor of operational cost. Pay it
  when the numbers demand it, not before.

## Benchmark honestly

Test with realistic data volumes and distributions - real data is skewed, and skew is what
breaks sharding and caching. Measure percentiles, never averages. Warm up before measuring, and
measure the whole path a user experiences, not one function.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Capacity & Load Management|Capacity & Load Management]]
- [[Coding Knowledge/01 - Software Engineering/Architecture Fundamentals|Architecture Fundamentals]]
- [[Coding Knowledge/05 - Web & Application Engineering/Caching|Caching]]
- [[Coding Knowledge/05 - Web & Application Engineering/Databases|Databases]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]]

## Sources

- Martin Kleppmann, *Designing Data-Intensive Applications* (2017) - cited, not reproduced. Dean & Barroso, "The Tail at Scale", CACM 2013 - <https://research.google/pubs/pub40801/>. AWS Builders' Library on load shedding and back-pressure - <https://aws.amazon.com/builders-library/>.
