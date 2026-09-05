---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Postmortems

Turning an incident into a permanent improvement, which requires that people can write down what actually happened.

> [!info] Provenance
> Blameless postmortem culture, the argument that blame suppresses the information you need, and
> writing for a trigger threshold are **Google SRE**, restated in our own words. The document
> structure, the emphasis on detection time and the local practice are **our synthesis**.

## Why blameless is a mechanism, not a courtesy

If naming a cause can get someone punished, people stop naming causes. The report then describes
the sanitised version, the real cause stays in the system, and the same incident recurs.

Blameless does **not** mean nobody is responsible, and it does not mean pretending mistakes did
not happen. It means the question is always **"what made this mistake possible, and why did
nothing catch it?"** rather than "who did it".

That question is also the more productive one. A system where a routine command can destroy
production has a design problem; the person who typed it is the least interesting part of it.

## When to write one

Decide the trigger in advance — otherwise the decision is made under embarrassment, which is the
worst time. Reasonable triggers: user-visible impact beyond some threshold, data loss, a recovery
that took longer than expected, a near-miss that only luck prevented, or any failure that
surprised you.

**Near-misses deserve postmortems.** They carry the same information at a fraction of the cost,
and they are the cheapest learning available.

## What it should contain

| Section | Purpose |
| --- | --- |
| **Summary** | What happened, impact, duration — readable in thirty seconds |
| **Impact** | Who was affected, how, how many, for how long |
| **Timeline** | Timestamped: what happened, what was noticed, what was done |
| **Causes at each layer** | Trigger, mechanism, systemic and process causes |
| **What went well** | Genuinely — the things that limited the damage should be kept |
| **What went badly** | Including the things that made the response slower |
| **Where we got lucky** | The most under-used section: what would have made this far worse |
| **Actions** | Owned, tracked, each linked to a specific cause |

## The two numbers that matter most

**Time to detect** and **time to recover**. Impact is roughly duration × severity, and duration
is dominated by these two — not by how long the fix took to write.

Most incidents are worse than they needed to be because nobody knew for twenty minutes. So the
highest-value action item is usually a **detection** improvement, not a prevention one. Prevention
addresses one cause; detection shortens every future incident, including the ones you have not
imagined.

Ask explicitly: *what would have told us sooner, and why did it not exist?*

## Causes, at every layer

Stopping at the first plausible explanation produces an action item that fixes today's bug and
nothing else. Work down the layers — trigger, mechanism, systemic, process — as in
[[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]].

Do not stop at "human error", "a rare edge case", or "the library has a bug". Each of those is a
question, not an answer.

## Actions that actually happen

- **Specific and owned.** "Improve monitoring" is not an action item.
- **Prioritised against real work**, or they are decoration. An action item nobody has time for
  should be closed honestly rather than left open as a lie.
- **At least one regression test**, so this exact failure cannot return silently.
- **Bias toward detection**, per above.

The uncomfortable pattern worth naming: most incidents were **known risks that nobody had
prioritised**, and the action item often already existed as a ticket. The incident's real value
is that it converts a theoretical risk into a funded one — so write it down while that is still
true.

## Applying it here *(our synthesis)*

There is no team, no review meeting, and nobody to blame. What remains is the most valuable part:
**every failure that cost real time becomes a durable note.**

That is exactly what
[[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]] is — a
running postmortem file for this stack. Each entry records what broke, what the mechanism was,
and what the fix was, and several of them were silent failures that would certainly have recurred
otherwise.

The local version of the process is three steps:

1. When something costs more than a few minutes, write what the mechanism was.
2. Ask what would have revealed it sooner — that answer usually generates the better fix.
3. Add it to the relevant note, and add a check if one is possible.

## Failure modes

- **Blame**, after which the reports stop being accurate.
- **Written from memory** because no timeline was kept during the incident.
- **Stopping at the first cause.**
- **Action items with no owner**, which are never done.
- **No detection improvement**, so the next incident is just as slow.
- **Never read again** — a postmortem nobody revisits is a diary.
- **No postmortem for near-misses**, discarding the cheapest lessons available.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Incident Management|Incident Management]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]]
- [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]]

## Sources

- Blameless postmortem culture derived from Google, *Site Reliability Engineering* - <https://sre.google/books/> - **no reuse licence**; restated in our own words, nothing reproduced. The human-error framing is consistent with Sidney Dekker, *The Field Guide to Understanding Human Error* (cited, not reproduced). Document structure, the detection-versus-prevention argument and the local practice are our synthesis.
