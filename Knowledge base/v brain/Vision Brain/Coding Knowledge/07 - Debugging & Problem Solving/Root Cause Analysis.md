---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Root Cause Analysis

Getting past the first plausible explanation to the one that, if fixed, prevents recurrence.

## What "root cause" means

The cause you can fix such that **this class of failure does not happen again**. Not the trigger,
not the last thing that changed, and not "human error".

There is usually more than one, at different levels. A useful analysis names all of them and
decides which are worth fixing.

## The layers

Take a real example: an agent returned a document made entirely of placeholders while every step
reported success.

| Layer | Cause | Fix |
| --- | --- | --- |
| **Symptom** | Output was placeholder text | - |
| **Proximate** | Stage 2 received empty context | Pass the value |
| **Mechanism** | Chained data was never supplied to the next stage | Supply it structurally in the executor |
| **Systemic** | A stage producing nothing was treated as success | Assert on output content, not on absence of error |
| **Process** | Nothing verified the output before it was reported | Add a real-execution check to the acceptance criteria |

Fixing only the proximate cause fixes today's bug. Fixing the systemic one prevents the next
five, which will otherwise arrive wearing different symptoms.

## Techniques

**Five whys**, with a caveat. Ask "why" repeatedly - but it produces a single chain, and real
failures are usually a *conjunction* of several conditions. Use it to go deeper, not to conclude
there was one cause.

**Causal chain / fault tree.** Map every condition that had to hold. Then ask which single one,
removed, would have prevented it. Often the cheapest fix is not on the obvious path.

**Change analysis.** What was different between working and failing? Not just code: data,
configuration, dependency versions, load, time of day, who ran it, which machine.

**Barrier analysis.** What *should* have caught this and did not? A missing type, an absent test,
an alert not configured, a review that did not look. The absent barrier is frequently the most
valuable finding.

## Stopping conditions

Stop when the cause is **actionable and general**. Going further reaches "the requirements were
ambiguous" and eventually "software is hard", which are true and useless.

Do not stop at:
- **"Human error"** - ask why the system permitted it, and why it was easy to do.
- **"A rare edge case"** - it happened, so it is not rare enough.
- **"The library has a bug"** - possibly, but why did nothing catch it here?
- **"It works now"** - if you cannot say why it broke, you cannot say it is fixed.

## Confirming

A cause is confirmed when you can **make the failure appear and disappear on demand** by
manipulating that cause. That is the whole test, and it is what separates a cause from a
correlation.

If reverting the fix does not bring the failure back, you have not found it.

## Writing it down

For anything that cost real time, record: what happened, the timeline, the causes at each layer,
what was fixed, what was deliberately not fixed, and **how it would be detected faster next
time**. Blameless - the goal is the system's behaviour, not the person's.

The detection question is usually the most valuable output. Most incidents are worse than they
needed to be because nobody knew for twenty minutes.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Postmortems|Postmortems]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Systematic Debugging|Systematic Debugging]]
- [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]
- [[Coding Knowledge/10 - Engineering Experience/Common Failure Patterns|Common Failure Patterns]]

## Sources

- Google, *Site Reliability Engineering*, postmortem culture chapter - <https://sre.google/books/> (cited only). Sidney Dekker, *The Field Guide to Understanding Human Error* - cited, not reproduced. The worked example is from this project.
