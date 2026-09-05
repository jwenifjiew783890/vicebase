---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Processes & Resources

Measuring CPU, memory and I/O honestly, and attributing them to the right process.

## Measure before concluding

The most common mistake in resource investigation is a confident narrative built on the wrong
metric. Establish, in order: **what the total is**, **which processes account for it**, and
**whether it is growing**. Only then ask why.

## Memory metrics, and which to trust

| Metric | Means | Use for |
| --- | --- | --- |
| **Private bytes / private commit** | Memory this process alone is responsible for | **Attributing memory to a process** |
| **Working set / RSS** | Physical memory currently resident, including shared pages | Total pressure; **do not sum across processes** - it double counts |
| **Virtual size** | Address space reserved | Almost nothing |
| **Commit charge** | System-wide promised memory | Whether the system is near its limit |

Summing RSS across processes over-counts shared libraries and produces impossible totals. Use
private bytes per process, and the OS's own total for the system.

## Attributing correctly

- **Take the sample twice, at the same point in a cycle.** A single reading cannot distinguish a
  leak from normal working memory.
- **Note the process start time and parent.** An orphan from an earlier session looks identical
  to a live worker in a process list, and is often the actual answer.
- **Check what is *doing* something**, not only what is large. CPU delta over a fixed interval
  separates active work from resident-but-idle.
- **Beware type mismatches when joining data sources.** *Measured in this project:
  `Win32_Process.ProcessId` is `UInt32` while `Get-Process.Id` is `Int32`; using one as a
  hashtable key and looking up with the other silently dropped three processes from a memory
  census.* Cast explicitly when joining.

## CPU

- **Percentages are per core.** 184% means nearly two cores saturated, not "184% of the machine".
- **Load average** (Linux) counts runnable *and* uninterruptible-sleep tasks, so a high load with
  low CPU usually means I/O wait.
- **A short sample lies.** Measure over a fixed interval and compute a delta.
- Distinguish user, system and iowait time - they point at completely different causes.

## The USE method

For each resource - CPU, memory, disk, network - check:

- **Utilisation** - how busy
- **Saturation** - how much queued work
- **Errors**

Saturation is the one usually skipped and often the most informative: a disk at 60% utilisation
with a deep queue is the bottleneck, and utilisation alone would not show it.

## Idle resource investigation

When asking "why is this machine busy at idle":

1. Enumerate the processes over a threshold, with private bytes, start time and parent.
2. Identify which are **required** - and be explicit about the list.
3. For each of the rest, determine *why* it is running before touching it.
4. **Do not delete anything whose purpose is unconfirmed.** Caches that regenerate safely are
   fair game; data, volumes, credentials and project files are not.
5. Prefer the application's own mature controls (a config setting, a retention policy, a memory
   cap) over a custom resource manager.
6. Measure before and after, and verify every service still works.

> [!note] Measured in this project
> A "high idle memory" investigation resolved to an **active bulk-ingestion job** holding ~2.9 GB
> and ~184% of one core - not a leak and not idle waste. Separately, the assumption that "the
> models run remotely" was false for embeddings: local SentenceTransformers and Whisper models
> accounted for ~2.5 GB of cached weights. **Both findings came from measurement contradicting
> the mental model, which is the normal outcome.**

## Disk and I/O

- `df -h` **and** `df -i` (inodes), `du -sh */` for the largest directories.
- `iostat -x`, `iotop` for per-process I/O on Linux.
- Deleted-but-open files hold space until the holder closes them (`lsof +L1`).
- Log rotation, cache eviction and retention policies are what keep disks from filling; check
  they exist before adding capacity.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Memory Management|Memory Management]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Memory Problems|Memory Problems]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring|Monitoring]]

## Sources

- Brendan Gregg, the USE method - <https://www.brendangregg.com/usemethod.html>. OS documentation for the metric definitions. All measured examples are from this project on 2026-09-03.
