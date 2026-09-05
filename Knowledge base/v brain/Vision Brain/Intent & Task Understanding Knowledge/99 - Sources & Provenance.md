---
type: note
domain: Intent & Task Understanding Knowledge
section: root
created: 2026-09-04
---

# Sources & Provenance

Where this domain's material comes from, each source's licence, and the rule that
keeps the corpus clean: **synthesise and attribute, never paste.**

## How these notes were produced

Every note is **original prose written for this vault.** What is reused is factual
and methodological — how a technique works, what a practice recommends — which is not
itself copyrightable. Named skills and papers are credited at the point of use;
nothing is copied verbatim. This follows the same discipline as
[[Coding Knowledge/99 - Sources & Provenance\|Coding Knowledge · Sources & Provenance]].

## Sources

| Source | Licence | Verified | How it is used |
| --- | --- | --- | --- |
| **`addyosmani/agent-skills`** — <https://github.com/addyosmani/agent-skills> (A. Osmani, F. Bartoli, J. León) | **MIT** | 2026-09-04 | Primary anchor. Concepts from `interview-me` (one-question intent interview → [[Intent & Task Understanding Knowledge/01 - Intent Extraction\|01]], [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]]), `idea-refine` + `spec-driven-development` (vague→concrete, testable criteria → [[Intent & Task Understanding Knowledge/02 - Prompt Enhancement\|02]], [[Intent & Task Understanding Knowledge/03 - Requirements, Constraints & Assumptions\|03]]), `constraint-driven-development` (constraint boundaries → 03), `planning-and-task-breakdown` (decompose into verifiable stages → [[Intent & Task Understanding Knowledge/04 - Task Decomposition & Agent Selection\|04]]). Concepts extracted, nothing copied. Same repo already recorded in the Coding ledger. |
| White et al., *A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT* — arXiv 2302.11382 | Academic (arXiv) | 2026-09-04 | The "question refinement" pattern (suggest a better-formed request) behind [[Intent & Task Understanding Knowledge/02 - Prompt Enhancement\|02]]. Cited by URL; concept restated. |
| *Reframing LLM Agent Security as an Agent-Human Interaction Problem* — arXiv 2605.24309 | Academic (arXiv) | 2026-09-04 | "Front-load ambiguity / over-authorization detection into planning; the agent is assistive, not decisional." Behind the safety stance in [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]]. |
| Intent-aware & uncertainty-aware clarifying-question research (e.g. CIKM 2024 intent-clarify; information-gain clarification, arXiv 2606.03135) | Academic | 2026-09-04 | General principle: precise, single, high-information clarifying questions; ask when ambiguity is material. Restated in 05. |

## What is Vision's own, not external

Deliberately separated so it is never mistaken for sourced fact:

- The **internal task contract** (explicit / inferred / assumptions / constraints /
  steps) in [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|00]] —
  our synthesis, adapted to the hub's existing plan shape.
- The **agent roster and selection rules** in [[Intent & Task Understanding Knowledge/04 - Task Decomposition & Agent Selection\|04]] —
  facts of Vision's own `agent-registry.json`, not an external source.
- The **material-passing mechanism and its workspace boundary**, the **honest-failure
  path**, and the **safe-vs-ask-first** mapping onto Vision's structural guarantees —
  read from Vision's own workflows and **verified by live execution 2026-09-04**
  (browser→desktop title handoff succeeded; a missing-file desktop read failed
  honestly).

## Relationship to other domains

This domain does not duplicate them; it routes into them:

- [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]] —
  *how* Vision talks (tone, restraint on questions). This domain is *what* it decides
  to do. The "don't interrogate" principle is shared.
- [[Coding Knowledge/09 - Engineering Practices/Requirements Analysis\|Requirements Analysis]]
  and [[Coding Knowledge/09 - Engineering Practices/Spec-Driven Development & Task Breakdown\|Spec-Driven Development & Task Breakdown]] —
  the engineering-grade treatment for code work specifically.
- The user model ([[Communication Style]], [[Personality & Behavior]]) — overrides
  every generic default here.

## Rules for future additions

1. Name the source and its licence before importing anything substantial.
2. Never paste more than a short attributed phrase, and never from a non-permissive
   source.
3. Record the retrieval date for anything fetched.
4. Keep Vision-verified claims (marked *live*) separate from external methodology.
5. If a claim can't be sourced or verified, mark it as judgement, not fact.
