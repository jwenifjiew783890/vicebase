---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# On-Call

Operating a system without destroying the person operating it - which is a reliability property, not a welfare one.

> [!info] Provenance
> The sustainable-rotation argument, the pages-per-shift limit and the balance between
> operational and project work are **Google SRE**, restated in our own words. The
> single-operator adaptation and the failure modes are **our synthesis**.

## Why this is an engineering topic

An exhausted operator makes worse decisions during exactly the incidents that need good ones.
Alert fatigue is not a morale problem with a reliability side effect — it **is** the reliability
problem, because the muted channel is where the real alert lands.

So the design constraints below are about system behaviour, not about kindness.

## The constraints that matter

**Cap the pages per shift.** A widely-used figure is around two actionable pages in a
twelve-hour shift; beyond that there is no time to investigate properly, and the response
degrades into pattern-matching. Exceeding the cap consistently is a signal to fix the system or
the alerts, not to try harder.

**Every page must be actionable.** If the response is "acknowledge and watch", it should not have
paged. Move it to a ticket or a dashboard.

**Every alert needs a documented response.** What it means, how to confirm it is real, what to
do first, and when to escalate. Written before the incident, because nobody writes it during one.

**Protect time for engineering.** If all available time goes to operations, nothing ever improves
and the operational load grows. This is the same self-reinforcing loop described in
[[Coding Knowledge/12 - Reliability Engineering/Toil|Toil]].

**Handoffs are explicit.** What is open, what was tried, what to watch. An implicit handoff loses
the state of every in-flight investigation.

## What a good runbook entry contains

1. **What this alert actually means** — in terms of user impact, not of the metric.
2. **How to confirm it is real**, including the known false-positive causes.
3. **The first mitigation** — usually roll back, fail over, or shed load. Mitigate before
   diagnosing.
4. **How to check the mitigation worked.**
5. **When to escalate**, and to what.
6. **What not to do** — the tempting action that makes it worse.

Point 3 is the one most often missing and most needed. **Restore service first; understand it
afterwards.** Rolling back before knowing the cause is correct behaviour under pressure, not a
failure of rigour.

## Applying it here *(our synthesis)*

This stack has one operator, no rotation, no paging, and no availability commitment. Most of the
ceremony is irrelevant. Three things scale down and are worth keeping:

**1. Nothing should require a human at an unreasonable hour.** In practice that means services
restart themselves (logon scheduled tasks), containers use `unless-stopped`, and no recovery
depends on a step only one person knows. A manual recovery step is a defect.

**2. The runbook is the README.** `D:\opencode\README.md` and
`D:\n8n\workflows\AGENT-REGISTRY.md` already carry the operational knowledge — how to start,
stop, publish, and what the known traps are. That is the right home for it: next to the thing,
version-controlled, found under pressure.

**3. Silent failure is the local equivalent of a missed page.** With no alerting, the only
protection against a silently broken agent is that the system fails **loudly** when it fails.
This is why the sentinel item, the explicit non-null success test, and asserting on output rather
than on the absence of an error all matter more here than they would in a monitored environment —
see [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]].

## Failure modes

- **Noisy alerting**, which is muted, after which nothing alerts.
- **Alerts with no runbook**, so every response is improvised from scratch.
- **A single point of knowledge** — one person who knows how to recover something.
- **No protected engineering time**, so operational load compounds.
- **Diagnosing before mitigating** while users are affected.
- **Implicit handoff**, losing in-flight investigation state.
- **Recovery steps that only exist in someone's shell history.**

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Incident Management|Incident Management]]
- [[Coding Knowledge/12 - Reliability Engineering/Toil|Toil]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring|Monitoring]]
- [[Coding Knowledge/01 - Software Engineering/Documentation|Documentation]]

## Sources

- Rotation, page-limit and workload-balance concepts derived from Google, *Site Reliability Engineering* - <https://sre.google/books/> - **no reuse licence**; restated in our own words, nothing reproduced. The runbook structure, the local adaptation and the failure modes are our synthesis.
