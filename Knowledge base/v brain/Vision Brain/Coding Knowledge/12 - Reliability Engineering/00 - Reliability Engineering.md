---
type: MOC
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Reliability Engineering

The operational discipline: setting a reliability target, spending it deliberately, and running the system without burning the people who run it.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

> [!info] Provenance for this whole section
> Most of the concepts here originate in **Google's Site Reliability Engineering books**, which
> are free to read online but carry **no reuse licence**, and in **Michael Nygard's
> *Release It!***, which is a copyrighted book. **Nothing from either is reproduced.** Every
> note is original prose that restates the engineering concept, names the source, and separates
> what the source contributes from our own synthesis and from what was measured in this project.
> See [[Coding Knowledge/99 - Sources & Provenance|Sources & Provenance]] for the policy.

## Why this is separate from sections 01 and 06

Three different things are easy to conflate:

| Section | Concerns | Example question |
| --- | --- | --- |
| [[Coding Knowledge/01 - Software Engineering/Reliability\|01 — Reliability]] | **Design time** — how the code behaves when a dependency fails | Where does the circuit breaker go? |
| [[Coding Knowledge/06 - DevOps & Infrastructure/00 - DevOps & Infrastructure\|06 — DevOps]] | **Tooling** — containers, hosts, networks, deploys, logs | How do I read this container's logs? |
| **12 — Reliability Engineering** | **Operational discipline** — targets, trade-offs, people | How reliable should this be, and who decides? |

## Notes

| Note | Answers |
| --- | --- |
| [[Coding Knowledge/12 - Reliability Engineering/Service Level Objectives\|Service Level Objectives]] | How reliable should this be, measured how? |
| [[Coding Knowledge/12 - Reliability Engineering/Error Budgets\|Error Budgets]] | Who decides between shipping and stabilising? |
| [[Coding Knowledge/12 - Reliability Engineering/Toil\|Toil]] | Which operational work should not exist? |
| [[Coding Knowledge/12 - Reliability Engineering/On-Call\|On-Call]] | How is this operated without burning people out? |
| [[Coding Knowledge/12 - Reliability Engineering/Incident Management\|Incident Management]] | Who does what while it is on fire? |
| [[Coding Knowledge/12 - Reliability Engineering/Postmortems\|Postmortems]] | How does an incident become an improvement? |
| [[Coding Knowledge/12 - Reliability Engineering/Capacity & Load Management\|Capacity & Load Management]] | What happens when demand exceeds capacity? |
| [[Coding Knowledge/12 - Reliability Engineering/Stability Antipatterns\|Stability Antipatterns]] | Which structures reliably cause outages? |

## The idea that ties them together

**Reliability is a quantity you choose and spend, not a virtue you maximise.** Every nine of
availability costs more than the last one, and beyond the point users can perceive it buys
nothing. So the discipline is: pick a target from what users actually need, measure against it,
and treat the difference between the target and 100% as a budget that funds change.

Everything else in this section follows from that.

## What applies at this scale

These practices come from organisations running large fleets with dedicated on-call teams. This
stack is a single-machine deployment with one operator. The **mechanisms** still apply and are
worth keeping:

- Choose a target rather than assuming "as reliable as possible".
- Alert on what a user would notice, not on what a machine reports.
- Write the incident down, because you will not remember it.
- Automate the third repetition.
- Treat a manual recovery step as a defect.

The **ceremony** does not: no error-budget policy meeting, no incident commander rotation, no
toil quota. Each note says explicitly which parts scale down and which do not.
