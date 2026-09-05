---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Performance Profiling

Finding where the time actually goes, which is reliably somewhere other than where you expect.

## Measure first, always

Developer intuition about performance is wrong most of the time. Optimising without a profile
means spending effort on 3% of the runtime while 80% sits elsewhere, and shipping complexity for
no benefit.

**Establish a baseline number before changing anything**, so improvement is demonstrable rather
than asserted.

## Define the question precisely

"It is slow" is not actionable. Which operation, under what conditions, how slow, compared with
what? Then decide which metric matters:

- **Latency** - one operation's duration. Report p50/p90/p99, never the average.
- **Throughput** - operations per second at a given concurrency.
- **Resource** - CPU, memory, I/O, network per operation.

Latency and throughput trade off. Optimising one can worsen the other, so name the target.

## Where to look, in order

1. **The whole path.** Measure end to end first, then decompose. Optimising a function that is
   2% of the request is wasted work.
2. **I/O before CPU.** Most slow applications are waiting - database, network, disk - not
   computing. A CPU profile of an I/O-bound process shows an idle process.
3. **The database.** Missing index, N+1, or a query returning far more than needed. This is the
   most common single answer in web applications.
4. **Serialisation.** JSON encode/decode at high rates is a real cost.
5. **Algorithmic complexity.** An accidental O(n^2) - a list membership test inside a loop - is
   invisible at 10 items and fatal at 10,000.
6. **Only then, micro-optimisation.**

## Profiler types

| Type | Shows | Cost | Use |
| --- | --- | --- | --- |
| **Sampling** | Where time is spent statistically | Low | Production, first look |
| **Instrumenting** | Exact call counts and times | High, distorts | Development, call-count questions |
| **Tracing / APM** | Time across services | Moderate | Distributed systems |
| **Flame graph** | Call-stack time visually | - | The fastest way to see a hot path |

**Read a flame graph by width, not by height.** Width is time; depth is only call-stack depth.
The widest plateau is the target.

## Tools

| Environment | Tool |
| --- | --- |
| Python | `cProfile` + `snakeviz`; `py-spy` for a live process without restarting it |
| Node/JS | `--cpu-prof`, Chrome DevTools, `clinic` |
| Browser | DevTools Performance panel; Lighthouse for the page-level view |
| JVM | async-profiler, JFR |
| Native | `perf`, `valgrind --tool=callgrind` |
| Databases | `EXPLAIN ANALYZE`, slow query log, `pg_stat_statements` |
| System | `top`, `iostat -x`, `iotop`, `perf top` |

`py-spy dump` on a hung process is one of the highest-value diagnostics available: it shows what
every thread is doing right now, with no code changes and no restart.

## Measuring honestly

- **Warm up** before measuring - JIT, caches, connection pools all distort the first runs.
- **Realistic data volume and distribution.** Real data is skewed; skew is what breaks things.
- **Repeat and report variance.** One run is noise.
- **Isolate.** Other load on the machine invalidates the measurement.
- **Change one thing**, re-measure, keep it only if it helped.

## After optimising

State the before and after numbers, and the conditions. "Faster" without numbers is not a
result. Then check that the optimisation did not trade away correctness, readability or memory -
and if it did, that the trade was worth it and is documented.

## Failure modes

- **Optimising without profiling.**
- **Profiling a warm-up run**, or an unrepresentative input.
- **Averages hiding a bad tail.**
- **Micro-optimising inside an I/O wait.**
- **Fixing the benchmark rather than the workload.**
- **No baseline**, so improvement cannot be demonstrated.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Database Problems|Database Problems]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Performance|Web Performance]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]

## Sources

- Brendan Gregg on flame graphs and systems performance - <https://www.brendangregg.com/flamegraphs.html>; tool documentation for each profiler listed.
