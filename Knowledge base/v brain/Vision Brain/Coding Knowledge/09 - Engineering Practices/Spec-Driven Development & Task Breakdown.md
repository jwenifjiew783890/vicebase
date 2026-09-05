---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-04
---

# Spec-Driven Development & Task Breakdown

The loop between knowing *what* is needed and having a design: turning an agreed requirement into
a small, ordered, verifiable sequence of build steps. This sits between
[[Coding Knowledge/09 - Engineering Practices/Requirements Analysis|Requirements Analysis]] (find
the real need) and [[Coding Knowledge/09 - Engineering Practices/System Design|System Design]] (the
design that survives). It is the discipline that keeps an agent — or a person — from "guessing in
code".

> [!info] Provenance
> Method **derived and restated** from the **`spec-driven-development`** and
> **`planning-and-task-breakdown`** skills in **`addyosmani/agent-skills`** (Addy Osmani, with
> F. Bartoli and J. León), MIT-licensed, retrieved **2026-09-04**
> (<https://github.com/addyosmani/agent-skills>). The *Applying it in Vision* section is our own.
> Nothing is copied verbatim; the source's concepts are named and credited. Full record in
> [[Coding Knowledge/99 - Sources & Provenance|Sources & Provenance]].

## The loop

**Specify → Plan → Tasks → Implement.** Each stage has an output that is reviewed before the next
begins. Writing the spec *after* the code produces documentation, not specification — the value is
in forcing clarity *before* code exists.

## 1 · Specify — the shared source of truth

Before building, surface assumptions explicitly, then pin down enough that "done" is not a matter
of opinion. A useful spec states:

- **Objective** — what, why, for whom, and what success is.
- **Boundaries** in three tiers — **Always do / Ask first / Never do**. "Ask first" items need
  human approval before implementation; "Never do" is non-negotiable without an explicit scope
  change.
- **Testing strategy** — framework, levels, what "verified" means here.
- **Interfaces & structure** — the commands, the directory/layout, the conventions a change must
  follow.

**Reframe every vague requirement as a testable criterion.** "Make it faster" is not a spec;
"dashboard LCP < 2.5s on 4G, initial load < 500ms" is. See
[[Coding Knowledge/09 - Engineering Practices/Requirements Analysis|Requirements Analysis]] for
eliciting these; this note is about writing them down so they drive the build.

### Multi-capability requests: map before you spec

When one request bundles several independently testable capabilities, do a **scope check** first:
produce a **capability/module map** — a table of modules, their dependencies, and a build order —
and get it approved *before* writing any module spec. Rules that keep it sane: module ids are
**kebab-case, chosen once, never renamed** mid-initiative, and the **dependency graph must be
acyclic**. This stops one monolithic spec that forces every later step to reason over an oversized
contract.

## 2 · Plan — the technical approach

Map the spec and the codebase **read-only** (no code yet). Output a short plan: major components,
**dependency order**, risks, what can run in parallel, and where the verification checkpoints go.

## 3 · Tasks — decompose into verifiable units

Break the plan into discrete tasks. **Each task carries its own contract:**

- a descriptive title and one-paragraph explanation,
- **2–3 acceptance criteria that are specific and testable** ("submission rejects invalid email
  formats", not "registration works"),
- **verification steps** — the tests/build/manual checks that prove it,
- explicit **dependencies** and the files it will likely touch.

**Size tasks small.** A rough scale:

| Size | Files | Scope |
| --- | --- | --- |
| XS | 1 | a single function or config change |
| S | 1–2 | one component or endpoint |
| M | 3–5 | one feature slice |
| L | 5–8 | multi-component — prefer to split |
| XL | 8+ | **too large — break it down** |

Agents (and reviewers) do best on **S–M** tasks. Split a task further if it would take more than a
couple of hours, needs four or more acceptance criteria, touches two independent subsystems, or has
"**and**" in its title. Keep a task to **~5 files or fewer**.

## 4 · Order & implement incrementally

- **Bottom-up on the dependency graph** — schema → types → validation → endpoints → UI. Build the
  foundation before its consumers.
- **Vertical slices, not horizontal layers** — deliver one complete path end-to-end (registration,
  *then* login, *then* the next), each a working, testable increment. Not "all the database, then
  all the API, then all the UI".
- **The system stays working after every task.** No big-bang "integrate everything at the end".
- **A verification checkpoint every 2–3 tasks** (tests pass, build clean, the flow works), and
  **high-risk work goes early** so it fails fast.
- Implement each task with test-first and incremental habits, pulling in the relevant *spec
  section* rather than the whole document (see
  [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]).

## When *not* to use this

A single-line fix, a typo, an unambiguous self-contained change needs no formal spec or task list.
Match ceremony to risk — the same rule the website-build workflow uses.

## Red flags

- Implementation started with **no written task list**.
- Tasks with **no acceptance criteria** or **no verification steps**.
- Everything sized XL; no checkpoints; dependency order unconsidered.
- **Overwriting an existing plan that still has unchecked tasks** — those may be mid-build in
  another session. Stop and ask.

## Applying it in Vision *(our synthesis)*

- The loop **is** Vision's cadence: **PLAN → APPROVE → IMPLEMENT → TEST → STOP**. "Specify" and
  "Plan" are the PLAN/APPROVE gates; the human-approval step on the spec is not optional
  ([[Decisions/Vision Architecture Decisions|ADR-012]], and Muaz's stated sequence).
- The **capability/module map** mirrors how Vision already thinks — the agent registry and the
  vault's domain map are exactly this "declare the modules and their build order once" pattern
  ([[Coding Knowledge/04 - Agent Engineering/Orchestrators|Orchestrators]]).
- **"Never overwrite an incomplete plan — another session may be mid-build"** is not hypothetical
  here: multiple Claude Code sessions edit the vault and the workflows concurrently. Treat a
  `tasks/` list, a registry, or a note with unfinished work the way that rule says — check first,
  ask before clobbering.
- **Always / Ask-first / Never** boundaries map onto Vision's permission tiers and the executors'
  `OFF → TASK → OFF` contract — write them into the spec so the agent inherits them.

## See also

- [[Coding Knowledge/09 - Engineering Practices/Requirements Analysis|Requirements Analysis]] ·
  [[Coding Knowledge/09 - Engineering Practices/System Design|System Design]] ·
  [[Coding Knowledge/09 - Engineering Practices/Testing Strategy|Testing Strategy]] ·
  [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]]
- [[Coding Knowledge/04 - Agent Engineering/Planners|Planners]] — the agent component that plans a
  route; this note is the engineering method it should follow.
- [[Website Development Knowledge/00 - Website Development Index|Website Development Knowledge]] —
  the same "match ceremony to risk" build discipline for websites.
