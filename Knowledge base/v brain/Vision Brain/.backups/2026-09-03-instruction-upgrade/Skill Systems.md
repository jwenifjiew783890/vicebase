---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Skill Systems

Packaging a repeatable procedure as data the agent loads when it applies.

## What a skill is

A named, reusable procedure with a **trigger condition** and a **body of instructions**, stored
as data rather than code. When a task matches the trigger, the body is loaded into context; when
it does not, the skill costs nothing.

That last property is the whole point: skills let a system know many procedures without paying
context for all of them on every request. A system prompt that contains every procedure is a
system prompt that is mostly irrelevant on every call.

## Anatomy

| Part | Purpose |
| --- | --- |
| **Name** | Stable identifier |
| **Description / trigger** | When this applies - the part that determines whether it is ever used |
| **Body** | The actual procedure: steps, constraints, examples, checks |
| **Resources** | Optional files, templates, scripts the skill refers to |

**The description does the selection**, exactly as with tools. A skill with a vague description
is a skill that never loads. Write it as "use this when the task is X", not as a title.

## Design rules

- **One skill, one procedure.** A skill covering three unrelated workflows will load for all
  three and be mostly noise.
- **Progressive disclosure.** A short description always visible; the full body loaded only when
  triggered; heavy resources loaded only when the body calls for them.
- **Make them composable.** Skills should not assume they are the only one loaded.
- **Include the failure modes**, not only the happy path. "If the file already exists, do X."
- **Include verification.** A skill that says how to check the work succeeded is worth several
  that only say what to do.
- **Version them**, and review changes. A skill is behaviour.

## Skills versus tools versus knowledge

Distinguishing these prevents a common muddle:

- A **tool** is a capability - code that does something.
- A **skill** is a procedure - how and when to use capabilities.
- **Knowledge** is fact and standard - what is true and what is required.

A skill for "release a version" describes the sequence; the tools are git and the CI API; the
knowledge is the project's release policy. Putting the release policy in the skill duplicates it;
putting the sequence in the knowledge base makes it unfindable when needed.

## Failure modes

- **Skills that never trigger** because the description does not match how tasks are phrased.
- **Skills that always trigger**, becoming a permanent context tax.
- **Overlapping skills** loading together and contradicting each other.
- **Stale skills** describing a workflow that changed - the same drift problem as documentation,
  with more consequence because the agent acts on it.
- **Skill sprawl.** Fifty skills, most unused, selection accuracy degraded for all.
- **Encoding facts in skills** rather than in knowledge, so the fact must be updated in several
  procedures.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Tool Selection|Tool Selection]]
- [[Coding Knowledge/04 - Agent Engineering/Self-Improvement|Self-Improvement]]
- [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]

## Sources

- Practitioner synthesis. Progressive disclosure of instructions is the pattern used by skill systems in current agent platforms; concepts restated, no text reproduced.
