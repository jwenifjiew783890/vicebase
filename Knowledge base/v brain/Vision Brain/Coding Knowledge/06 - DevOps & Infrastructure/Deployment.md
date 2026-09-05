---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Deployment

Getting a change into production without an incident, and getting back out when there is one.

## The three properties that matter

1. **Reproducible** - the same input produces the same artefact. Pinned versions, lock files,
   no `latest`.
2. **Reversible** - you can get back to the previous state quickly, and it has been rehearsed.
3. **Observable** - you can tell within minutes whether it worked, from signals rather than from
   silence.

A deploy missing any of these is a gamble regardless of how much testing preceded it.

## Build once, promote

Build the artefact once and promote that exact artefact through environments. Rebuilding per
environment means the thing tested is not the thing shipped, and the difference is exactly where
the incident comes from.

Configuration comes from the environment, so one artefact behaves correctly everywhere.

## Strategies

| Strategy | Rollback | Cost |
| --- | --- | --- |
| **Recreate** (stop, start new) | Redeploy old | Downtime |
| **Rolling** | Roll forward or back gradually | Needs version compatibility |
| **Blue-green** | Switch traffic back - fastest | Double capacity |
| **Canary** | Stop the rollout | Needs good metrics |
| **Feature flag** | Turn it off - instant | Flag debt |

**Separate deploy from release.** Ship the code disabled, enable it as a separate decision. This
converts a risky deploy into a reversible configuration change, and it is the single most useful
practice in this note.

## Compatibility during a rolling deploy

Old and new versions run simultaneously. Everything they share must tolerate both:

- **Database schema** - backwards compatible for one release; expand, migrate, contract.
- **Message formats** - consumers must tolerate unknown fields; do not remove a field in the
  same release that stops writing it.
- **APIs** - additive only.
- **Caches** - a shared cache holding a changed shape will be read by the old version. Version
  the key.

## Pre-deploy checklist

- Does it roll back, and has that been tested?
- Are migrations backwards compatible?
- Are new configuration values present in every environment?
- Do health checks reflect real readiness, including dependencies?
- What signal will show a problem, and who is watching it?
- Is anyone available if it goes wrong? *Deploying at the end of the day or before a break is a
  process failure, not a scheduling detail.*

## After deploying

Watch error rate, latency percentiles, saturation and the specific behaviour the change affects,
for long enough that a slow-burning problem would appear. Many deployment failures surface at
the next traffic peak, not at deploy time.

## Failure modes

- **No rollback plan**, so an incident becomes a forward-fix under pressure.
- **Migration and code deployed together**, making rollback impossible.
- **Config drift** between environments - it works in staging because staging has a variable
  production lacks.
- **Manual steps** in the middle.
- **Health check that passes before the app is ready**, so traffic arrives at a broken instance.
- **No canary or gradual rollout** for a risky change.
- **Deploying an artefact nobody can trace to a commit.**

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Error Budgets|Error Budgets]]
- [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]]
- [[Coding Knowledge/09 - Engineering Practices/Release Strategy|Release Strategy]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Build & Deployment Failures|Build & Deployment Failures]]

## Sources

- Jez Humble & David Farley, *Continuous Delivery* (2010) - cited, not reproduced; The Twelve-Factor App - <https://12factor.net/> (repository CC BY 4.0, verified 2026-09-03); Google, *Site Reliability Engineering* - cited only.
