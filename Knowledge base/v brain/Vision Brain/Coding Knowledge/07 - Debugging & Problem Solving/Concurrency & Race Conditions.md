---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Concurrency & Race Conditions

The bugs that appear sometimes. Ordinary debugging fails here, so the techniques are different.

## Why the usual approach fails

These bugs are **non-deterministic** and **observation-sensitive**. Adding a print statement or
attaching a debugger changes the timing and often makes the bug disappear - the classic
heisenbug. So the method shifts from *observe the failure* to **reason about the interleaving and
then prove it**.

## Recognising one

Suspect concurrency when:

- It fails intermittently, without an input change
- It fails more under load, or on a machine with more cores
- It fails in CI and not locally (or the reverse)
- Adding logging or a delay changes or hides it
- The data is *sometimes* wrong rather than always
- A counter, balance or list is occasionally short
- It only happens on retry, restart, or during shutdown

## The classes

**Data race** - two threads access the same memory, at least one writes, with no synchronisation.
Not merely "unordered": the compiler and CPU may reorder and cache such that **no interleaving of
the source code explains the observed result**. Undefined behaviour in C/C++.

**Race condition without a data race** - check-then-act, read-modify-write. Each individual
operation is correctly locked; the *pair* is not atomic. `if not exists: create` executed by two
threads creates two.

**Deadlock** - locks acquired in opposite orders. Everything stops.

**Livelock** - threads active, no progress, typically from mutual back-off.

**Starvation** - one participant never scheduled.

**Lost update** - two read-modify-write sequences; one overwrites the other.

**Order violation** - operation B depends on A having completed, and nothing enforces it. Common
in initialisation and shutdown.

**ABA** - a value changes from A to B and back; a compare-and-swap sees "unchanged" and is
wrong.

## Finding them

**Tools first** - they are far more effective than reasoning alone:

| Environment | Tool |
| --- | --- |
| C/C++/Go | ThreadSanitizer (`-fsanitize=thread`, `go test -race`) |
| Java | Java Flight Recorder, jcmd thread dumps, FindBugs concurrency checks |
| Python | Faulthandler, `py-spy dump` for stuck threads |
| Any | Stress testing with high concurrency; artificial delays at suspect points |

**Deliberately perturb timing.** Insert randomised delays at the points you suspect. If a delay
between the check and the act makes it reproducible, you have found the window.

**Increase concurrency and reduce work per operation.** More threads doing shorter operations
widens the window in which a race can be observed.

**Read the code as an adversary**: assume a context switch between *every pair of instructions*
and ask what breaks. For shared state, ask "what if another thread runs completely between these
two lines?"

**Thread dumps for deadlock.** A dump showing thread A holding lock 1 waiting for 2, and B
holding 2 waiting for 1, is a complete diagnosis in one artefact. Get a dump before restarting -
restarting destroys the only evidence.

## Fixing

In order of preference:

1. **Remove the sharing.** Immutable data, message passing, thread-local state. This eliminates
   the class rather than managing it.
2. **Make the whole compound operation atomic** - a single lock over check-and-act, a database
   `UPDATE ... WHERE`, a compare-and-swap, an upsert with a unique constraint.
3. **Use a higher-level primitive** - a concurrent collection, a queue, a channel - rather than
   raw locks.
4. **Consistent lock ordering** to prevent deadlock, with a documented hierarchy.
5. **Never hold a lock across a network call or an `await`.**

> [!warning] Do not "fix" it with a sleep
> A delay that makes the symptom go away has not removed the race; it has narrowed the window.
> It will fail again on different hardware, under load, or at the worst possible moment - and by
> then the sleep will look intentional.

## Verifying the fix

A single passing run proves nothing. Run the reproduction many times, under load, with the race
detector enabled, ideally on a machine with more cores than the one where it failed. Absence of
the symptom in ten runs is weak evidence; a race detector reporting clean is strong evidence.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Async & Concurrency|Async & Concurrency]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reproducible Debugging|Reproducible Debugging]]
- [[Coding Knowledge/02 - Programming & Languages/C and C++|C and C++]]

## Sources

- ThreadSanitizer documentation - <https://clang.llvm.org/docs/ThreadSanitizer.html>; Go race detector - <https://go.dev/doc/articles/race_detector>; Lu et al., "Learning from Mistakes: A Comprehensive Study on Real World Concurrency Bug Characteristics" (ASPLOS 2008) for the bug taxonomy.
