---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Toil

Operational work that should not exist: how to recognise it, and why it is worth a rule rather than good intentions.

> [!info] Provenance
> The definition of toil and the argument for capping it are **Google SRE**, restated in our own
> words. The identification checklist, the ranking method and the local examples are **our
> synthesis**.

## The definition, and why it is narrow

Toil is operational work with a specific set of properties. It is:

- **manual** — a human performs it
- **repetitive** — it has been done before and will be again
- **automatable** — a machine could do it, in principle
- **tactical** — reactive and interrupt-driven rather than planned
- **devoid of enduring value** — the service is in the same state afterwards as before
- **linear in service growth** — twice the traffic, twice the work

The narrowness is deliberate. Plenty of unglamorous work is **not** toil: writing a
postmortem produces enduring value; a one-off migration is not repetitive; investigating a novel
failure is not automatable. Calling all unpleasant work "toil" makes the term useless, in the
same way that calling all disliked code "technical debt" does.

## Why it is capped rather than merely discouraged

Toil grows with the service, and it crowds out exactly the engineering that would reduce it.
Left alone the loop is self-reinforcing: more toil leaves less time to automate, which produces
more toil. Google's response is a **hard cap on the proportion of time spent on it**, with the
remainder protected for engineering — the specific figure matters less than the fact that it is
a limit rather than an intention.

The transferable principle: **an intention to automate loses to an urgent manual task every
time. A limit does not.**

## Recognising it

Ask of any recurring operational task:

1. Have I done this before, and will I do it again?
2. Could a script do it, if I wrote the script?
3. Does the system end up in the same state it was in before?
4. Does the work grow as usage grows?
5. Did an alert or a person interrupt me to do it?

Three or more yeses means it is toil, and it should be on a list.

## Deciding what to eliminate first

Rank by **total time consumed**, not by how annoying each instance is. A two-minute task done
daily costs more than a one-hour task done quarterly, and the two-minute one is the one nobody
proposes automating.

Then, in order of cost to fix:

1. **Delete it.** Is it needed at all? A surprising share of recurring operational work is
   maintaining something nobody uses.
2. **Fix the cause.** A restart performed weekly is a memory leak nobody has diagnosed. The
   restart is the symptom; automating the restart makes the leak permanent.
3. **Make it self-service** so it does not require you specifically.
4. **Automate it**, with the automation itself monitored — an unmonitored automation is a new
   silent failure mode.

**Step 2 is the one most often skipped.** Automating a workaround preserves the defect forever
and removes the pain that would have motivated fixing it. Before automating anything recurring,
ask why it recurs.

## Automation has its own risks

A script that performs a destructive operation without a human in the loop is a **force
multiplier for mistakes** — the same idea appears in
[[Coding Knowledge/12 - Reliability Engineering/Stability Antipatterns|Stability Antipatterns]].
So:

- Automate the diagnosis before the remediation.
- Make automated actions idempotent and bounded (limit how many things it may act on at once).
- Log what it did and why.
- Give it a dry-run mode, and default to it while developing.

## Applying it here *(our synthesis)*

Toil in this stack is small in absolute terms and worth naming anyway, because a single operator
absorbs it invisibly:

| Recurring work | Toil? | Response |
| --- | --- | --- |
| Restarting a service after a reboot | Yes | Already automated — logon scheduled tasks |
| Publishing workflows after editing generators | Yes | Scripted; the generator is the source of truth |
| Pruning n8n execution history | Was | Eliminated by configuration, not by a cron job — `EXECUTIONS_DATA_PRUNE` |
| Checking whether services are up | Yes | A single health-check command, not four manual curls |
| Investigating a new failure | **No** | Novel, produces enduring value |
| Writing a note after a failure | **No** | Produces enduring value — this domain is that output |

The n8n pruning row is the pattern to imitate: **the application's own mature control removed the
work entirely**, rather than a custom script performing it forever. Prefer that whenever it
exists — it is also a stated principle of this project.

## Failure modes

- **Automating a workaround** instead of fixing the cause, making the defect permanent.
- **Calling all unpleasant work toil**, which makes the concept useless.
- **Automation with no monitoring**, converting visible manual work into invisible silent
  failure.
- **Unbounded automated remediation**, which amplifies a mistake across the fleet.
- **Ranking by annoyance** rather than by total time.
- **No list at all**, so the work is never visible enough to be prioritised.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/On-Call|On-Call]]
- [[Coding Knowledge/12 - Reliability Engineering/Stability Antipatterns|Stability Antipatterns]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment|Deployment]]
- [[Coding Knowledge/10 - Engineering Experience/Practitioner Heuristics|Practitioner Heuristics]]

## Sources

- Definition and the capping argument derived from Google, *Site Reliability Engineering* - <https://sre.google/books/> - **no reuse licence**; restated in our own words, nothing reproduced. The checklist, ranking method, automation-risk section and the local table are our synthesis; the n8n pruning settings were applied and verified in this project.
