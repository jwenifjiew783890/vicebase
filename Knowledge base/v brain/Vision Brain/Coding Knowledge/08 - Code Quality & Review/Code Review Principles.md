---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# Code Review Principles

The practice of reviewing: what to look for that tools cannot, and how to make the comment land.

## What a human review is uniquely for

Linters catch style. Type checkers catch shapes. Tests catch regressions in what they cover. A
human review exists for what none of those can see:

- **Is this the right thing to build at all?**
- **Does it belong here**, in this layer, in this module?
- **What happens at the edges** the tests do not cover?
- **What does the next person need to know** that is not written down?
- **Does it duplicate something that already exists?**

If a review is spending its time on formatting, the tooling is missing and the review is being
wasted.

## Reviewing effectively

**Read the description first.** What is this trying to do? A diff without that context is
reviewed for local correctness only, which misses the important problems.

**Read the whole change before commenting.** A comment on line 20 is often answered on line 200.

**Trace one path end to end** rather than reading top to bottom. Follow a request, a value, or a
failure through the change.

**Ask about the edges explicitly.** Empty, null, huge, concurrent, retried, interrupted,
malicious. This is where a reviewer earns their place.

**Check the tests against the requirement**, not against the implementation. Would they fail if
the change were reverted?

**Look for what is not there.** No error handling on the new network call. No index on the new
foreign key. No migration for the new column. Absences are invisible in a diff and are frequently
the real defect.

**Time-box it.** Review quality collapses after about an hour, and on changes beyond a few
hundred lines. If a change is too big to review well, saying so *is* the review.

## Comments that work

- **State the problem and its consequence.** "This drops the exception, so a failed write looks
  like a success."
- **Mark severity.** `nit:`, `question:`, `suggestion:`, or nothing for blocking. Without this
  the author cannot tell what gates the merge, and either over- or under-reacts.
- **Ask when uncertain.** "What happens if `items` is empty?" gets an answer; "this breaks on
  empty" gets a defence.
- **Offer the alternative** when you have one. Criticism without a direction is expensive for
  the author.
- **Praise the good decision** occasionally and specifically. It calibrates what "good" means
  here far better than a style guide.
- **Never about the person.** "This function" not "you".

## Being reviewed

- **Write the description you would want to receive**: what, why, what was considered and
  rejected, what is untested, what you are unsure about.
- **Keep it small and single-purpose.**
- **Self-review the diff first.** You will find half of what the reviewer would.
- **Flag your own uncertainty.** Pointing at the risky part directs attention where it is worth
  most.
- **Respond to every comment**, even to disagree. An ignored comment is how a reviewer learns
  reviewing is pointless.
- **Disagreement is fine and technical.** Explain the reasoning; if it does not convince the
  reviewer, that is the check working.

## Failure modes

| Anti-pattern | Effect |
| --- | --- |
| Rubber stamp | The review provides no value; everyone learns to skip it |
| Nitpick storm | Real problems buried under preferences |
| Blocking on personal taste | Slows the codebase's improvement |
| Reviewing only the diff | Misses the context that makes it wrong |
| Enormous changes | Unreviewable; approved on faith |
| Silence on a bad design | The most expensive omission in the list |

---

## See also

- [[Coding Knowledge/03 - Code Review Standards|Code Review Standards]]
- [[Coding Knowledge/08 - Code Quality & Review/Security Review|Security Review]]
- [[Coding Knowledge/08 - Code Quality & Review/Architecture Review|Architecture Review]]

## Sources

- Google, *Engineering Practices* - <https://google.github.io/eng-practices/review/> (CC BY 3.0, verified 2026-09-03; synthesised with attribution).
