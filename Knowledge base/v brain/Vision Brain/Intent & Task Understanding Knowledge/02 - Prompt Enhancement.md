---
type: note
domain: Intent & Task Understanding Knowledge
section: Prompt Enhancement
created: 2026-09-04
---

# Prompt Enhancement

Take a short, informal request and expand it into instructions an agent can actually
execute — **while keeping the request the user's, not the model's.** Enhancement adds
operational detail; it does not swap in a "better" goal.

> [!info] Provenance
> The vague-idea → concrete-proposal move draws on the **`idea-refine`** skill and
> the PRD framing of **`spec-driven-development`** in **`addyosmani/agent-skills`**
> (MIT); the "question refinement" pattern is from White et al., *A Prompt Pattern
> Catalog* (arXiv 2302.11382), restated. The goal-preservation stance and all Vision
> mapping are our synthesis. See [[Intent & Task Understanding Knowledge/99 - Sources & Provenance\|99]].

## The one line that governs this note

> **Make the user's request executable — do not change it into what the model thinks
> would be better.**

Enhancement is expansion *within* the user's intent. If the enhanced version would
surprise the user ("I asked to tweak the header, why did it rebuild the site?"), the
enhancement went too far.

## What enhancement preserves — always

Carry these through unchanged. Dropping one is the most damaging failure in this
whole domain, because it looks like success:

- **The goal** — the outcome from [[Intent & Task Understanding Knowledge/01 - Intent Extraction\|01]].
- **User-selected tools** — "in WordPad", "use Blender", "vanilla JS". Never
  substitute a tool the user did not ask for.
- **User-selected style / language / format** — visual style, filename, file format,
  the language to write in.
- **Important wording** — a phrase they clearly care about.
- **Negative requirements** — every "don't", "no", "not", "avoid". These are easy to
  lose because enhancement is additive by nature; guard them explicitly.

## What enhancement adds

Only detail that serves the stated goal:

- **Operational specifics** the goal implies — for a website: structure, responsive
  behaviour, basic accessibility and performance expectations, where assets come
  from, how it will be validated.
- **A default for a non-critical unknown**, clearly marked as a default (not as
  something the user asked for) — see the assumption tiers in
  [[Intent & Task Understanding Knowledge/03 - Requirements, Constraints & Assumptions\|03]].
- **A verification step** for anything that writes or changes state.

If an addition is *material* and you cannot pick a safe default, it is a question,
not an enhancement ([[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]]).

## Worked example — "make me a website for vision"

A reasonable enhancement, with the goal intact:

- **Goal (unchanged):** a website representing Vision.
- **Added, as defaults (stated):** start with a single responsive landing page;
  clean modern layout; semantic HTML with basic WCAG contrast/alt text; no heavy
  framework unless asked; assets kept local; validate by opening it in the browser
  agent.
- **Flagged for the user (material, not assumable):** is this marketing, product, or
  docs? one page or several? is there an existing site to build on?
- **Route:** intent → [[Website Development Knowledge/00 - Website Development Index\|Website Development Knowledge]]
  → coding/implementation → browser validation ([[Intent & Task Understanding Knowledge/04 - Task Decomposition & Agent Selection\|04]]).

What enhancement must **not** do here: decide unprompted that Vision wanted a
five-page marketing site with a blog and a contact form, then build it.

## Conversational enhancement — the user shouldn't have to talk like a programmer

"make the Vision website look better" should become something like:

> **Goal:** improve the *existing* Vision site's visual quality.
> **Likely areas:** visual hierarchy, spacing, typography, navigation,
> responsiveness, small interaction polish.
> **First step:** *inspect the actual site* before changing anything.

Two rules make this safe:

1. **Inspect before you change.** "Look better" is not "rebuild". Read the current
   site (browser agent / the repo) first; propose the smallest change that meets the
   goal. Do not assume a full redesign.
2. **Improve, don't replace.** "Better" modifies the thing that exists; it does not
   grant permission to throw it away. A redesign is a *different, larger* request —
   confirm it before treating "look better" as one.

## Anti-patterns

- Silently upgrading scope: "tweak the header" → a full redesign.
- Swapping the user's tool for the model's favourite ("no React" → shipped React).
- Adding a feature nobody asked for because it seemed nice, and presenting it as
  part of the request.
- Losing a "don't" because the enhanced instruction was written fresh and positive.
- Rewriting so heavily the user no longer recognises their own request.
