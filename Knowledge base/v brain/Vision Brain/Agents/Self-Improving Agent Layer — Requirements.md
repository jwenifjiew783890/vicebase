---
type: Requirements
domain: Agents
status: approved requirement — NOT implemented
created: 2026-09-03
---

# Self-Improving Agent Layer — Requirements

**Up:** [[Vision Brain]] › [[Agents/00 - Agents|Agents]]

> [!important] Reference only
> This note records an **approved architectural requirement**. Nothing here has been
> built, and nothing in Vision has been changed to accommodate it. Selection between
> candidates has not been made, and the audit and comparison step has not been run.
> See [[Decisions/Vision Architecture Decisions|ADR-013]].

## Intent

Add a controlled self-improving agent layer that gets better at work over time, without
becoming a second architecture and without acquiring the ability to change Vision itself.

## Layering

```
VISION — AGENTS          top-level orchestrator (unchanged, stays in charge)
    └── self-improving agent/layer      operates underneath it
            └── heavy executors         OFF → TASK → OFF
```

`VISION — AGENTS` remains the top-level orchestration layer. The self-improving layer is
a **specialist underneath it**, not a replacement for it and not a peer to it. Consistent
with [[Agents/Agent Strategy|Agent Strategy]]: an agent is a worker operating through
controlled capabilities, and is not Vision Core.

## Candidate

**NousResearch Hermes Agent** and its official self-evolution project is the preferred
candidate. It is preferred, not chosen: a clearly better mature open-source alternative
displaces it. The comparison must be made against the requirements below rather than
against general capability claims, and the alternative must be **reported before being
installed**, never installed first.

## Functional requirements

The layer must learn from all four signal types:

| Signal | Example |
| --- | --- |
| Successful tasks | a task completed cleanly — record what worked |
| Failures | a task that failed — record the failure mode |
| Corrections | the user fixes the agent's output |
| Feedback | the user comments on quality without correcting directly |

It must also:

- create, improve, persist and **reuse** skills / procedural knowledge
- improve those skills and workflows over time rather than only accumulating them
- keep persistent memory where persistence is genuinely warranted
- work with the existing model providers, including NVIDIA/Nemotron and other API models

## Architectural constraints

These are the constraints that decide the design; a candidate that cannot meet them is
not a candidate.

1. **Integrates with the existing Vision orchestrator; does not replace it.**
2. **Does not duplicate the Obsidian source-of-truth architecture.** Obsidian remains the
   single source of truth for durable shared knowledge, and is used for that purpose here
   where appropriate. See [[Decisions/Vision Architecture Decisions|ADR-009]].
3. **No full-vault duplication into Open WebUI Knowledge.** Retrieval is scoped and
   on-demand against Obsidian. This is settled architecture, not an open question.
4. **The agent must not freely modify Vision itself** — not its core architecture, and no
   deploying of arbitrary self-changes.
5. **Learning changes must be reviewable, reversible and isolated.** A change the agent
   makes to its own skills must be inspectable before it takes effect, undoable after it
   does, and contained so a bad one cannot spread.
6. **Heavy executors remain on-demand:** `OFF → TASK → OFF`. Nothing heavy stays resident.
7. **Do not add another large independent agent architecture** if an existing mature
   system already provides the required functionality.

## Must remain intact

Adding this layer must leave all of the following working exactly as they are:

- existing Vision agents and the `VISION — AGENTS` orchestration layer
- the MCP connections (`obsidian-vision-brain`, `n8n_vision`, `n8n_vision_test`)
- the Islamic source system — the deterministic `islamic_sources` tool, its SQLite index,
  the global retrieval policy filter and the citation audit
  (see [[Islamic Knowledge/99 - Source & Authenticity Rules|Source & Authenticity Rules]])
- the OpenCode integration and its agent permission boundary

## Sequence to follow

Per [[Decisions/Vision Architecture Decisions|ADR-012]] — `PLAN → APPROVE → IMPLEMENT →
TEST → STOP`:

1. record these requirements ← **this note; done**
2. audit the current `VISION — AGENTS` architecture and the Hermes integration status
3. research and compare mature options against the requirements above
4. justify the selection **before** building anything
5. implement only the selected option, with the **smallest possible integration**
6. run the acceptance tests below
7. report and stop

## Acceptance tests (for the implementation step, not yet run)

1. normal task execution
2. task failure → learning
3. user correction → learning
4. skill creation
5. skill reuse on a later task
6. persistence across restart
7. protection against unauthorised self-modification
8. Obsidian source-of-truth remaining intact
9. existing Vision agents still working
10. no duplicate full-vault knowledge import

## Related

[[Agents/Agent Strategy|Agent Strategy]] ·
[[Decisions/Vision Architecture Decisions|Vision Architecture Decisions]] ·
[[Integrations/Integration Strategy|Integration Strategy]]
