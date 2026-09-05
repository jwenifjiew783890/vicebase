---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Proven Fixes

Solutions that reliably work, and the mechanism that makes each one work - because a fix applied without its mechanism is cargo cult.

## Reliability

**Timeout on every remote call.** *Mechanism*: bounds the worst case so one stalled dependency
cannot consume the caller's resources. *Measured here: an unbounded model call hung for 302
seconds; `timeout: 60000` with `maxRetries: 1` turned it into a clean 61-second failure.*

**Exponential backoff with jitter.** *Mechanism*: spreads retries in time so they do not
synchronise into a herd, and gives the dependency room to recover.

**Circuit breaker.** *Mechanism*: converts a slow failure into a fast one, freeing the caller's
threads and removing load from a struggling dependency.

**Bulkhead (separate pools per dependency).** *Mechanism*: one saturated dependency cannot
consume the resources the healthy ones need.

**Idempotency key.** *Mechanism*: makes "retry after unknown outcome" safe, which is the only
honest response to a timeout.

**Outbox pattern.** *Mechanism*: the state change and the event are written in one transaction,
so they cannot diverge; publishing happens separately and may retry.

**Bounded queue with explicit shedding.** *Mechanism*: back-pressure. Failure becomes a fast
rejection instead of memory exhaustion.

## Correctness

**Parse, don't validate.** *Mechanism*: converting input into a validated type once at the
boundary means the rest of the code cannot receive an invalid value at all.

**Database constraints.** *Mechanism*: the last line of defence that every path passes through -
including migrations, scripts and manual fixes, which bypass application validation.

**Atomic compound operations** (`UPDATE ... WHERE`, upsert, compare-and-swap). *Mechanism*:
removes the window between check and act, which is where the race lives.

**Sentinel instead of an empty result.** *Mechanism*: in a pipeline where an empty stage causes
downstream stages to be skipped, a sentinel keeps the pipeline flowing and lets the caller
distinguish "no results" from "nothing ran". *Measured here: an empty n8n node silently halted an
agent with every step marked success.*

**Explicit non-null success test.** *Mechanism*: `error === undefined` is false when a successful
call returns `error: null`. Test the actual success condition, not the absence of a field.

**Read state from a named source, not from positional context.** *Mechanism*: `$json` at a
pipeline node means "the previous node's output", which differs from "the workflow input" in
multi-hop flows. *Measured here: retrieved knowledge silently vanished until reads were changed
to reference the trigger by name.*

## Performance

**Add the index.** *Mechanism*: turns a sequential scan into a lookup. The most common single fix
for a "slow application".

**Batch the N+1.** *Mechanism*: one query with `IN`, or eager loading, replaces n round trips -
each of which costs latency that no amount of query tuning removes.

**Move work off the request path.** *Mechanism*: the user waits for the response, not for the
work.

**Stream instead of loading.** *Mechanism*: memory becomes O(1) in the input size.

**Bound concurrency with a semaphore.** *Mechanism*: prevents resource exhaustion from
parallelism that the downstream cannot absorb.

## Change safety

**Expand and contract.** *Mechanism*: at every moment, both the old and new code work against
the current schema, so rollback is always possible.

**Feature flag.** *Mechanism*: separates deploy from release, making the change reversible in
seconds without a deployment.

**Parallel run before switching.** *Mechanism*: divergences are observed on real data before
anyone depends on the new path.

**Strangler fig.** *Mechanism*: the migration is a series of small reversible steps rather than
one irreversible event.

## Diagnosis

**`git bisect run`.** *Mechanism*: binary search over history; `log2(n)` tests instead of n.

**Snapshot-diff for memory.** *Mechanism*: absolute heap contents are noise; the delta between
two identical states is signal.

**`py-spy dump` / thread dump on a hung process.** *Mechanism*: shows exactly where every thread
is blocked, with no code change and no restart.

**Count and rank distinct log messages** (`sort | uniq -c | sort -rn`). *Mechanism*: converts an
unreadable volume into a ranked list, where the rare message is visible.

**Trust the CA rather than disabling verification.** *Mechanism*: keeps the security property
while solving the actual problem, which is that the certificate is not in the trust store.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/11 - Vision & OpenCode/Proven Solutions|Proven Solutions]]
- [[Coding Knowledge/10 - Engineering Experience/Common Failure Patterns|Common Failure Patterns]]

## Sources

- Michael Nygard, *Release It!* (2nd ed., 2018) for the stability patterns - cited, not reproduced. AWS Builders' Library - <https://aws.amazon.com/builders-library/>. Alexis King, "Parse, don't validate" - <https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/>. All "measured here" items were observed in this project on 2026-09-03.
