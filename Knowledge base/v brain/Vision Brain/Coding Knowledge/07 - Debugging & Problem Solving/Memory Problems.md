---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Memory Problems

Distinguishing a leak from normal behaviour, and finding what is retaining memory.

## First: is it actually a leak?

A single high reading is not evidence. **Growth across repeated identical cycles, with no
plateau, is.**

The diagnostic question is: *does it come back down when the work finishes?* If it does, it is
working memory. If it plateaus at a higher level, it may be allocator retention or a cache doing
its job. Only monotonic growth across cycles is a leak.

## Use the right metric

**Private bytes / private commit**, not working set or RSS, when attributing memory to a
process. RSS includes shared pages, so summing it across processes over-counts and produces
nonsense totals.

Also, RSS falling under pressure is **normal reclaim**, not a fix - and it will rise again.

## Things that look like leaks and are not

- **Allocator retention.** Freed memory is kept by the allocator for reuse rather than returned
  to the OS. Extremely common; RSS stays high with no leak.
- **Fragmentation.** Scattered live objects prevent whole pages being released.
- **Garbage collection not yet run**, or a generational collector that has not promoted.
- **Caches and buffer pools** behaving as designed.
- **Memory-mapped files** counted in RSS but backed by disk.
- **Page cache** on Linux (`buff/cache` in `free -h`) - reclaimable, and correct.
- **An active job.** *Measured in this project: 2.9 GB of apparent idle usage was an in-flight
  bulk-ingestion job, identified by a CPU delta of 184% of one core over a 30-second sample. The
  metric that settled it was CPU, not memory.*

## Finding a real leak

**The method: snapshot, do N cycles, snapshot, diff.** Absolute heap contents are noise; the
delta between two identical states is signal.

| Environment | Approach |
| --- | --- |
| Python | `tracemalloc` snapshots and `compare_to`; `objgraph.show_growth()`; `gc.get_objects()` |
| Node/JS | Three heap snapshots in DevTools; compare, inspect **retainers** |
| C/C++ | ASan/LSan, `valgrind --leak-check=full`, `heaptrack` |
| JVM | Heap dump + Eclipse MAT dominator tree |
| Any (Linux) | `/proc/<pid>/smaps_rollup`, `pmap -x` for the mapping breakdown |
| Any (Windows) | Private bytes over time; VMMap for the breakdown |

**Look at retainers, not at what is large.** The question is never "what is using memory" but
"what is preventing this from being freed". A retainer chain leading back to a global, a cache,
an event listener or a closure is the answer.

## The usual culprits

- A **global collection** that only ever grows.
- A **cache with no eviction policy or size limit**.
- **Event listeners / callbacks never removed**, holding their closures.
- **Closures capturing large objects** unnecessarily.
- **Threads or tasks that never exit**, each holding a stack and its locals.
- **Reference cycles** with finalisers, which some collectors will not collect.
- **A native library leaking** inside a managed process - the heap profiler shows nothing while
  RSS grows. This is the hardest case; suspect it when managed heap and RSS diverge.
- **Unbounded queues or buffers** between a fast producer and a slow consumer.

## Out-of-memory kills

- Linux OOM killer: `dmesg -T | grep -i oom` names the process and the score.
- Container OOM: **exit code 137**.
- A cgroup or container limit lower than expected - the process is not "leaking", it is capped.

Check the limit before investigating the process. A container with a 512 MB limit running a
service that legitimately needs 700 MB is a configuration problem, not a leak.

## Reducing usage

Stream instead of loading; bound every cache; use compact representations (`__slots__`,
generators, typed arrays, appropriate integer widths); release references in long-lived scopes;
and reduce worker or thread count - concurrency multiplies per-request memory, and lowering it
is often the fastest large win.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Memory Management|Memory Management]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]]

## Sources

- Tool documentation (`tracemalloc`, Valgrind, LeakSanitizer, Chrome DevTools, Eclipse MAT). Brendan Gregg on memory analysis - <https://www.brendangregg.com/>. The bulk-ingestion example was measured in this project on 2026-09-03.
