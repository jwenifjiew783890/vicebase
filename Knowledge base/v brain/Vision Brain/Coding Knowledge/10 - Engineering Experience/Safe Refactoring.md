---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Safe Refactoring

Changing structure in code you do not fully understand, without breaking it.

## The situation this addresses

Refactoring with good tests is straightforward - see
[[Coding Knowledge/08 - Code Quality & Review/Refactoring|Refactoring]]. This note is about the
harder and more common case: **code you must change, that you do not fully understand, with
tests that do not cover it.**

The instinct to rewrite is strong and usually wrong. Old code encodes edge cases nobody
remembers, and a rewrite discards them silently.

## Get a safety net first

**Characterisation tests.** Do not test what the code *should* do - capture what it *does*,
including its oddities, and pin it. Run the existing code over realistic inputs, record the
outputs, and assert on them. Now any behaviour change is visible, and you can refactor with
confidence you did not have to earn by understanding.

Where the code is too tangled to test at all, use a **seam**: find the smallest place you can
intercept - a function boundary, a parameter, a subclass - and get a test in there first. Making
the code testable is itself the first refactor, and it is done with the tiniest possible changes.

**Approval testing** works well for large outputs: capture the full output as a file, diff on
every run. Cheap and very effective for reports, generated code and serialised structures.

## Sequence

1. **Get it under test** (characterisation).
2. **Make the smallest structural change**, run tests, commit.
3. Repeat.
4. **Only then** change behaviour, as a separate commit.

Each commit leaves working code. If something breaks, the last commit is small enough to
inspect.

## Techniques for the risky cases

**Parallel run.** Build the new implementation beside the old. Run both, compare outputs on real
input, log divergences, and only switch when they agree. The most reliable technique available
for anything where correctness matters, and it is under-used because it feels like extra work -
it is far less work than an incident.

**Strangler fig.** Route a slice of traffic to the new path, grow the slice, delete the old.
Almost every successful large migration is this; almost every failed one was a big-bang rewrite.

**Branch by abstraction.** Introduce an interface over the current implementation, add a second
implementation behind it, switch with a flag. Keeps everything on the main branch and shippable.

**Expand and contract.** For any interface or schema: add the new, support both, migrate callers,
remove the old. Never remove and add in one step.

## Rules

- **Never mix structure and behaviour in one commit.**
- **Never reformat while changing** - it destroys `git blame` and buries the change.
- **Rename with the tool's rename**, not find-and-replace.
- **Keep the old code until the new one has run in production**, behind a flag if necessary.
- **Delete the old path deliberately**, as its own change. Leaving both is how a codebase ends up
  with two ways to do everything.

## When not to refactor

- The code is about to be deleted.
- It is stable, rarely touched, and works. Ugly and untouched costs nothing.
- You do not have time to do it in small steps - a rushed half-refactor is worse than none.
- You do not understand it and cannot get it under test. Add the characterisation tests first,
  as its own piece of work.

## Failure modes

- **Rewriting instead of refactoring**, discarding undocumented edge-case knowledge.
- **Refactoring without a net**, changing behaviour silently.
- **Abandoning halfway**, leaving two patterns.
- **One enormous "cleanup" commit** that cannot be reviewed or reverted.
- **Refactoring toward the wrong abstraction**, which now has to be undone as well.

---

## See also

- [[Coding Knowledge/08 - Code Quality & Review/Refactoring|Refactoring]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]
- [[Coding Knowledge/10 - Engineering Experience/Approaches That Commonly Fail|Approaches That Commonly Fail]]

## Sources

- Michael Feathers, *Working Effectively with Legacy Code* (2004) - characterisation tests and seams; cited, not reproduced. Martin Fowler, *Refactoring* (2nd ed., 2018), branch by abstraction and strangler fig - <https://martinfowler.com/bliki/BranchByAbstraction.html>.
