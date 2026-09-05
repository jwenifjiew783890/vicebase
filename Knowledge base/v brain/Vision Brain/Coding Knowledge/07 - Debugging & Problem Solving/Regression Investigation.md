---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Regression Investigation

It used to work. This is the most tractable class of bug, because the answer is in the history.

## Establish the two endpoints

Find a **known-good** and a **known-bad** state. Without both, there is nothing to bisect.

If "it used to work" is a belief rather than an observation, verify it - a surprising amount of
regression investigation ends with "it never worked, nobody exercised that path".

## Bisect

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.2.0
# test, then: git bisect good | git bisect bad
```

With a reliable test, automate it entirely:

```bash
git bisect run ./test-the-thing.sh
```

This is the highest-return debugging tool most engineers under-use. It converts an open-ended
investigation into `log2(n)` mechanical steps - fifteen commits tested out of thirty thousand.

**Requirements**: each commit must build (which is why commit hygiene matters), and the test must
be reliable. A flaky test makes bisect return a random commit with full confidence.

## When the code did not change

Then something else did. In rough order of frequency:

| Suspect | How to check |
| --- | --- |
| **Dependency** | Lock file diff; was an unpinned package published? |
| **Data** | New shape, volume, or an edge case that had not occurred |
| **Configuration** | Environment variables, feature flags, secrets rotated |
| **External API** | Provider changed, deprecated, or silently updated a model |
| **Infrastructure** | Base image, kernel, resource limits, network policy |
| **Time** | Certificate expiry, token expiry, a date boundary, DST, month-end |
| **Scale** | It worked at 100 rows and not at 100,000 |

**Certificate and token expiry deserve special mention** - they produce a sudden failure with no
change on your side, and they are among the most common "nothing changed" causes.

## Once the commit is found

- **Read the whole commit**, not just the obvious line. The cause may be in a test change, a
  configuration file or a dependency bump inside it.
- **Understand why it broke.** A commit that *revealed* a latent bug is not the same as one that
  introduced it, and reverting the wrong one hides the real problem.
- **Check for the same pattern elsewhere.** The mistake is rarely unique.

## Revert or fix forward

**Revert** when: production is affected, the fix is not obvious, or the change is not urgent.
Reverting is fast, safe and buys time to understand.

**Fix forward** when: the revert would break something that now depends on it, the fix is small
and understood, or the change cannot be cleanly reverted.

Reverting is not an admission of failure; it is the correct first response to a production
regression. Understand it afterwards, with the pressure removed.

## Close the loop

**Every regression becomes a test.** This is the single highest-value output of the
investigation - it is the mechanism by which a codebase accumulates protection against exactly
the failures it has actually experienced.

Verify the test properly: it must **fail on the bad commit and pass on the fix**. A test that
passes in both directions proves nothing and will be trusted anyway.

Then ask the systemic question: **why did nothing catch this?** Missing test, gap in the review,
absent type, no alert. The answer there prevents the next one.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Version Control|Version Control]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]]

## Sources

- `git bisect` documentation - <https://git-scm.com/docs/git-bisect>. Practitioner synthesis otherwise.
