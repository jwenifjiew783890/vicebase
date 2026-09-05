---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# Refactoring

Changing structure without changing behaviour - and the discipline that keeps that promise true.

## The definition is the constraint

**Refactoring changes structure and preserves behaviour.** If behaviour changes, it is not a
refactor; it is a change, and it must be reviewed and tested as one.

The two rules that follow are the entire practice:

1. **Never mix a refactor with a behaviour change in one commit.** Doing so makes the diff
   unreviewable - nobody can tell which moved lines are the fix - and makes a revert take the fix
   with it.
2. **Refactor only under a test that would catch a behaviour change.** Without one, "preserves
   behaviour" is a hope. If tests do not exist, write characterisation tests first: capture what
   the code *currently* does, including its oddities, and pin it.

## When to refactor

- **Immediately before** a change, to make the change easy. This is the highest-value moment -
  the code's shape is fresh in mind and the benefit is realised straight away.
- **Immediately after**, to clean up what the change revealed.
- **When the third duplication appears.** Two is coincidence.
- **When you had to read it three times.** That is a measurement.

**Not** as a standalone project with no driving need. Large refactors detached from feature work
are hard to justify, hard to review, and tend to be abandoned half-done, which leaves the
codebase in two styles instead of one.

## Safe sequences

Take small steps, each of which leaves the code working, and run the tests between them.

**Extract a function**: copy the block out, parameterise what it needs, call it, run tests,
delete the original.

**Rename**: use the tool's rename, not find-and-replace. Find-and-replace catches strings,
comments and unrelated identifiers.

**Change a signature**: add the new parameter with a default, migrate callers one at a time,
remove the default.

**Replace an implementation**: build the new one beside the old, switch behind a flag, compare
outputs on real traffic if possible, remove the old.

**Split a module**: move the code first with no other change, then adjust.

**Strangler fig** for anything large: route a slice of traffic to the new implementation, grow
the slice, delete the old. Almost every successful large migration is this pattern; almost every
failed one was a big-bang rewrite.

## What justifies it

A refactor should make a *specific* future change cheaper. "It is cleaner" is not sufficient on
its own - clean is subjective and the change carries risk. Being able to say "after this, adding
a provider is one file instead of five" is.

## Failure modes

- **Refactoring without tests**, and silently changing behaviour.
- **Mixing with a fix**, making both unreviewable.
- **The big rewrite**, which underestimates the accumulated edge-case knowledge in the old code.
- **Abandoning halfway**, leaving two patterns where there was one.
- **Refactoring toward an abstraction that is wrong** - now the wrong shape is enforced.
- **Reformatting the whole file** while changing three lines, destroying `git blame` and burying
  the actual change.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Modularity & Abstraction|Modularity & Abstraction]]
- [[Coding Knowledge/08 - Code Quality & Review/Technical Debt|Technical Debt]]
- [[Coding Knowledge/10 - Engineering Experience/Safe Refactoring|Safe Refactoring]]

## Sources

- Martin Fowler, *Refactoring* (2nd ed., 2018) and the strangler fig pattern - <https://martinfowler.com/bliki/StranglerFigApplication.html>; book cited, not reproduced. Michael Feathers, *Working Effectively with Legacy Code* (2004) - characterisation tests; cited only.
