---
type: MOC
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Debugging & Problem Solving

One note per failure class, because each has its own diagnostic sequence. The general method is in the domain root.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

> [!important] Start here
> The general procedure is [[Coding Knowledge/02 - Debugging Method|Debugging Method]] in the
> domain root. This section is the specialised knowledge: what to check, in what order, for each
> class of failure.

## Method

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Systematic Debugging\|Systematic Debugging]] | Hypothesis, bisection, and the discipline that makes them work |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis\|Root Cause Analysis]] | Getting past the first plausible explanation |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Reproducible Debugging\|Reproducible Debugging]] | Making it fail on demand - the prerequisite for everything |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Reading Logs & Stack Traces\|Reading Logs & Stack Traces]] | Extracting the answer from what you already have |

## By failure class

| Note | When |
| --- | --- |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling\|Performance Profiling]] | It works, slowly |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Memory Problems\|Memory Problems]] | It grows, or it is killed |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Concurrency & Race Conditions\|Concurrency & Race Conditions]] | It fails sometimes |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Network & API Failures\|Network & API Failures]] | It cannot reach something |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Dependency & Version Conflicts\|Dependency & Version Conflicts]] | It worked yesterday, or works elsewhere |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Database Problems\|Database Problems]] | Slow queries, locks, wrong data |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Build & Deployment Failures\|Build & Deployment Failures]] | It does not build, or does not run where it was sent |
| [[Coding Knowledge/07 - Debugging & Problem Solving/Regression Investigation\|Regression Investigation]] | It used to work |

## The first four questions, for any failure

1. **What changed?** Code, data, config, dependency, environment, load, time.
2. **Has it ever worked?** If not, it is unimplemented, not broken.
3. **Am I looking at the right thing?** Right host, process, branch, container, file.
4. **Can I make it fail on demand?** Everything else depends on this.
