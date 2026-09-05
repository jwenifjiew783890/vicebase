---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Reproducible Debugging

Making the failure happen on demand. Everything else in debugging depends on this, and it is usually the step people skip.

## Why it comes first

Without a reliable reproduction you cannot: confirm a hypothesis, know when it is fixed, write a
regression test, or hand the problem to anyone else. Time spent getting to a reproduction is
almost always repaid, because every later step runs against it repeatedly.

**Reproduction speed is a multiplier on the whole investigation.** A 30-second reproduction and a
10-minute one are completely different investigations, and it is often worth an hour to convert
one into the other.

## Getting there

**1. Capture the exact conditions.** Input, environment, versions, timing, sequence of actions,
which user, which record, which host. The report "it failed" is missing all of it; ask.

**2. Reproduce in the environment that failed** before trying to reproduce locally. A local
reproduction that does not fail proves nothing, and a lot of time is lost concluding "cannot
reproduce" when the difference was the environment.

**3. Then reduce.** Remove input, configuration and code until it stops failing. The last thing
removed is the trigger. Delta debugging - repeatedly halving the input - automates this and
routinely produces a minimal case that makes the cause self-evident.

**4. Automate it.** A script or test that triggers the failure. Now you can bisect, and you have
the regression test already written.

## Controlling the variables

Non-determinism is what stands between you and a reproduction. Remove it:

| Source | Control |
| --- | --- |
| **Time** | Inject a clock; freeze it in tests |
| **Randomness** | Seed it, and log the seed on failure |
| **Concurrency** | Reduce to one thread; or force an interleaving with delays |
| **Network** | Record and replay, or a stub |
| **External state** | A fixed fixture or a snapshot |
| **Environment** | A container with pinned versions |
| **Filesystem/ordering** | Sort directory listings; do not rely on order |

**Log the seed and the inputs on failure.** A randomised test that fails once and cannot be
repeated has wasted its finding; one that prints its seed is reproducible forever.

## When it will not reproduce

- **Add observability instead.** If you cannot reproduce it, instrument the path so the next
  occurrence is fully described: log the inputs, the intermediate values, the decision points.
  Then wait. This is frequently faster than chasing it.
- **Look for a state you are not reproducing** - a specific record, a cache entry, an
  accumulated condition, a particular sequence of prior actions.
- **Consider timing.** Intermittent means concurrency, timeout, or a scheduled boundary until
  proven otherwise.
- **Consider environment.** Different data, different scale, different hardware, different
  locale, different timezone.
- **Check whether it is being swallowed** somewhere - the failure may be happening far more often
  than it is being reported.

## Preserving the evidence

Before restarting anything: capture logs, a thread dump, a heap dump, the process list, the
current configuration, and the state of the data. **A restart destroys the only copy of the
failure.** This is the most common irreversible mistake in incident response - the pressure to
restore service is real, but sixty seconds of evidence capture makes the difference between
fixing it and waiting for it to happen again.

## Keeping the reproduction

Once you have it, keep it as a test. A reproduction that only lived in someone's terminal has to
be rediscovered the next time.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Systematic Debugging|Systematic Debugging]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Concurrency & Race Conditions|Concurrency & Race Conditions]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]

## Sources

- Andreas Zeller, *Why Programs Fail* (2nd ed., 2009) - delta debugging; cited, not reproduced. Practitioner synthesis for the evidence-preservation and non-determinism sections.
