---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Error Budgets

The mechanism that converts "should we ship this risky change?" from an argument into arithmetic.

> [!info] Provenance
> The error-budget concept and its use as an arbitration mechanism between feature velocity and
> stability are **Google SRE**, restated in our own words. The arithmetic table, the
> anti-patterns, and the single-operator adaptation are **our synthesis**.

## The idea

If the objective is 99.9% over 28 days, then **0.1% of unreliability is permitted** — and
permitted means *allocated*, not merely tolerated. That remainder is the error budget.

The reframing this buys is the entire point: reliability stops being a virtue that one group
demands and another resists, and becomes a **shared quantity with a balance**. Shipping a risky
change spends budget. An outage spends budget. When the budget is healthy, ship. When it is
exhausted, stop shipping features and spend the effort on reliability until it recovers.

Nobody has to win an argument, because the number decides.

## What a budget actually buys

Over a 28-day window:

| Objective | Budget | Roughly |
| --- | --- | --- |
| 99% | 1% | ~6 h 43 m |
| 99.5% | 0.5% | ~3 h 22 m |
| 99.9% | 0.1% | ~40 m |
| 99.95% | 0.05% | ~20 m |
| 99.99% | 0.01% | ~4 m |

Two things become obvious from the table, and they are the reason to write it down:

1. **Each additional nine costs an order of magnitude** in engineering effort, and buys an order
   of magnitude less absolute time.
2. **At 99.99% you cannot deploy by hand.** Four minutes a month is less than one careful manual
   rollback. The target dictates the automation, not the other way round.

Budget is normally measured in **failed requests rather than wall-clock minutes**, since a
service degraded for 5% of users for an hour is not the same as a total outage for an hour.

## The policy is what makes it real

A budget with no consequence is a metric. The policy has to be agreed **before** it is spent,
or it will be renegotiated at exactly the moment it matters. A minimal version:

- Budget healthy → ship normally.
- Budget below ~25% → risky changes need an explicit decision; prefer canaries and flags.
- Budget exhausted → feature work pauses; reliability work only, until the rolling window
  recovers.
- Budget consistently untouched → the target is too loose, or you are over-investing in
  reliability and could ship faster.

That last line matters and is routinely forgotten: **a permanently full budget is a signal to
take more risk**, not a success.

## Burn rate

The useful alerting signal is not "budget remaining" but **how fast it is being consumed**.
Burning a month's budget in an hour needs a page; burning it evenly over the month needs
nothing.

Alert on **multiple windows at once** — a fast burn over a short window catches a sudden
outage, a slower burn over a long window catches a persistent degradation that would otherwise
never trip a threshold. Alerting on burn rate rather than on raw error rate is the single
largest reduction in alert noise available once SLOs exist.

## Applying it here *(our synthesis)*

A single-operator stack does not need a budget policy, a review meeting, or a feature freeze.
The **transferable part** is the underlying question, and it is worth asking explicitly before
any change to this stack:

> How much unreliability can this component have before it matters to me — and has it already
> had that much this week?

Two concrete consequences already visible in this project:

- The NVIDIA endpoint is a **free tier with no availability commitment**. Its budget is
  effectively unbounded and outside our control, which is precisely why every model node is
  bounded with `timeout: 60000` and `maxRetries: 1` — you cannot budget for a dependency, so
  you contain it instead.
- The Obsidian retriever's 45-second timeout is a de facto objective. It was exceeded once and
  silently halted an agent, which is a budget spent on something nobody chose to spend it on.

## Failure modes

- **A budget with no policy** — a number that changes nobody's behaviour.
- **The policy renegotiated when it first bites**, which teaches everyone it is decorative.
- **A 100% target**, giving a zero budget and making every change formally unjustifiable.
- **Budget measured in minutes** when partial degradation is the normal failure shape.
- **Alerting on the balance instead of the burn rate**, so you learn too late.
- **A permanently full budget** treated as success rather than as slack to spend.
- **Planned maintenance charged to the budget** without deciding in advance whether it should be.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Service Level Objectives|Service Level Objectives]]
- [[Coding Knowledge/12 - Reliability Engineering/Capacity & Load Management|Capacity & Load Management]]
- [[Coding Knowledge/09 - Engineering Practices/Release Strategy|Release Strategy]]

## Sources

- Concept derived from Google, *Site Reliability Engineering* and *The Site Reliability Workbook* - <https://sre.google/books/> - **no reuse licence**; restated in our own words, nothing reproduced. The budget table is arithmetic we computed, not a reproduced table. The policy sketch, the burn-rate guidance and the single-operator adaptation are ours.
