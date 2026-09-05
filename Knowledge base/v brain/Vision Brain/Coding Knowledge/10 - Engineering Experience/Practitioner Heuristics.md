---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Practitioner Heuristics

Rules of thumb that are usually right, with the conditions under which they are not.

> [!note] These are heuristics
> Each is a default that saves thinking in the common case. Each has exceptions, and the
> exceptions are named.

## On diagnosis

**It is usually your code.** Suspect the compiler, kernel or library last. *Exception: after a
dependency upgrade, suspect the dependency first.*

**"Nothing changed" is almost always false.** Something changed - code, data, config, a
dependency, load, or a date passing. Certificates and tokens expire without anyone acting.

**The bug is where you have not looked**, which is usually the code you are confident about.

**If it worked five minutes ago, bisect.** The history holds the answer and bisection finds it
mechanically.

**Intermittent means timing** - concurrency, a timeout, or a scheduled boundary - until proven
otherwise.

**Check that you are debugging the thing you think you are** before anything clever. Right host,
right process, right branch, right container, right file. This costs thirty seconds and
regularly saves hours.

**When three hypotheses in a row are wrong, your model is wrong.** Stop theorising and go read
the code path end to end.

**The error message is usually accurate and usually skimmed.** Read all of it, literally.

## On writing code

**Make it work, then make it right, then make it fast** - and only make it fast if measurement
says so.

**Duplicate twice, abstract on the third.** The wrong abstraction costs more than duplication,
because duplication is visible and deletable.

**If it needs a comment to explain what it does, rewrite it. If it needs one to explain why,
write the comment.**

**Prefer boring technology.** Novelty spends a limited budget; spend it where it differentiates.

**The best code is deleted code.** Every line is a permanent obligation.

**When stuck on a design, write the calling code first.** The interface you *want* usually
reveals the design.

**If you cannot test it, the design is probably wrong.** Difficulty testing is a design signal,
not a testing problem.

## On systems

**Everything fails; design for what happens then.** The question is never whether.

**Anything unbounded will eventually be unbounded** - a queue, a cache, a log, a table, a retry.

**Retries need backoff and jitter, or they amplify the outage they were meant to survive.**

**If it is not monitored, it is not running** - you simply do not know yet.

**The database is usually the bottleneck.** Look there before rewriting application code.

**Latency you cannot see is still latency.** Queue time before your handler is real to the user.

## On process

**Small changes.** Almost every desirable property follows from this one.

**If it is not in version control, it does not exist.**

**A backup that has never been restored is not a backup.**

**Automate the third time.** Once is fine, twice is tolerable, three times means it will happen
forever.

**Write down the decision, not just the outcome** - the reasoning is what cannot be recovered
later.

**Do not deploy before you leave.** The code is no riskier; your response time is much worse.

## On working with uncertainty

**Say what you did not verify.** An admitted gap is useful information; an unfounded claim of
verification removes the reader's reason to check, which is worse than no claim at all.

**When you disagree with a constraint, say so once and then work within it.** Re-litigating a
settled decision mid-task wastes the time the decision was meant to save.

**Prefer the reversible option** when genuinely unsure. You can learn from a reversible mistake.

---

## See also

- [[Coding Knowledge/01 - Engineering Principles|Engineering Principles]]
- [[Coding Knowledge/10 - Engineering Experience/Troubleshooting Checklists|Troubleshooting Checklists]]
- [[Coding Knowledge/10 - Engineering Experience/Engineering Trade-offs|Engineering Trade-offs]]

## Sources

- Practitioner judgement, widely held rather than attributable to one source. Some have canonical formulations: Kent Beck ("make it work, make it right, make it fast"); Dan McKinley, "Choose Boring Technology" - <https://boringtechnology.club/>; Sandi Metz on duplication vs the wrong abstraction - <https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction>.
