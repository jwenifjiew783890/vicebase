---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Maintainability

Whether the next person - possibly you, possibly an agent - can change this safely without reconstructing the author's mental model.

## What maintainability actually is

Not "clean code" as an aesthetic. It is the **cost of the next change**, and it has three
components: how long it takes to *understand* what is there, how confident you can be that a
change is *safe*, and how long the *feedback loop* is between making a change and knowing.

Optimise those three and the code will look fine as a side effect. Optimise appearance and the
three may not improve at all.

## What actually reduces the cost

**Names that carry meaning.** The single highest-leverage thing. `retry_after_seconds` beats
`t`. A boolean called `disable_ssl_verify_off` will cause an outage.

**Comments that explain why.** The code already says what. Comments earn their place by
recording the reason, the alternative rejected, the constraint that is not visible locally, or
the bug this line prevents. A comment that restates the line below is worse than none - it will
drift and then lie.

**Small, honest functions.** Small because a reader holds a limited amount at once, not because
of a line count rule. A 60-line function with one job beats six 10-line functions that must be
read together.

**Local reasoning.** Can this function be understood from itself, its arguments, and its
callees' names? Every global, every implicit ordering, every action-at-a-distance breaks that.

**Consistency.** The same problem solved the same way throughout. Two idioms for error handling
in one codebase doubles what a reader must know.

**Tests that state intent.** A well-named test is documentation that cannot go stale, and the
safety net that makes change possible at all.

**Deletion.** Dead code, unused flags, abandoned experiments and commented-out blocks all cost
attention and none pay rent. Version control is the archive; delete it.

## What quietly destroys it

| Cause | Symptom |
| --- | --- |
| Hidden state | "It works the second time you run it" |
| Boolean parameters | `render(true, false, true)` at every call site |
| Deep inheritance | Understanding a method requires four files |
| Copy-paste divergence | Five near-identical blocks, three of them fixed |
| Config sprawl | Nobody knows which of four files is authoritative |
| Stale comments and docs | Readers learn to ignore all of them |
| No tests on the risky part | Every change is a gamble, so nobody changes it |
| Clever one-liners | Correct, unreadable, and unmodifiable |

## Complexity is incremental

Systems do not become unmaintainable in one decision. They get there through many small,
individually-defensible compromises - each one "just this once". The defence is to treat
**every** change as either reducing complexity or paying for the increase explicitly.

## The practical checks

Before finishing a change, ask:

- Could someone unfamiliar with this change understand it from the diff and the description?
- If this is wrong, how would anyone find out? Is there a test, a log line, an alert?
- Did I leave anything behind that is now unused?
- Is there now more than one way to do this in the codebase?
- Would reverting this be simple?

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Modularity & Abstraction|Modularity & Abstraction]]
- [[Coding Knowledge/01 - Software Engineering/Documentation|Documentation]]
- [[Coding Knowledge/08 - Code Quality & Review/Technical Debt|Technical Debt]]
- [[Coding Knowledge/08 - Code Quality & Review/Refactoring|Refactoring]]

## Sources

- John Ousterhout, *A Philosophy of Software Design* (2018) - complexity as incremental accumulation; cited, not reproduced. Kernighan & Pike, *The Practice of Programming* (1999) - cited, not reproduced. Google, *Engineering Practices* - <https://google.github.io/eng-practices/> (CC BY 3.0).
