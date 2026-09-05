---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Service Level Objectives

Turning "it should be reliable" into a number that can be measured, argued about, and designed against.

> [!info] Provenance
> The SLI/SLO/SLA distinction, the argument for choosing few indicators, and the
> user-perception framing are **Google SRE concepts, restated here in our own words**. The
> worked examples, the failure modes, and the "applying it here" section are **our synthesis**.

## The three terms, kept distinct

Conflating these is the most common mistake in the topic.

| Term | Is | Example |
| --- | --- | --- |
| **SLI** — indicator | A *measurement* of one aspect of service quality | Fraction of HTTP requests completing in under 300 ms |
| **SLO** — objective | A *target* for an SLI over a stated window | 99.5% of such requests, measured over 28 days |
| **SLA** — agreement | A *contract* with a consequence attached | Below 99% in a month, the customer is credited |

An SLI without an SLO is a dashboard nobody acts on. An SLO without an SLI is an aspiration. An
SLA should always be **looser** than the internal SLO, so the internal target is breached first
and there is time to react before anything contractual happens.

## Choosing indicators

The governing rule, from SRE practice: **measure what a user would notice.** CPU utilisation is
not an SLI, because a user has never noticed CPU. Latency of the operation they performed is.

Keep the set small. A handful of indicators that genuinely reflect the experience beats twenty
that dilute attention, because every indicator you commit to is one you must measure, alert on
and defend.

The usual families:

- **Availability** — the proportion of valid requests served successfully
- **Latency** — the proportion of requests served faster than a threshold
- **Quality / correctness** — the proportion of responses that were complete and correct
- **Freshness** — for data pipelines, the proportion of results newer than some age
- **Throughput / coverage** — the proportion of the intended work actually processed

## Expressing latency correctly

**Do not set an SLO on an average.** An average hides the tail entirely, and the tail is the
experience being complained about.

Two workable forms:

- A **threshold proportion**: "99% of requests complete within 300 ms". Preferred — it is a
  single number, it aggregates cleanly, and it maps directly onto a budget.
- A **percentile target**: "p99 latency under 300 ms". Readable, but percentiles do not average
  or aggregate correctly across windows and services, which causes real confusion later.

## Setting the target

- **Start from observed behaviour**, not from a round number. Measure current performance for a
  few weeks, then set a target slightly better than what users already tolerate.
- **99.9% is not automatically right.** Ask what the user would actually do differently at
  99.9% versus 99%. If nothing, the extra nine is being bought for no one.
- **Different paths deserve different targets.** Checkout and the marketing page are not the
  same service, and applying one target to both over-invests in one and under-invests in the
  other.
- **Use a rolling window** (commonly 28 or 30 days). A calendar month resets the budget on an
  arbitrary date and encourages end-of-month risk-taking.
- **Exclude what you do not control**, deliberately and in writing — otherwise the first
  upstream outage makes everyone stop trusting the number.

## Measuring honestly

- **Measure as close to the user as possible.** Server-side metrics miss DNS, TLS, the CDN and
  the client's own network — all real to the user.
- **Define "valid request".** Health checks, bots and requests rejected for bad input should
  usually be excluded; say so explicitly, or the number quietly drifts.
- **Count what happened, not what was sampled**, where the volume allows it.

## Applying it here *(our synthesis)*

A single-operator, single-machine stack does not need an SLA and does not need a formal review.
It does benefit from **one written sentence per service** stating what "working" means, because
that sentence is what an alert and a health check should encode.

For this stack that is roughly:

| Service | A usable statement of "working" |
| --- | --- |
| Vision (Open WebUI) | The UI loads and a chat request returns a first token within ~10 s |
| n8n | `/healthz` returns 200 and an agent capability completes without a model timeout |
| OpenCode | Returns 401 unauthenticated, and a scoped explain request returns text |
| Obsidian API | A folder listing returns within the retriever's 45 s timeout |

That last one is a real SLI here: the retriever's timeout **is** the objective, and exceeding it
once already caused a silent agent halt. See
[[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]].

## Failure modes

- **An SLO on a metric users cannot perceive** — CPU, memory, queue length.
- **An SLO on an average**, hiding the tail that generates complaints.
- **A target of 100%**, which makes the budget zero and every change unjustifiable.
- **An SLA tighter than the SLO**, so the contract breaks before the internal alarm.
- **Too many indicators**, none of which anyone defends.
- **Measured server-side only**, so the users' actual experience is invisible.
- **Never reviewed**, so the target describes a system that no longer exists.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Error Budgets|Error Budgets]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring|Monitoring]]
- [[Coding Knowledge/01 - Software Engineering/Observability|Observability]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- Concepts derived from Google, *Site Reliability Engineering* and *The Site Reliability Workbook* - <https://sre.google/books/> - which are readable online but grant **no reuse licence**. Restated entirely in our own words; no text, table or figure reproduced. Examples, the latency-form comparison, the failure modes and the "applying it here" table are our own synthesis.
