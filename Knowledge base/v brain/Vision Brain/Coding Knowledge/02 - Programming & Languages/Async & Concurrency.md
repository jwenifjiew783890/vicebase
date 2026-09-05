---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Async & Concurrency

The models, what each is good for, and the failure modes that only appear under load.

## Concurrency is not parallelism

**Concurrency** is structuring a program as independently progressing tasks. **Parallelism** is
executing them simultaneously on multiple cores. Async I/O gives concurrency without
parallelism; threads on multiple cores give both; Python threads give concurrency but not
parallel bytecode execution.

Choosing wrongly here is the root of most "we added threads and it got slower".

## The models

| Model | Good for | Costs |
| --- | --- | --- |
| **Async / event loop** | Many concurrent I/O waits | One blocking call stalls everything; function colouring |
| **Threads** | Blocking I/O, some parallel CPU | Shared mutable state, locks, races |
| **Processes** | CPU-bound work, isolation | Memory duplication, IPC serialisation cost |
| **Message passing / actors** | Isolating state by construction | Mailbox growth, back-pressure design |
| **Data parallel** | Uniform work over a large collection | Only applies to uniform work |

**Rule of thumb**: I/O-bound -> async or threads. CPU-bound -> processes or a native
implementation. Mixed -> async with a bounded thread/process pool for the heavy parts.

## What actually goes wrong

**Data race.** Two threads, at least one writing, no synchronisation. Results are not merely
unordered; the compiler and CPU may reorder or cache values so that no interleaving of the
source code explains what you observe.

**Race condition without a data race.** Check-then-act: `if not exists: create`. Both threads
check, both create. Correct locking of each individual operation does not fix it; the *pair*
must be atomic.

**Deadlock.** Two locks acquired in opposite orders. Prevention: a global lock ordering, or
lock-free designs, or timeouts on acquisition.

**Livelock and starvation.** Threads active but making no progress, or one thread never
scheduled.

**Lost update.** Read, modify, write from two places. Use atomic operations, compare-and-swap,
or a database-level atomic update.

**Blocking the event loop.** A synchronous call inside an async function stops every other task.
This is the single most common async bug and it presents as "the whole service got slow".

**Unbounded concurrency.** `Promise.all` / `gather` over 10,000 items opens 10,000 connections.
Always bound with a semaphore or a worker pool.

**Fire-and-forget.** A task nobody awaits: exceptions vanish, and in some runtimes the task can
be garbage collected mid-flight. Hold a reference and attach an error handler.

## Making it manageable

1. **Do not share mutable state.** Message passing and immutable data remove entire bug classes
   rather than mitigating them.
2. **If you must share, share behind one lock with a documented scope.** Hold it for the
   shortest possible time, and *never* across an `await` or a network call.
3. **Prefer the highest-level primitive available** - a thread pool, a queue, a channel - over
   raw threads and manual locks.
4. **Make concurrency explicit at the boundary**: this function may run concurrently with
   itself; this one may not.
5. **Bound everything** - queue depth, pool size, in-flight requests. Unbounded queues turn
   overload into out-of-memory.
6. **Design for cancellation** from the start. Cooperative cancellation with cleanup, and know
   what happens to in-flight work.

## Debugging

Concurrency bugs are non-deterministic by nature, so ordinary debugging fails - see
[[Coding Knowledge/07 - Debugging & Problem Solving/Concurrency & Race Conditions|Concurrency & Race Conditions]]
for the techniques that do work.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Concurrency & Race Conditions|Concurrency & Race Conditions]]
- [[Coding Knowledge/02 - Programming & Languages/Python|Python]]
- [[Coding Knowledge/02 - Programming & Languages/JavaScript|JavaScript]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]

## Sources

- Rob Pike, "Concurrency is not parallelism" (2012) - <https://go.dev/blog/waza-talk>. Herb Sutter, "The Free Lunch Is Over" (2005). Language runtime documentation for the specific models. Facts restated, text not copied.
