---
type: note
domain: Intent & Task Understanding Knowledge
section: Task Decomposition & Agent Selection
created: 2026-09-04
---

# Task Decomposition & Agent Selection

Break a multi-part request into ordered stages, pick the right specialist for each,
and pass the output of one into the next — using the **existing**
[[Coding Knowledge/11 - Vision & OpenCode/Vision Architecture\|VISION — AGENTS]] hub,
not a new one.

> [!info] Provenance
> The decompose-into-verifiable-steps method draws on **`planning-and-task-breakdown`**
> in **`addyosmani/agent-skills`** (MIT), restated and detailed in
> [[Coding Knowledge/09 - Engineering Practices/Spec-Driven Development & Task Breakdown\|Spec-Driven Development & Task Breakdown]].
> The agent roster and the material-passing mechanism are facts of Vision's own
> system (`agent-registry.json`), verified by live execution. See
> [[Intent & Task Understanding Knowledge/99 - Sources & Provenance\|99]].

## First: does this even need decomposing?

Most requests are **one stage, one agent**. Decompose only when there is more than
one distinct deliverable or a real dependency between steps.

- `open example.com` → one stage (browser). Done.
- `download the assignment and open it in WordPad` → two stages (browser → desktop),
  with a dependency. Decompose.

Count what the user actually asked to *receive*. One deliverable → one stage. The
cost of over-planning is latency and failure surface; the cost of under-planning is a
missing deliverable. Both are real.

## Kinds of stage relationship

| Relationship | Meaning | Planning consequence |
| --- | --- | --- |
| **Independent** | Stages don't need each other | Could run in any order (hub runs sequentially) |
| **Dependent / sequential** | B needs A's output | Order matters; A's result feeds B |
| **Parallel-in-principle** | Two deliverables, no data link | Still ordered by the hub; note they're independent |
| **Verification** | Confirm a stage did what it claimed | Add after any write/change (the `verify`) |
| **Human approval** | A consequential step needs a yes | A gate, not an agent stage — see [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]] |

**Order bottom-up on dependencies**, and keep the system in a working state after
each stage rather than integrating everything at the end (the same discipline as
[[Coding Knowledge/09 - Engineering Practices/Spec-Driven Development & Task Breakdown\|Spec-Driven Development]]).

## Selecting the agent — map the requirement to the specialist

Vision's real, enabled agents (from `agent-registry.json`) and what each is *for*:

| Need in the request | Agent | Executor |
| --- | --- | --- |
| Look something up on the live web; open/read/click a **specific website**; screenshot; capture a download | **Browser** | Auto Browser |
| Operate a **Windows app**; enter/read on-screen text; save & verify a file on the desktop | **Desktop** | Windows-MCP |
| Model / lay out / light / export **3D** content | **Blender** | Blender (headless) |
| Read or change **code** in a local project (needs an absolute path) | **Coding** | OpenCode |
| Open research question; compare named options | **Research** | n8n |
| Draft / summarise / extract text; draft a message (never sends) | **Content** | n8n |
| Analyse supplied data; write a report; plan a goal | **Business** | n8n |
| Is a service up? check a website's status; digest feeds | **Monitoring** | n8n |

Selection rules that prevent the common mistakes:

- **Don't route everything through Desktop.** Desktop is for operating Windows apps,
  not a general fallback. Reading a web page is the **Browser** agent's job.
- **Don't send browser work to Desktop.** If Auto Browser can do it (navigate, read,
  fill a web form, capture a download), it is a Browser stage — not "drive Chrome via
  the desktop".
- **Coding needs an absolute project path** and refuses without one — carry the path
  in the stage's context.
- **Fewest agents that genuinely satisfy the request.** `compare_options` already
  researches, so a comparison doesn't need a separate research stage first.
- Prefer the **read-only** capability when the goal is read-only (Monitoring's
  website check over a full Browser session, when a status/excerpt is all that's
  asked).

## Passing material between agents

This is the part that makes a chain real rather than two agents run side by side.
The hub already does it — **use it, don't rebuild it**:

- Each agent returns a structured result (`ok`, `result`, and for the executors
  structured artifact fields like Browser's `downloads`/`screenshots`/`final_page`
  and Desktop's `files`). See the contract in
  [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|00]].
- The hub's `Prepare Stage` node carries an earlier stage's result into a later
  stage's `context` — either where the plan wrote the literal token `{{PREVIOUS}}`,
  or automatically when a later stage has no context of its own.
- So in the plan, a dependent stage's `context` should be `{{PREVIOUS}}` (or name the
  specific artifact), and the downstream agent works on it.

**Proven live:** a Browser stage read example.com's title; the hub passed it into a
Desktop stage that wrote the title to a workspace file and read it back to verify —
two stages, `complete: true`, material intact.

**Known boundary (don't force it):** the Browser and Desktop executors have
*separate* workspace roots and Auto Browser downloads land in the browser stack's
own data dir, which the Desktop executor is not scoped to read. **Text/metadata
(a title, a filename, a path) passes cleanly; the actual file bytes of a browser
download are not yet in a place the desktop stage can open.** A "download then open
the file" chain therefore needs a shared handoff location before it will work
end-to-end — a change to executor scoping, not something to hack around in a plan.

## The planning loop (for genuinely multi-agent tasks)

1. Understand intent → 2. Identify the required outcome(s) → 3. Break into stages →
4. Order by dependency → 5. Select an agent per stage → 6. Decide what material
passes between them → 7. Add a verify to each write → 8. Note any human-approval gate
→ 9. Hand the plan to the hub → 10. On a stage failure, don't feed bad state
downstream (see [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]]) →
11. Stop at the stage cap (the hub enforces max 4) → 12. Let the hub synthesise the
result. **Skip this whole loop for one-stage requests.**

## Anti-patterns

- Routing a "read this web page" task to Desktop.
- Making every request a four-stage plan.
- A dependent stage with empty context and no `{{PREVIOUS}}`, so the downstream agent
  works on nothing.
- Assuming a browser-downloaded file is readable by the desktop stage (the workspace
  boundary above).
- Adding a stage that produces nothing the user asked for.
