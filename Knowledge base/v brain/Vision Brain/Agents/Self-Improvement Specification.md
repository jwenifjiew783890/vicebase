---
type: Specification
domain: Agents
status: specification — defines the mechanism; not yet implemented
created: 2026-09-03
---

# Self-Improvement Specification

**Up:** [[Vision Brain]] › [[Agents/00 - Agents|Agents]] ·
Requirement: [[Agents/Self-Improving Agent Layer — Requirements]] ·
Principles: [[Coding Knowledge/04 - Agent Engineering/Self-Improvement|Self-Improvement]]

> [!info] What this document is
> The **operational contract** for Vision's skill-learning layer: what is captured, how a skill
> is created, evaluated, trusted, demoted and rolled back, and what the agent may never touch.
> The principles live in the Coding Knowledge note above; this is the mechanism. One concept,
> one note — this does not restate the principles, and the principles do not restate this.

Nothing here is built yet. It is written first so that what gets built is decided rather than
discovered.

## Position in the architecture

```
VISION — AGENTS                 orchestrator — unchanged, stays in charge
  └── specialist agents / capabilities
        └── Evaluate Results    ← the learning signal, already emitted today
              └── skill-learning layer   (on-demand; no resident runtime)
                    └── Obsidian  Agents/Skills/<name>/SKILL.md
                          └── future agents retrieve and reuse
```

The layer **reads** the outcome of work Vision already did. It never executes the work itself —
that is what keeps Vision the executor and prevents a second agent runtime.

## 1. What counts as a learning event

Exactly four, all derived from signals Vision already produces:

| Event | Source | Why it is worth capturing |
| --- | --- | --- |
| **Success** | `Evaluate Results` → `complete: true` | A sequence that worked is a candidate procedure |
| **Failure** | `Evaluate Results` → `failed > 0`, with the stage's error | The failure mode is the payload |
| **Empty** | `Evaluate Results` → `empty > 0` | The agent ran but produced nothing usable — a distinct defect |
| **Correction** | The user rejects, edits or contradicts an output | The strongest signal available, and the only one carrying intent |

A learning event is **not** created by the agent deciding something was interesting. It is
created by one of the four conditions above. This is deliberate: an agent that nominates its own
learning events will nominate its own mistakes.

**Silence is not success.** A user who did not complain has not approved anything. Absence of a
correction never promotes a skill.

## 2. What gets captured

For every event, a record containing only what is verifiable:

- the task as stated, and the agent that ran it
- the capability sequence actually invoked
- the outcome, verbatim from `Evaluate Results` (not a summary of it)
- for failures: the error text as emitted
- for corrections: the before and after, and the user's words
- timestamps, and the run identifier

Never captured: secrets, credentials, personal data beyond the task text, or the agent's own
speculation about why something worked.

## 3. How a candidate skill is generated

By **prompting an existing Vision model** with the captured record and the authoring standard —
the same design Hermes uses, where `build_learn_prompt()` returns a prompt and the agent's own
toolset does the work. No distillation engine, no new runtime.

Output is a directory in the open [SKILL.md](https://agentskills.io) format:

```
Agents/Skills/<skill-name>/
  SKILL.md          YAML frontmatter: name, description (both required) + body
  references/       optional, loaded only when the body calls for them
```

Authoring rules, from Anthropic's published Agent Skills guidance and the vault's own
[[Coding Knowledge/04 - Agent Engineering/Skill Systems|Skill Systems]] note:

- **The description does the selection.** Write "use this when the task is X", not a title.
  A vague description is a skill that never loads.
- **One skill, one procedure.**
- **Progressive disclosure** — short description always visible, body on trigger, references
  only when the body calls for them.
- **Include the failure modes and the verification step**, not only the happy path.
- Keep the body lean; split into `references/` rather than growing one file.

A candidate is born **`provisional`** and is never loaded into a task automatically.

## 4. How it is evaluated

Three gates, in order. Failing any one stops promotion.

1. **Static scan.** Reject exfiltration, destructive commands, prompt-injection and persistence
   patterns before a human ever reads it. `skills_guard.py` from Hermes (MIT, stdlib-only) is
   verified to do exactly this standalone and may be vendored with attribution.
2. **Human review.** The skill is a Markdown file in the vault: readable, diffable, editable.
   No skill becomes `trusted` without a person reading it.
3. **Independent use.** It must produce a successful outcome on a task that is *not* the one it
   was learned from. Passing on its own origin task proves nothing.

## 5. When it becomes trusted

| State | Meaning | How it is entered |
| --- | --- | --- |
| `provisional` | Exists, not used automatically | On creation |
| `trusted` | Eligible for automatic retrieval | All three gates passed |
| `stale` | Unused for a long period | Time, automatic |
| `archived` | Withdrawn, recoverable | Demotion or age |
| `pinned` | Exempt from all automatic transitions | Set by a human only |

Promotion is **never automatic**. Time and success make a skill *eligible*; a human makes it
trusted.

## 6. How failures demote or retire a skill

A `trusted` skill whose use coincides with a `failed` or `empty` outcome is demoted to
`provisional` **immediately, automatically, and without review** — the asymmetry is deliberate:
promotion needs a human, demotion does not.

Repeated failure after demotion moves it to `archived`.

**Nothing is ever deleted.** Archiving moves the directory; the content survives and is
recoverable. This is Hermes's `archive-never-delete` invariant, and it is the difference between
a reversible system and a lossy one.

## 7. How provenance is recorded

In the SKILL.md frontmatter, so it travels with the skill and is visible in any diff:

```yaml
---
name: <skill-name>
description: Use this when ...
state: provisional
origin_event: success | failure | correction
origin_run: <run id>
created: 2026-09-03
created_by: agent | user
supersedes: <previous version, if any>
review:
  scanned: <date>
  reviewed_by: <person>
  independent_use: <run id>
---
```

`created_by` matters: a skill a **user** wrote is theirs and is never auto-curated. Only
agent-authored skills are subject to automatic transitions. This is Hermes's write-origin
provenance pattern, reimplemented rather than imported.

## 8. How versions are managed

The skill is a file in the vault, so version history is file history. A change to a `trusted`
skill:

1. writes the new body alongside the old,
2. returns the skill to `provisional`,
3. records `supersedes`,
4. requires the gates again.

**Editing a trusted skill does not preserve its trust.** Behaviour changed; trust is re-earned.

## 9. How rollback works

Three levels, cheapest first:

1. **Demote** — set `state: provisional`. The skill stops being retrieved. Instant, no content lost.
2. **Revert** — restore the previous body from file history. It is Markdown; the diff is readable.
3. **Archive** — move the directory out of `Agents/Skills/`. Recoverable by moving it back.

If a skill cannot be identified as the cause, demote the candidates and re-promote one at a time.

## 10. How user corrections override previous behaviour

A correction is the highest-authority signal in the system and it acts **immediately**:

- the skill whose behaviour was corrected is demoted to `provisional` at once;
- the correction is captured as a learning event with the user's own words;
- any new skill derived from it records `origin_event: correction`;
- a correction can never be overridden by subsequent success counts. Only the user can restore
  what the user rejected.

## 11. What the agent is forbidden from changing

Absolute. No task, instruction or learned skill may authorise any of these.

- **Its own permissions**, allowlists, sandbox boundaries or capability registry. *A system that
  can widen its own boundary has no boundary.*
- **Vision's core** — Open WebUI source, `VISION — AGENTS`, the n8n hierarchy, MCP configuration,
  the OpenCode integration, the Islamic Knowledge system.
- **Its own state field.** The agent proposes; promotion is a human act.
- **Another skill's provenance or review record.**
- **Anything outside `Agents/Skills/`.** The learning layer's entire write surface is that one
  directory. Durable knowledge elsewhere in the vault is written by people.

Improvement flows into **data the agent reads**, never into **code the agent runs**.

## Resource contract

On-demand only: invoked after a task, exits when done. No daemon, no resident process, no vector
store, no second database. If an implementation needs a persistent runtime to work, it is the
wrong implementation — see the measured evidence in
[[Agents/Self-Improving Layer — Candidate Comparison (PROPOSED)]].

## Provenance of this specification

- **`SKILL.md` format** — open standard, [agentskills.io](https://agentskills.io) v1.0.0.
- **Authoring and progressive disclosure** — Anthropic, *Equipping agents for the real world with
  Agent Skills* (anthropic.com/engineering).
- **Lifecycle states, archive-never-delete, write-origin provenance, static scanning** — patterns
  observed by reading NousResearch/hermes-agent (MIT), reimplemented here rather than imported;
  `skills_guard.py` is the one component verified extractable and is MIT-licensed.
- **Trust states and demotion-on-failure** — HKUDS/OpenSpace (MIT), design only; its loop was
  measured unsuitable for this architecture.
- **The four learning events** — Vision's own `Evaluate Results` node, which already emits them.

## See also

[[Coding Knowledge/04 - Agent Engineering/Self-Improvement|Self-Improvement]] ·
[[Coding Knowledge/04 - Agent Engineering/Skill Systems|Skill Systems]] ·
[[Coding Knowledge/04 - Agent Engineering/Evaluation Loops|Evaluation Loops]] ·
[[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]
