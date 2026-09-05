---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Modularity & Abstraction

Where to put the seams, how much to hide behind them, and how to tell a good abstraction from an expensive one.

## The measure of a module

A good module is one where **the interface is much smaller than the implementation**. That ratio
is the whole point: callers carry a little knowledge, the module carries a lot. A module whose
interface is nearly as complex as its internals has added a file and bought nothing - "a
shallow module", in Ousterhout's phrasing.

Prefer **fewer, deeper modules** to many thin ones. Splitting a 300-line function into fifteen
20-line functions that each need the others' context has moved the complexity into the call
graph, where it is harder to see.

## Information hiding

The purpose of a boundary is to let the inside change without the outside noticing. So hide:

- the storage format and the schema
- the algorithm and its complexity
- the concurrency strategy
- whether an operation is local or remote *only if the failure model is genuinely equivalent* -
  otherwise this is a leaky abstraction and callers must know

**Information leakage** is the same design knowledge appearing in two modules. If changing a
file format means editing both the reader and an unrelated validator, the format leaked.

## Rules for drawing boundaries

1. **Split by what changes together**, not by technical layer. "All the models / all the views"
   guarantees that every feature change touches every folder.
2. **A boundary should reduce, not relay.** If a layer only forwards calls, delete it.
3. **Dependencies point toward stability.** Volatile things (UI, adapters, vendors) depend on
   stable things (domain rules), never the reverse.
4. **No cycles.** A dependency cycle means the two modules are one module with extra ceremony.
5. **One owner per piece of data.** Two components writing the same row is not modularity.

## When abstraction is worth it

Abstract when there is **real, present variation** or a **real, present need to substitute**
(a test double, a second vendor, a second backend). Do not abstract for imagined future
variation - the guess is usually wrong, and the wrong abstraction is more expensive than
duplication, because duplication is easy to see and easy to delete.

> Practitioner rule: **duplicate twice, abstract on the third.** Two similar things are often
> coincidence; three is a pattern.

## Signs an abstraction is wrong

- Callers routinely need to bypass it, or reach through it to the thing behind.
- Every new case needs a new flag or a new parameter on the interface.
- The interface has an argument that only one implementation uses.
- The name is a category, not a role: `Manager`, `Helper`, `Utils`, `Processor`.
- Understanding a caller requires reading the implementation anyway.

When these appear, the correct move is often to **inline the abstraction back** and re-derive
the boundary from what the code actually does now.

## Coupling ranked, worst to best

1. Shared mutable global state
2. Shared database tables written by both sides
3. Shared internal representation (one module reaching into another's structure)
4. Shared schema with an owner and a version
5. A published interface
6. Data passed as arguments and returned as values

Move down this list whenever a change is expensive.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Architecture Fundamentals|Architecture Fundamentals]]
- [[Coding Knowledge/01 - Software Engineering/Maintainability|Maintainability]]
- [[Coding Knowledge/08 - Code Quality & Review/Refactoring|Refactoring]]

## Sources

- John Ousterhout, *A Philosophy of Software Design* (2018) - the deep/shallow module framing and "information leakage" are his; cited, not reproduced. David Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules" (1972). Sandi Metz on duplication vs the wrong abstraction - <https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction>.
