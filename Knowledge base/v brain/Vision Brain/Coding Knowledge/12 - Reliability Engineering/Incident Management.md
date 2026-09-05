---
type: note
domain: Coding Knowledge
section: 12 - Reliability Engineering
created: 2026-09-03
---

# Incident Management

Who does what while it is on fire. Structure exists so that nobody has to invent one under pressure.

> [!info] Provenance
> The separation of roles, the living incident document and the "mitigate before diagnosing"
> principle are **Google SRE practice** (itself adapted from emergency-services incident
> command), restated in our own words. The single-operator checklist and the evidence-capture
> section are **our synthesis**, and the evidence-capture point comes from a failure measured in
> this project.

## The failure this prevents

Without structure, an incident becomes several people investigating the same thing, nobody
talking to the people affected, two conflicting changes applied at once, and no record of what
happened. The recovery then takes longer than the failure — which is the pattern public
postmortems repeat most often.

## Roles, separated on purpose

| Role | Owns | Does **not** |
| --- | --- | --- |
| **Incident commander** | Coordination, decisions, who does what | Debug personally |
| **Operations lead** | Making the changes to the system | Talk to stakeholders |
| **Communications** | Telling affected people what is known and when the next update comes | Change anything |
| **Investigators** | Finding the cause | Apply changes without the ops lead |

The separation exists because the commander's job becomes impossible the moment they start
debugging — and debugging is far more absorbing than coordinating. One person can hold several
roles in a small incident; the point is that each role's work is **explicitly owned**, not that
four people are required.

## The sequence

**1. Declare it.** An explicit "this is an incident" is what starts the structure. Ambiguity
about whether something counts is itself a delay.

**2. Mitigate before diagnosing.** Restore service first. Rolling back without knowing the cause
is correct, not lazy — the cause is still there afterwards to investigate, and users are not.

**3. Capture evidence before restarting.** Logs, a thread dump, a heap dump, the process list,
the current configuration, the state of the data. **A restart destroys the only copy of the
failure.** Sixty seconds here is the difference between fixing it and waiting for it to happen
again. *(This one is ours, and it is written from experience in this project — restarting a
service ahead of capturing its state has already cost an investigation.)*

**4. One person coordinates.** Everyone investigating in parallel produces duplicated work and no
shared picture.

**5. Keep one living document** — timeline, current understanding, what has been tried, what is
next, who is doing what. It is the handoff mechanism and the raw material for the postmortem, and
it cannot be reconstructed afterwards.

**6. Change one thing at a time**, and record each change with its timestamp. Two simultaneous
changes make the outcome unattributable in both directions.

**7. Make no unrelated changes.** "While we are in here" is how one incident becomes two.

**8. Hand off explicitly** if it outlasts anyone's attention: what is known, what was tried, what
to watch.

**9. Declare it over**, and say so to everyone who was told it had started.

## Communication

- **Say what is known, what is not, and when the next update will come.** The last part is what
  stops people asking, and it is the part most often omitted.
- **Update on a schedule even when there is no news** — silence is read as "nobody is working
  on it".
- **Describe impact in the user's terms**, not in internal component names.
- **Never speculate about the cause publicly** during the incident. Early theories are usually
  wrong, and the correction is more damaging than the delay.

## Applying it here *(our synthesis)*

A single-operator stack has no roles to assign. What remains, and is genuinely useful:

- **Say out loud that this is an incident**, because it changes behaviour — mitigate first, stop
  making unrelated changes.
- **Write the timeline as you go.** You will not remember it, and this domain's
  [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]] note exists
  because timelines were written down.
- **Capture evidence before restarting**, always.
- **One change at a time**, even when alone — especially when alone, since there is no second
  person to notice the confounding.
- **Resist the tempting side-quest.** The Docker daemon force-kill in this project turned a
  cleanup into ~20 minutes of downtime.

## Failure modes

- **No declaration**, so nothing changes about how people work.
- **Everyone debugging, nobody coordinating.**
- **Restart before capture**, destroying the evidence.
- **Several simultaneous changes**, making the outcome unattributable.
- **Silence toward affected users**, which generates more interruption than updates would.
- **Public speculation** that later has to be retracted.
- **No written timeline**, so the postmortem is reconstructed from memory and is wrong.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Postmortems|Postmortems]]
- [[Coding Knowledge/12 - Reliability Engineering/On-Call|On-Call]]
- [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reproducible Debugging|Reproducible Debugging]]

## Sources

- Role separation and incident-response structure derived from Google, *Site Reliability Engineering* - <https://sre.google/books/> - **no reuse licence**; restated in our own words, nothing reproduced. Google credits the US Incident Command System as the origin of the role model. The evidence-capture step, the local adaptation and the failure modes are our synthesis, informed by incidents in this project.
