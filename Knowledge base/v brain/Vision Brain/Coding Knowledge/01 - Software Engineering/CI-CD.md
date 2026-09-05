---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# CI/CD

The pipeline as a safety mechanism: what it must check, how it fails usefully, and how it gets undermined.

## What the pipeline is for

To make **the safe path the easy path**. Every check that runs automatically is a class of
mistake that can no longer reach production through inattention. The value is not automation
for its own sake - it is that correctness stops depending on anyone remembering.

## Pipeline stages, in order of how fast they should fail

1. **Lint and format** - seconds. Mechanical, no opinions in review.
2. **Type check** - seconds. Catches the whole class of shape errors.
3. **Unit tests** - under a couple of minutes, or people bypass the pipeline.
4. **Build** - a real artefact, built once and promoted, not rebuilt per environment.
5. **Integration tests** - against real dependencies in containers.
6. **Security checks** - dependency vulnerabilities, secret scanning, static analysis.
7. **Deploy to staging**, smoke test.
8. **Deploy to production**, with a defined rollback.

Order by speed, so that the cheap failure arrives first. A pipeline where the linter failure
surfaces after twelve minutes of tests wastes an engineer's attention every time.

## Non-negotiables

- **Build once, promote the same artefact.** Rebuilding per environment means the thing tested
  is not the thing shipped.
- **Configuration comes from the environment**, not from the artefact. Same image, different
  config.
- **Every deploy has a rollback**, and it has been rehearsed. A rollback plan that has never
  run is a hypothesis.
- **The pipeline is reproducible**: pinned versions, locked dependencies, no "latest".
- **Secrets from a secret store**, injected at runtime, never in the repository or the image
  layers.
- **A red main branch is an emergency**, not a background condition. The moment red becomes
  normal, the pipeline has stopped being a signal.

## Deployment strategies

| Strategy | How | Best for |
| --- | --- | --- |
| **Rolling** | Replace instances gradually | The default; needs N-1/N+1 compatibility |
| **Blue-green** | Two environments, switch traffic | Instant rollback; costs double capacity |
| **Canary** | Small traffic share first, watch metrics | Risky changes; needs good observability |
| **Feature flag** | Deploy dark, enable separately | Decouples deploy from release - the most useful of all |

**Separate deploy from release.** Shipping code and turning it on are different decisions, and
keeping them separate is what makes large changes safe.

## Database changes

The rule that prevents most deploy disasters: **schema changes must be backwards compatible for
one release**. Add a column, deploy code that writes both, backfill, deploy code that reads the
new one, then drop the old. A destructive migration deployed with the code that needs it cannot
be rolled back.

## Failure modes

- **Flaky pipeline.** Re-running until green trains everyone to ignore failures, including real
  ones.
- **Slow pipeline.** Encourages batching changes, which makes each deploy riskier.
- **Tests that do not run.** A misconfigured matcher silently matching zero tests; the pipeline
  is green and empty. Check that the test count is what you expect.
- **Deploying without a health gate.** Rolling out to every instance before noticing the new
  build crashes on boot.
- **Manual steps in the middle.** Anything requiring a human at 2 a.m. will be done wrong.
- **No artefact provenance.** Unable to answer "which commit is running in production?".

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]
- [[Coding Knowledge/09 - Engineering Practices/Release Strategy|Release Strategy]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment|Deployment]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Build & Deployment Failures|Build & Deployment Failures]]

## Sources

- Jez Humble & David Farley, *Continuous Delivery* (2010) - build-once-promote and deploy/release separation; cited, not reproduced. The Twelve-Factor App, config in the environment - <https://12factor.net/config> (repository CC BY 4.0, verified 2026-09-03). Google, *Site Reliability Engineering*, release engineering chapter - cited only.
