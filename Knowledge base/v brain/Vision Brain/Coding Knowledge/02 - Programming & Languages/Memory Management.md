---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Memory Management

Where memory goes, why processes grow, and how to tell a leak from normal behaviour.

## The metrics, and which one to trust

Confusing these is why memory investigations go wrong.

| Metric | Means |
| --- | --- |
| **RSS / working set** | Physical memory currently resident. Includes shared pages, so summing across processes double-counts |
| **Private / private commit** | Memory this process alone is responsible for. **The right number for "who is using memory"** |
| **Virtual size** | Address space reserved. Often enormous and meaningless |
| **Commit charge** | Total memory promised system-wide, including what is paged out |
| **Heap in-use** | What the language runtime thinks it is using - usually *less* than RSS |

RSS falling when another process needs memory is normal reclaim, not a fix. Private commit
staying flat under load is the real evidence of no leak.

## Why a process grows without leaking

- **Allocator retention.** `free()` returns memory to the allocator, which frequently keeps it
  for reuse rather than returning it to the OS. RSS stays high; there is no leak.
- **Fragmentation.** Many small live objects scattered across pages prevent whole pages being
  released.
- **GC not yet run**, or a generational collector that has not promoted and collected.
- **Caches and pools** doing exactly what they were built to do.
- **Memory-mapped files** counted in RSS but backed by disk.
- **Arena-per-thread allocators** (glibc) growing with thread count.

Conclusion: **a one-off high number is not evidence of a leak. A trend is.** Measure private
bytes repeatedly at the same point in a cycle.

## What a leak actually looks like

Monotonic growth in private bytes across repeated identical cycles, with no plateau. The
signature question is "does it come back down after the work finishes?".

Common causes by ecosystem:

- **Managed (Python, JS, Java, C#)**: unintentional retention - a growing global list or dict, a
  cache with no eviction, event listeners never removed, a closure capturing a large object, a
  logger holding request objects, threads that never exit.
- **Reference counted (Python, Swift, `shared_ptr`)**: reference cycles. Python's cycle
  collector handles most, but objects with `__del__` in a cycle, or C-extension cycles, may not
  be collected.
- **Manual (C, C++)**: missed `free`, an error path that returns before cleanup, ownership
  ambiguity across an API boundary.
- **Native inside managed**: a native library leaking under a Python or Node process. The heap
  profiler shows nothing; RSS grows anyway.

## Tools

| Environment | Tool |
| --- | --- |
| Python | `tracemalloc` snapshots and diffs; `objgraph`; `py-spy dump` for a live process |
| Node/JS | `--inspect` heap snapshots, compare three snapshots and look at retainers |
| C/C++ | ASan/LSan, `valgrind --leak-check=full`, `heaptrack`, `massif` |
| JVM | heap dump + Eclipse MAT dominator tree |
| Any, on Linux | `/proc/<pid>/smaps_rollup`, `pmap -x` |
| Any, on Windows | private bytes via `Get-Process`, VMMap, RAMMap |

**The method that works**: take a snapshot, do N cycles of work, take another, **diff**. The
absolute contents of a heap are noise; the delta between two identical states is signal.

## Reducing memory in practice

- Stream instead of loading whole files or result sets.
- Bound every cache with a size and an eviction policy.
- Use compact representations: generators over lists, `__slots__` in Python, typed arrays, the
  right integer width.
- Release references explicitly when a large object is done with in a long-lived scope.
- Reduce worker or thread counts before optimising code - concurrency multiplies per-request
  memory.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Memory Problems|Memory Problems]]
- [[Coding Knowledge/02 - Programming & Languages/C and C++|C and C++]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]

## Sources

- Brendan Gregg on memory analysis - <https://www.brendangregg.com/>; Python `tracemalloc` documentation - <https://docs.python.org/3/library/tracemalloc.html>; Valgrind and LLVM LeakSanitizer documentation. Metric definitions restated from OS documentation.
