---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Evaluation Loops

Continuously measuring whether the agent is getting better, as opposed to feeling like it is.

## Why agents need this more than most software

An agent's failures are usually **silent and plausible**: it completes a task the wrong way, or
answers confidently from nothing, and reports success. Ordinary software crashes; an agent
returns a paragraph. Without measurement, quality drifts invisibly and every change is a guess.

## What to measure

| Dimension | Metric |
| --- | --- |
| **Outcome** | Task completed correctly - the only metric that ultimately matters |
| **Process** | Steps taken, tools chosen, retries, replans |
| **Cost** | Tokens, model calls, wall-clock time per task |
| **Safety** | Attempts outside permitted scope, destructive actions, confirmations required |
| **Recovery** | Behaviour when a step fails - did it recover, stop cleanly, or fabricate? |

Process metrics matter more than they do for ordinary software, because an agent that gets the
right answer via twelve unnecessary tool calls is one input away from getting the wrong one.

## Building the harness

1. **Fixed task set** - 20-50 real tasks with verifiable outcomes. Real, not imagined.
2. **Deterministic verification wherever possible** - did the file change correctly, does the
   code compile, does the test pass, is the cited note real. This is far more reliable than a
   model judging quality.
3. **Run several times per task.** Agents are stochastic; one run is an anecdote. Report the
   distribution, including the worst case.
4. **Record the trace**, not just the outcome - which tools, which arguments, which errors. When
   a task regresses, the trace explains it.
5. **Gate changes on it.** Prompt, model, tool and retrieval changes all run the suite first.

## Regression cases are the highest-value part

Every real failure becomes a permanent case. This turns debugging into accumulated value: the
suite grows to encode exactly the ways this system has actually failed, which is a far better
predictor of future failure than any set of imagined tests.

## Production signals

Offline sets miss what real use finds. Track: user corrections and re-prompts, abandonment,
escalation to a human, retries, task duration, and cost per task. A rise in re-prompts is a
quality regression even when every offline metric held.

## Failure modes

- **No harness.** Every "this is better now" is unfalsifiable.
- **Measuring only success rate**, so a 3x cost increase for +2% passes unnoticed.
- **A single run per task**, mistaking variance for change.
- **Evaluating only the happy path**, so recovery behaviour is never tested.
- **Model-judged everything**, when deterministic checks were available.
- **A suite that is never updated**, so it tests a version of the task that no longer matters.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Evaluation|Evaluation]]
- [[Coding Knowledge/04 - Agent Engineering/Feedback Loops|Feedback Loops]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]

## Sources

- Practitioner synthesis. Related published work: agent benchmark methodology in SWE-bench - <https://www.swebench.com/> and tau-bench - <https://arxiv.org/abs/2406.12045>.
