---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# Requirements Analysis

Finding out what is actually needed, which is rarely what was first asked for and rarely what you assumed.

## The gap

A request is a proposed solution. Behind it is a problem, and behind that a goal. Building the
request exactly, without understanding the problem, produces software that technically satisfies
and does not help.

But the opposite failure is just as real: **reinterpreting the request into what you would rather
build**. The discipline is to understand the problem *and* deliver the thing asked for, raising
the concern rather than silently substituting your own scope.

## Questions that find the real requirement

- **What are you doing today?** The current workaround reveals the actual need better than any
  description of the desired feature.
- **What happens if this does not exist?** Separates essential from pleasant.
- **Who uses this, how often, and in what situation?** A thing used daily under pressure has
  different requirements from a thing used monthly at leisure.
- **What does success look like, measurably?**
- **What is explicitly out of scope?** Naming this early prevents most of the later argument.
- **What must remain true?** Constraints - compliance, budget, existing systems, deadlines.
- **What is the volume, now and expected?** Ten, ten thousand, ten million. This single number
  changes the design more than anything else.

## The parts that are always underspecified

Ask about these explicitly, every time. They are where the late surprises come from:

- **Errors** - what should happen when it fails? What does the user see? Who is told?
- **Empty state** - what is shown when there is nothing yet?
- **Scale** - how much data, how many users, how fast growing?
- **Permissions** - who may see it, who may change it?
- **Concurrency** - what if two people do this simultaneously?
- **History** - is an audit trail needed? Can things be undone?
- **Lifecycle** - how does something get deleted, archived, expired?
- **Migration** - what happens to the data that already exists?

## Writing it down usefully

Express requirements as **observable behaviour with acceptance criteria**, not as
implementation. "A user with an expired subscription sees a renewal prompt instead of the
dashboard, and their data remains intact for 30 days" can be verified. "Handle expired
subscriptions properly" cannot.

Separate:
- **Must** - the change is not useful without it
- **Should** - significant value, could ship after
- **Could** - if it is nearly free
- **Won't** - explicitly out of scope, recorded so it is not silently reintroduced

## Handling ambiguity

Do the parts that do not depend on the answer first. For the parts that do: **state the
assumption explicitly and proceed**, rather than blocking, unless proceeding under any
assumption would be unsafe or would waste the work if wrong.

An assumption written down is cheap to correct. An assumption made silently is discovered at
review, or in production.

## Failure modes

- **Building the request rather than solving the problem.**
- **Building the imagined problem** rather than the request, without saying so.
- **Requirements as implementation** - "add a Redis cache" instead of "the dashboard must load
  in under a second".
- **No acceptance criteria**, so "done" is a matter of opinion.
- **Scope discovered incrementally** because the underspecified parts were never asked about.
- **The edge cases deferred**, then found to be most of the work.

---

## See also

- [[Coding Knowledge/09 - Engineering Practices/System Design|System Design]]
- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]

## Sources

- Practitioner synthesis. MoSCoW prioritisation is standard practice. Gojko Adzic, *Specification by Example* (2011) for acceptance criteria - cited, not reproduced.
