---
type: note
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Debugging Method

The default procedure when something is broken and the cause is not yet known. It is a loop, and the discipline is in not skipping steps.

> [!important] The single rule that matters most
> **Do not change anything until you can state what you expect the change to prove.**
> Changing code to see what happens is not debugging; it is shuffling. Every edit made without
> a prediction destroys evidence and adds a variable.

## The loop

**1 - Reproduce.** A bug you cannot trigger on demand cannot be verified as fixed. Get to the
smallest, fastest, most reliable reproduction available. If it only happens sometimes, that is
itself the first finding - see
[[Coding Knowledge/07 - Debugging & Problem Solving/Concurrency & Race Conditions|Concurrency & Race Conditions]].

**2 - Read the actual error.** All of it. The top frame is where it surfaced; the cause is
usually further down, and in a chained exception it is under `caused by` / `during handling of
the above`. Most wasted debugging time is spent solving a symptom named in line one while the
answer sat in line forty.

**3 - State the expectation.** Write down what the system *should* do at the failing point,
concretely: "after this call `rows` should be a list of 12 dicts." A bug is a divergence
between belief and reality, and you cannot find the divergence without stating the belief.

**4 - Bisect the distance between belief and reality.** Halve the search space each time, along
whichever axis is cheapest to split:
- *In space* - is the value correct at the midpoint of the pipeline?
- *In time* - `git bisect` between a known-good and known-bad commit.
- *In configuration* - remove components until it stops failing.
- *In data* - shrink the input until it stops failing; the last removal is the trigger.

**5 - Find the mechanism, not the correlation.** "It works when I add a sleep" is a
correlation. The mechanism is *why* the delay matters. Stop at correlation and you have a
change that will fail again on faster hardware.

**6 - Fix the cause and prove it.** Make the change, then demonstrate the reproduction now
passes **and** that reverting the change brings the failure back. That second half is the step
almost everyone skips, and it is the only thing separating a fix from a coincidence.

**7 - Ask where else this lives.** The same mistake is rarely unique. Grep for the pattern.

**8 - Leave a regression test and a note.** A bug without a test will return.

## Diagnostic ordering

When several hypotheses are open, test them in order of **cost to test**, not in order of
likelihood. A five-second check that eliminates a possibility beats a twenty-minute
investigation of a more probable one.

## The questions that unstick a stalled investigation

- What changed? Code, data, config, dependency, environment, load, time - something did.
- Has this ever worked? If not, it is not a regression, it is an unimplemented case.
- Am I debugging the thing I think I am? Confirm you are hitting the process, host, container,
  branch and file you believe you are. This is a top cause of hours lost.
- Is the error even reaching me? A swallowed exception or a filtered log level can make a loud
  failure look like a silent one.
- What does the system *say* it is doing? Logs, metrics, traces, `ps`, `netstat`, the DB.
- Can I make it fail faster? Reproduction speed is the multiplier on every later step.

## When to stop and change tactics

If three hypotheses in a row have been wrong, the model of the system is wrong, not the
hypotheses. Stop generating theories and go gather description: read the code path
end to end, print the actual values, check the versions actually loaded.

> [!tip] Explain it out loud
> Stating the problem in full sentences to another person - or to nobody - resolves a large
> share of bugs before the listener answers, because the explanation forces the assumption into
> the open.

## Anti-patterns

| Anti-pattern | Why it costs |
| --- | --- |
| Changing several things at once | You lose which one mattered, and inherit any new bugs |
| Fixing the symptom | The cause resurfaces elsewhere, now with a confusing workaround in place |
| "It's probably a caching issue" | An untested guess that stops investigation |
| Trusting the comment over the code | Comments drift; the code is what ran |
| Blaming the compiler, kernel or library first | Occasionally right, usually a detour; suspect your own code first |
| Debugging by rebuilding | Sometimes it works, and teaches nothing about what happened |

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/00 - Debugging & Problem Solving|Debugging & Problem Solving]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reproducible Debugging|Reproducible Debugging]]
- [[Coding Knowledge/10 - Engineering Experience/Troubleshooting Checklists|Troubleshooting Checklists]]

## Sources

- Method is the common core of: Andreas Zeller, *Why Programs Fail* (2nd ed., 2009) - cited, not reproduced; Brian Kernighan & Rob Pike, *The Practice of Programming* (1999), ch. 5 - cited, not reproduced; David Agans, *Debugging: The 9 Indispensable Rules* (2002) - cited, not reproduced; `git bisect` documentation - <https://git-scm.com/docs/git-bisect>.
