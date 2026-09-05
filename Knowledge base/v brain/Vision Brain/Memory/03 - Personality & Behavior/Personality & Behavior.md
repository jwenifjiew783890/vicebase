---
type: stable
category: behavior
last_verified: 2026-09-03
confidence: medium-high
---

# 03 — Personality & Behavior

> **Scope note.** This is an *interaction preference model*, not a
> psychological profile. It describes how to work with the user effectively.
> Do not extend it into personality diagnosis.

Stated by the user 2026-09-03; several items independently corroborated by
observed behaviour in the Vision work.

## How they build

- Highly project-oriented and highly iterative. `[user]`
- Ambitious about system scope — likes exploring large, capable systems. `[user]`
- Comfortable experimenting with software; happy to install and test. `[user]`
- **Prefers practical implementation over endless planning.** `[user]`
- Likes seeing systems *actually work*, not described as working. `[user]`
- Thinks in complete systems rather than isolated features. `[user]` `[vault]`
- Cares about architecture and long-term scalability. `[user]` `[vault]`

## How they review work

- Notices inconsistencies quickly. `[user]`
- **Challenges answers that seem incorrect.** `[user]`
- Expects a correction when an earlier answer was wrong — and values that
  over face-saving. `[user]`
- Values honesty above pleasing language. `[user]`

Practical consequence: do not smooth over a mistake or quietly move past it.
Correct it plainly and continue.

## What they expect from AI

- Strongly values autonomy — delegate-and-verify, not step-by-step handholding.
  `[user]`
- Likes handing implementation to capable agents. `[user]`
- **Wants the AI to remember relevant context** instead of re-asking the same
  questions. `[user]` — this note's existence is a direct response to that.
- Prefers unified user experiences over fragmented workflows. `[user]`

## Observed corroboration

`[inferred — CONFIDENCE: HIGH]` During Phase 2.1 the user set the task up as
"inspect first, choose, then implement, then prove it with real operations,
then report" — matching the stated preference for verification over assertion
and for delegated implementation. Consistent with [Lessons Learned](Memories/Lessons%20Learned.md.md) items 6
and 7 (*prove it runs*, *test real behaviour*).
