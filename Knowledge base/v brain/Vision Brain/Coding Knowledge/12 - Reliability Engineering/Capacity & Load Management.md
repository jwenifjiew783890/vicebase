---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Capacity & Load Management

What the system does when demand exceeds what it can serve - which is a design decision, or it will be an outage.

> [!info] Provenance
> Load shedding, graceful degradation, request criticality and the organic/inorganic growth
> distinction are **Google SRE** concepts, restated in our own words. Cascading-failure dynamics
> draw on both Google SRE and Nygard's *Release It!* — **both without reuse licences**, both
> restated. The decision table and the local application are **our synthesis**.

## The premise

Overload is not a hypothetical. Traffic is spiky, dependencies slow down, and capacity is finite.
The only question is whether the behaviour at the limit was **designed** or is **emergent** — and
emergent behaviour at the limit is reliably the worst possible: everything slows, queues grow,
memory fills, and the service fails completely rather than partially.

**A system that degrades gracefully under overload serves more users than one that tries to serve
everyone and collapses.**

## Shed load deliberately

When saturated, **reject work quickly and cheaply** rather than accepting work you cannot
finish. A fast 429 or 503 costs almost nothing and lets the client retry sensibly. An accepted
request that times out after 30 seconds consumed a connection, a thread and memory, and helped
nobody.

Practical form:

- Bound every queue. An unbounded queue converts a throughput problem into an out-of-memory
  crash, which is strictly worse.
- Reject at the edge, before expensive work begins.
- Return `Retry-After` so clients back off with information rather than guessing.
- Shed the **least important** work first, which requires knowing what that is.

## Criticality

Not all requests deserve equal treatment under pressure. Classifying them in advance is what
makes shedding possible:

| Class | Example | Under pressure |
| --- | --- | --- |
| **Critical** | Checkout, authentication, writes | Serve |
| **Important** | Search, browsing | Serve degraded |
| **Best effort** | Recommendations, analytics, prefetch | Shed first |

Without a classification, shedding is random, and random shedding drops critical requests at
exactly the moment they matter most.

## Graceful degradation

Decide in advance what a reduced service looks like, because it will not be invented well during
an incident:

- Serve stale cached data and say it is stale
- Return fewer results, or skip the expensive enrichment step
- Queue the action and confirm asynchronously
- Disable the expensive feature and say so plainly

Almost any of these beats a 500. **A degraded answer is a product decision**, so it should be
made with the product in mind rather than by whichever timeout fires first.

## Cascading failure

The dynamic that turns a partial problem into a total one:

1. One instance becomes slow or fails.
2. Its load is redistributed to the remaining instances.
3. They exceed their own capacity and slow down.
4. Health checks fail, instances are removed, load concentrates further.
5. Everything is down, including the parts that were healthy.

The defences are all about **breaking the feedback loop**: bounded queues, load shedding, circuit
breakers so callers stop adding load, bulkheads so one dependency cannot exhaust shared
resources, and — importantly — **liveness checks that do not depend on dependencies**, so a
downstream blip does not restart the entire fleet.

**Slow is worse than down.** A dependency returning errors quickly lets callers fail fast and
move on. One that responds in 30 seconds holds every caller's threads and takes them with it.
This is the case nobody load-tests, and it deserves an explicit test.

## Capacity planning

Two kinds of growth, and they need different handling:

- **Organic** — gradual, forecastable from trend. Handle with routine headroom.
- **Inorganic** — a launch, a campaign, a link from somewhere large, a batch job. Not
  forecastable from trend; it has to be **told to you in advance**, which is an organisational
  problem rather than a technical one.

Plan headroom for a realistic peak, not for the average — and remember that a marketing email
sent to everyone at once is a self-inflicted traffic spike that arrives with no warning to
engineering.

**Load test with realistic data.** Real data is skewed, and skew is what breaks caching,
sharding and query plans. A load test against uniform synthetic data mostly tests the load
generator.

## Applying it here *(our synthesis)*

This stack has one user and no traffic problem, so most of this is dormant. Two parts are live
and already earned their place:

**Bounding a slow dependency.** The NVIDIA endpoint returning 504s is precisely the "slow is
worse than down" case. Unbounded, one stalled call held a workflow for **302 seconds**;
bounded with `timeout: 60000` and `maxRetries: 1` it fails cleanly in ~61 seconds. That is load
management at a scale of one.

**Bounding retrieval.** The Knowledge Retriever caps at 6 notes and 6,000 characters, and returns
a sentinel rather than nothing. That is a bounded queue and a shed-load policy in miniature: the
context window is the finite resource, and exceeding it degrades every answer.

The general form to carry forward: **for every dependency, know what happens when it is slow,
not merely when it is absent.**

## Failure modes

- **Unbounded queues**, turning overload into a crash.
- **No criticality classification**, so shedding is random.
- **Retry storms** adding load to an already-overloaded dependency.
- **Liveness checks that depend on dependencies**, causing restart storms.
- **Testing only the "down" case**, never the "slow" case.
- **Load testing with uniform synthetic data.**
- **No degraded mode**, so the only options are "fine" and "500".

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Stability Antipatterns|Stability Antipatterns]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]
- [[Coding Knowledge/12 - Reliability Engineering/Error Budgets|Error Budgets]]

## Sources

- Load shedding, criticality, graceful degradation and the organic/inorganic growth distinction derived from Google, *Site Reliability Engineering* - <https://sre.google/books/> - **no reuse licence**. Cascading-failure and slow-versus-down dynamics also draw on Michael Nygard, *Release It!* (2nd ed., 2018) - **copyrighted, no reuse licence**. Both restated entirely in our own words; nothing reproduced. The decision table, the local application and the failure modes are our synthesis; the 302-second measurement is from this project.
