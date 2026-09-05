---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# Release Strategy

Getting a change to users with a way back, and knowing quickly whether it worked.

## Separate deploy from release

**Deploying** puts code on servers. **Releasing** makes it active for users. Keeping these
separate - via feature flags - is the single most useful practice in this note, because it turns
a risky deploy into a reversible configuration change.

It also means a large change can ship in small deployed increments while remaining invisible,
which is what makes trunk-based development possible without long-lived branches.

## Sequencing a change

1. **Deploy dark.** The code ships, disabled.
2. **Enable internally.** Your own team uses it.
3. **Enable for a small share.** Watch the metrics that would show a problem.
4. **Ramp.** Increase gradually, watching at each step.
5. **Full release.**
6. **Remove the flag.** This step is skipped constantly, and flag debt accumulates until nobody
   knows which combinations are actually tested.

## Rollback

Every release needs a defined way back, and it must be **rehearsed** - a rollback plan that has
never run is a hypothesis.

| Mechanism | Speed | Applies to |
| --- | --- | --- |
| Feature flag off | Seconds | Anything behind a flag |
| Traffic switch (blue-green) | Seconds | Whole-version rollback |
| Redeploy previous artefact | Minutes | Standard |
| Database rollback | Slow, sometimes impossible | Avoid needing it |

**The database is what makes rollback hard.** Keep schema changes backwards compatible for one
release; then the code can always go back even when the schema cannot.

## Release size

Small and frequent beats large and rare. A small release has a small blast radius, an obvious
cause when something breaks, and a cheap rollback. A quarterly release bundles a hundred changes
whose interactions have never been observed, and when it fails nobody knows which change did it.

The instinct to batch changes "to reduce risk" inverts the actual risk.

## Watch after releasing

Define **before** the release what signals would indicate a problem, and watch them for long
enough that a slow-burning issue surfaces - many failures appear at the next traffic peak, not
at deploy time.

Error rate, latency percentiles, saturation, and the specific behaviour the change affects. Plus
the business-level metric, which is often the fastest true signal.

## Timing

Release when people are available to respond. Deploying at the end of the day, before a weekend
or before a holiday is a process failure, not a scheduling detail - the code is no riskier, but
the response time is much worse.

## Communicating

- **Changelog** for users, in their terms, not commit messages.
- **Breaking changes announced in advance**, with a migration path and a timeline.
- **Deprecations measured**, not assumed - instrument usage so you know who is still on the old
  path before removing it.

## Failure modes

- **No flag**, so the only rollback is a redeploy.
- **Flags never removed**, producing an untested combinatorial space.
- **Migration and dependent code released together**, making rollback impossible.
- **Big-bang releases**, unattributable when they break.
- **Nobody watching** after the release.
- **No changelog**, so users discover changes by being surprised.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment|Deployment]]
- [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]]
- [[Coding Knowledge/09 - Engineering Practices/Change Management|Change Management]]

## Sources

- Jez Humble & David Farley, *Continuous Delivery* (2010) - cited, not reproduced; Martin Fowler on feature toggles - <https://martinfowler.com/articles/feature-toggles.html>.
