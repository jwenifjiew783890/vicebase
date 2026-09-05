---
type: note
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Failure Patterns

Recurring ways engineering work goes wrong, independent of language or stack. Read before committing to an approach - most of these are cheap to avoid and expensive to discover.

## In the code

**The swallowed error.** `except: pass`, an ignored return code, a promise with no `.catch`.
Converts a loud failure into a silent wrong answer, which is the most expensive class of bug.

**The empty collection that stops everything.** A stage that legitimately produces nothing, in a
pipeline whose downstream stages are skipped when a stage is empty. Every step reports success
and the result is missing. Emit a sentinel rather than nothing when downstream must continue.

**Off-by-one in the boundary case.** Empty, single-element, exactly-at-the-limit, and
one-past-the-limit. Test the boundary, not the middle.

**The unbounded wait.** Any network call without a timeout will eventually hang for as long as
the peer allows. One stalled dependency then freezes everything upstream. Bound every call, and
bound the retries too - a default of "retry twice" turns one 5-minute stall into fifteen.

**The retry that amplifies.** Retries without backoff and jitter turn a brief degradation into a
self-sustaining overload. Add exponential backoff, jitter, a cap, and a circuit breaker.

**Time as an assumption.** Local time, DST, leap seconds, clock skew, monotonic vs wall clock,
and "this will surely finish within a second". Use UTC internally and a monotonic clock for
durations.

**Shared mutable state across concurrency.** The bug that reproduces on the CI machine and not
yours. See [[Coding Knowledge/07 - Debugging & Problem Solving/Concurrency & Race Conditions|Concurrency & Race Conditions]].

**Unbounded growth.** A cache with no eviction, a list that only appends, a log with no
rotation, a table with no retention. Fine for a week, an incident at month three.

**The N+1 query.** A loop that queries per item. Invisible with ten rows, fatal with ten
thousand.

**String-built structure.** SQL, shell commands, HTML or JSON assembled by concatenation.
This is the injection class in its entirety. Use parameters, argument arrays and real
serialisers.

**Config drift.** The same value in three places. It will diverge, and the divergence will be
found in production.

## In the design

**Premature abstraction.** A framework built for three imagined cases, all of which turn out
wrong. Wait for the third real duplication.

**The distributed monolith.** Services split for organisational reasons but still deploying
together and sharing a database. All the cost of distribution, none of the independence.

**The leaky abstraction that must not leak.** Hiding a network call behind an interface that
looks local. Callers then treat it as free, and the failure model is invisible.

**No back-pressure.** A producer faster than its consumer with an unbounded queue between them
converts a throughput problem into an out-of-memory crash.

**Single point of failure treated as reliable.** One provider, one key, one host, no fallback,
no degraded mode. The question is not whether it fails but what happens when it does.

**Migration with no rollback.** A schema change that cannot be reversed, deployed alongside code
that depends on it, is a decision that cannot be undone under pressure.

## In the process

**Fixing what you have not reproduced.** The change may be correct and irrelevant, and now the
real bug is hidden behind a plausible patch.

**The bundled diff.** A fix, a refactor and a rename in one change. Review degrades, the bisect
is useless, and the revert takes the fix with it.

**"It works on my machine".** Version, environment variable, cached artefact, local file,
different data, different OS. Reproduce in the environment that failed.

**Trusting the summary over the artefact.** A green pipeline that skipped the tests, a log
excerpt that omitted the error, a report that says "verified". Look at the thing itself.

**Optimising without measuring.** Effort spent on 3% of the runtime while the other 80% sits
untouched. Profile first.

**Changing several variables at once.** Then you cannot attribute the outcome, in either
direction.

## In AI-assisted work specifically

**Confident invention.** A function, flag or config key that does not exist in the installed
version. Verify against the actual API surface, not against plausibility.

**Silent scope expansion.** An unrequested rewrite delivered as a bug fix.

**Unverified claims of verification.** "Tests pass" without a test run. Report what was
actually executed.

**Cargo-culted structure.** Patterns copied from a different stack's conventions into one where
they do not apply.

---

## See also

- [[Coding Knowledge/10 - Engineering Experience/Common Failure Patterns|Common Failure Patterns]]
- [[Coding Knowledge/10 - Engineering Experience/Approaches That Commonly Fail|Approaches That Commonly Fail]]
- [[Coding Knowledge/10 - Engineering Experience/Architecture Failure Modes|Architecture Failure Modes]]

## Sources

- Practitioner synthesis. Corroborating published material: public postmortems indexed at <https://github.com/danluu/post-mortems>; AWS Builders' Library on timeouts, retries and jitter - <https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/>; OWASP Top Ten - <https://owasp.org/www-project-top-ten/>. The AI-specific patterns are observations from this project.
