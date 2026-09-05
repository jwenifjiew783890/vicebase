---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Monitoring

Knowing something is wrong before a user tells you, without generating noise that trains everyone to ignore it.

## Alert on symptoms, not causes

"Checkout error rate above 2% for 5 minutes" is a symptom - it is definitionally bad. "CPU above
80%" is a cause, and it may be entirely fine.

Alerting on causes produces alerts that fire when nothing is wrong and stay silent when something
is. Alerting on symptoms means every page corresponds to a real problem.

## What to monitor

**The four golden signals**, per service:
- **Latency** - percentiles, and split successful from failed requests (a fast 500 flatters the
  average)
- **Traffic** - request rate
- **Errors** - rate and type
- **Saturation** - how close to a limit

**Resources**, by the USE method: utilisation, saturation, errors per resource.

**Business-level signals** are often the earliest and truest: orders per minute, jobs completed,
messages delivered. A drop in these catches failures that every technical metric misses.

**Queue depth and age** for anything asynchronous. Growing depth is the earliest warning of
trouble in the whole stack, and it is invisible from request metrics.

## Rules for alerts

1. **Every alert is actionable.** If the response is "watch it", it is not an alert.
2. **Every alert has a runbook** - what it means, how to confirm, what to do first.
3. **Alert on trends and sustained conditions**, not instantaneous spikes. Require a duration.
4. **Set thresholds from real data**, not from round numbers.
5. **Page rarely.** Everything else is a ticket or a dashboard.
6. **Review every alert that fires.** Was it real? Was the runbook right? Should the threshold
   move? Unreviewed alerting decays into noise within months.

**Alert fatigue is the failure mode that matters**, because it is silent: the team mutes the
noisy channel, and the real alert lands in the muted channel.

## Health checks

- **Liveness** - is the process functioning, or should it be restarted? Keep it shallow;
  a liveness check that depends on the database will restart every instance during a database
  blip, converting a partial outage into a total one.
- **Readiness** - should this instance receive traffic? This one *may* check dependencies.
- **Deep health / startup probe** - a richer check used at startup or by monitoring, not by the
  restart mechanism.

Distinguishing these prevents the classic cascade where a dependency problem triggers a restart
storm.

## Synthetic monitoring

Run the critical user journey continuously from outside. It catches what internal metrics miss:
DNS, TLS expiry, CDN misconfiguration, a firewall change, a whole-region failure. Certificate
expiry in particular should have its own explicit alert, days in advance - it is one of the most
common and most avoidable outages.

## Failure modes

- **Alerting on causes**, producing noise.
- **No duration requirement**, so every transient spike pages.
- **Dashboards instead of alerts.** Nobody is watching at 3 a.m.
- **Monitoring only the server**, so a broken frontend build is invisible.
- **Averages**, hiding the tail.
- **Liveness checks that depend on dependencies**, causing restart storms.
- **No monitoring of the monitoring** - a collector that stops reporting looks exactly like a
  healthy quiet system.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Service Level Objectives|Service Level Objectives]]
- [[Coding Knowledge/12 - Reliability Engineering/On-Call|On-Call]]
- [[Coding Knowledge/01 - Software Engineering/Observability|Observability]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Logging|Logging]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- Google, *Site Reliability Engineering*, four golden signals and alerting philosophy - <https://sre.google/books/> (readable online, cited only). Brendan Gregg, the USE method - <https://www.brendangregg.com/usemethod.html>.
