---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# Change Management

Making changes reviewable, traceable and reversible - which is mostly about their size and their record.

## Size is the master variable

Almost every property you want from a change follows from keeping it small:

- **Reviewable** - review quality collapses beyond a few hundred lines
- **Attributable** - a bisect lands on something comprehensible
- **Revertible** - reverting takes only the intended thing with it
- **Low risk** - a small blast radius

**One logical change per commit, one purpose per pull request.** If the description needs "and",
it is two changes.

## The discipline that most improves diffs

**Never mix a refactor with a behaviour change.** A diff where 400 lines moved and 3 lines
changed behaviour is a diff where nobody can see the 3 lines. Do the move in one commit and the
change in the next, and both become reviewable.

The same applies to reformatting: a formatting pass mixed into a fix destroys `git blame` for
that file and buries the change.

## The record

The commit message and the pull request description are the only places the reasoning survives.
The code shows what; only you know why.

Include: what was wrong, why this approach, what was considered and rejected, what is **not**
covered, and what you could not verify. That last item is not a weakness - it tells the reviewer
where to look, which is exactly what a reviewer needs.

Link to the issue, the incident or the ADR. A change traceable to its reason is a change someone
can evaluate in a year.

## Traceability

Be able to answer, at any time:

- Which commit is running in production?
- What changed between the last release and this one?
- Why was this line written this way?
- What else shipped at the same time as this incident?

That requires: version identifiers in the artefact, a tagged release, meaningful commits, and
deploy records with timestamps. It is not bureaucracy - it is what makes incident investigation
take minutes instead of hours.

## Reversibility

Design each change so undoing it is simple:

- Additive before subtractive - add the new, migrate, then remove the old in a later change
- Backwards-compatible schema changes
- Feature flags for anything risky
- Avoid changes that cannot be undone once data exists in the new shape

## Coordinating a change across components

When a change spans several, sequence so that **each intermediate state works**:

1. Deploy the consumer that tolerates both old and new
2. Deploy the producer that emits the new
3. Remove the old handling, later

Deploying both at once assumes atomic deployment, which does not exist in a rolling update.

## Emergency changes

There are real emergencies, and process should not prevent fixing production. But:

- **Still small.** An emergency is the worst time for a large change.
- **Still recorded**, even briefly.
- **Reviewed after the fact**, always.
- **Followed by the proper fix**, tracked - the emergency patch is debt, and it will otherwise
  become permanent.

## Failure modes

- **Large changes** that are approved on faith.
- **Mixed refactor and fix.**
- **Empty commit messages**, discarding the reasoning permanently.
- **Untraceable deploys** - nobody can say what is running.
- **Coordinated deploys assumed atomic.**
- **Emergency fixes never revisited.**

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Version Control|Version Control]]
- [[Coding Knowledge/09 - Engineering Practices/Release Strategy|Release Strategy]]
- [[Coding Knowledge/08 - Code Quality & Review/Code Review Principles|Code Review Principles]]

## Sources

- Practitioner synthesis. Google, *Engineering Practices* on small changes - <https://google.github.io/eng-practices/review/developer/small-cls.html> (CC BY 3.0).
