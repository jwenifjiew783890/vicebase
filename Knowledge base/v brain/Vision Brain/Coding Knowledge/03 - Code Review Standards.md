---
type: note
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Code Review Standards

What a review is for, what blocks a change, and what does not. Applies both when reviewing and when writing code that will be reviewed.

## The standard

**A change should be approved when it definitely improves the overall health of the codebase,
even if it is not perfect.** Perfection is not the bar; continuous improvement is. A reviewer
who blocks a genuine improvement over stylistic preference is making the codebase worse by
slowing it down, and one who waves through a structural mistake is making it worse directly.

This is Google's published standard and it is adopted here deliberately, because it settles the
argument that otherwise consumes reviews.

## Order of attention

Review in this order and stop escalating once something blocking is found - a design flaw makes
comments on naming irrelevant.

1. **Design** - does this change belong here at all? Is it in the right layer? Does it duplicate
   something that exists?
2. **Correctness** - does it do what it claims, including at the edges: empty, zero, one, huge,
   unicode, concurrent, retried, interrupted?
3. **Security and data safety** - untrusted input, authz on the write path, secrets, injection,
   destructive operations without a guard.
4. **Failure behaviour** - what happens when the dependency is down, slow, or returns garbage?
   Is the error actionable?
5. **Tests** - do they test behaviour rather than implementation? Would they fail if the change
   were reverted?
6. **Naming and clarity** - will the next reader understand this without the author present?
7. **Comments** - do they explain *why*, not restate *what*?
8. **Style** - last, and mostly the linter's job.

## What blocks a change

- It is incorrect, or unsafe, or loses data.
- It introduces a security hole or an unbounded resource.
- It cannot be understood well enough to be maintained.
- It has no test for behaviour that could regress silently.
- It bundles an unrelated change that hides the real one.

## What does not block

- A different-but-equivalent approach the reviewer prefers.
- Style the linter accepts.
- A pre-existing problem the change did not introduce (raise it separately -
  see [[Coding Knowledge/08 - Code Quality & Review/Technical Debt|Technical Debt]]).
- Perfection of a thing that is already better than what it replaces.

## How to write review comments

- **Be specific and give the reason.** "This drops the exception, so a failed write looks like
  a success" beats "handle errors properly".
- **Distinguish severity.** Mark non-blocking suggestions as such - `nit:`, `optional:`,
  `question:` - so the author knows what actually gates the merge.
- **Ask, when you might be wrong.** "What happens if `items` is empty here?" invites the
  author's knowledge; "this breaks on empty input" invites a defence.
- **Comment on the code, never the coder.** "This function does X" not "you always do X".

## For the author

- **Explain the why in the description**, including what you considered and rejected. The diff
  shows what; only you know why.
- **Keep changes small and single-purpose.** Review quality falls off a cliff with size.
- **Review your own diff first.** Half of what a reviewer would find is visible on a second
  read.
- **Say what is untested.** Naming the gap is respected; hiding it is not.
- **Disagreement is technical, not personal.** Explain the reasoning; if it does not convince,
  the reviewer is the check that exists for a reason.

## Reviewing AI-written code specifically

Machine-generated changes fail differently from human ones, so weight the review differently:

- **Plausible-but-absent APIs.** Confirm every called function, flag and parameter actually
  exists in the version in use. This is the single most common defect.
- **Silent scope creep.** Reformatting, renames and "improvements" mixed into a small fix.
- **Invented tests.** Tests that assert the implementation rather than the requirement, or that
  pass without exercising the change. Check that reverting the change fails the test.
- **Confident narration.** A report saying tests pass is not evidence that tests were run.
- **Error handling that only looks careful.** `try/except` around everything, logging nothing,
  returning a default that hides the failure.

---

## See also

- [[Coding Knowledge/08 - Code Quality & Review/00 - Code Quality & Review|Code Quality & Review]]
- [[Coding Knowledge/08 - Code Quality & Review/Code Review Principles|Code Review Principles]]
- [[Coding Knowledge/08 - Code Quality & Review/Security Review|Security Review]]

## Sources

- Google, *How to do a code review* and *The Standard of Code Review* - <https://google.github.io/eng-practices/review/> - licensed CC BY 3.0 (licence verified 2026-09-03). The "improves the overall health of the codebase" standard is theirs, restated here with attribution. The AI-review section is practitioner judgement from this project, not from that source.
