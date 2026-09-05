---
type: note
domain: Intent & Task Understanding Knowledge
section: Requirements, Constraints & Assumptions
created: 2026-09-04
---

# Requirements, Constraints & Assumptions

Turn the enriched request into something with a testable definition of done, and —
critically — **keep three kinds of statement apart**: what the user actually
requires, what Vision inferred, and what Vision is assuming as a default. Confusing
these is how an agent ends up confidently doing the wrong thing.

> [!info] Provenance
> Reframing vague asks as testable criteria and the boundary tiers draw on
> **`spec-driven-development`** and **`constraint-driven-development`** in
> **`addyosmani/agent-skills`** (MIT), restated. The engineering-grade treatment
> lives in [[Coding Knowledge/09 - Engineering Practices/Requirements Analysis\|Requirements Analysis]];
> this note is the general, agent-routing version. Ours unless cited. See
> [[Intent & Task Understanding Knowledge/99 - Sources & Provenance\|99]].

## Reframe every vague requirement as a testable criterion

"Make it faster / cleaner / better" is not yet a requirement. Push it until you
could *check* whether it was met:

| Vague | Testable |
| --- | --- |
| "make it faster" | "landing page loads in under ~2.5s on a normal connection" |
| "clean up the file" | "remove trailing whitespace and dead code; behaviour unchanged" |
| "make it look better" | "improve spacing/typography/hierarchy; layout still works on mobile" |
| "works on phone" | "usable and readable at ~375px wide; no horizontal scroll" |

If it cannot be made checkable *and* the difference is material, that is a
clarification, not a requirement you get to invent
([[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]]).

## Constraints are hard limits — they survive everything

A constraint is a boundary the result must respect no matter what else changes.
Capture each one the instant it appears, verbatim, into the contract's `constraints`.
Common kinds, all of which have been silently dropped by naive planners:

- **Specific software / tool** — "in WordPad", "use Blender", "OpenCode".
- **File format** — ".docx", "PNG not JPG", "plain text".
- **Filename / location** — an exact name or folder.
- **Visual style** — "minimal", "dark", "match the existing site".
- **Language** — the human language of the output; the programming language.
- **Budget / deadline** — when stated.
- **Application requirement** — "must open in X".
- **Security restriction** — "don't touch the database", "read-only".
- **Every "do not" and "must"** — the most load-bearing words in the request.

**A constraint outranks a default and outranks the model's preference.** "Vanilla
JS, no React" means React is off the table even if the model would build it faster
in React. If two constraints genuinely conflict, that is a clarification.

## Three kinds of statement — never let them blur

This is the discipline the whole domain exists to protect (and the reason the task
contract has separate `explicit` / `inferred` / `assumptions` fields):

| Kind | Definition | How Vision may use it |
| --- | --- | --- |
| **Explicit** | The user actually said it | Treat as fixed truth |
| **Inferred** | A reasonable deduction from what they said | Use, but **label it an inference** if surfaced ("I'm taking this to mean…") |
| **Optional default** | A safe choice for a non-critical unknown | Use, and **state it** ("defaulting to a single page — say if you want more") |

Two rules on top:

- **Never present an inference as something the user explicitly requested.** "You
  wanted a dark theme" (they didn't say that) is a fabricated requirement; "I went
  dark to match the existing site — easy to change" is an honest default.
- **A default is only legitimate when the unknown is non-critical.** If the choice
  materially changes the result (marketing site vs internal tool), it is not a
  default — it is a question.

## How this feeds the plan

Once requirements, constraints and assumptions are separated and the definition of
done is testable, the constraints and the required artifacts drive
[[Intent & Task Understanding Knowledge/04 - Task Decomposition & Agent Selection\|agent selection]]
(e.g. a "must open in WordPad" constraint forces a desktop stage), and the testable
criteria become the `verify` steps on each stage.

## Anti-patterns

- Accepting "make it better" as executable without a testable target.
- Recording an inference or a default in the `explicit` bucket.
- Dropping a "don't" or a named tool during enhancement, then "rediscovering" it as
  a bug after the work is done.
- Choosing a default for a decision that actually needed the user.
