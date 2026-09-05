---
type: note
domain: Intent & Task Understanding Knowledge
section: Intent Extraction
created: 2026-09-04
---

# Intent Extraction

Read the request as it actually is — informal, short, mistyped, half in another
language — and recover what the person is trying to *achieve*. The failure to avoid
is answering the literal words while missing the point.

> [!info] Provenance
> The one-question interview idea is from the **`interview-me`** skill in
> **`addyosmani/agent-skills`** (MIT). The "inject conversation history to resolve
> references like *just fix it*" point restates published intent-classification
> practice. Everything else, and all Vision-specific mapping, is our synthesis. Full
> record in [[Intent & Task Understanding Knowledge/99 - Sources & Provenance\|99]].

## What to pull out of a request

Not every request has all of these; extract the ones that are present, and note
which are missing so [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]]
can decide whether the gap matters.

| Signal | The question it answers | Example cue |
| --- | --- | --- |
| **Desired outcome** | What does "done" look like *for them*? | "so I can send it tonight" |
| **Object of the task** | What is being acted on? | "the file I downloaded", "the Vision site" |
| **Target environment** | Where does it happen? | "on my desktop", "in WordPad", "on phone" |
| **Constraints** | What is fixed and non-negotiable? | "in vanilla JS, no React" |
| **Quality bar** | Rough draft or polished? | "polished", "just a quick check" |
| **Deadline / urgency** | Only when stated | "by tonight", "quick" |
| **Required artifacts** | What do they expect to receive? | "a landing page", "a report" |
| **Implicit dependencies** | What must happen first? | opening a file implies it exists / was fetched |
| **Explicit prohibitions** | The "don't" that must survive planning | "don't redesign the whole thing" |
| **Preferred method** | A tool/approach they named — honour it | "use WordPad", "do it in Blender" |

A **prohibition or a named tool is the highest-value signal in the sentence.** It is
also the one most often lost during enhancement, so capture it verbatim into the
contract's `constraints` / `preferred_tools` the moment it appears.

## Natural, messy language is the normal case

Muaz's input is often terse, code-switched (English + Roman Urdu/Hindi), voice-typed,
or shorthand. Treat all of it as first-class, not as something to correct.

- **Typos and speech-to-text errors** — read through them to the obvious word
  ("opne the fiel", "wordpade"). Do not echo the typo back or make it a topic.
- **Roman Urdu / Hindi and code-switching** — "yeh file kholo", "isko theek kardo"
  are ordinary instructions. Understand them; reply in the user's register (see
  [[Conversation Knowledge/05 - Memory Continuity and Cultural Adaptation\|Conversation 05]]).
- **Slang / shorthand** — "make it pop", "clean it up", "sort this out" carry real
  intent; map them to concrete outcomes in [[Intent & Task Understanding Knowledge/02 - Prompt Enhancement\|02]].
- **Fragments** — "the assignment thing from earlier" is a reference, not noise.

The rule: **infer the wording, never invent the intent.** Fixing a typo is safe;
deciding what an ambiguous *goal* means is not — that belongs to
[[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]].

## Contextual references — "that one", "the file you downloaded", "same as before"

These only resolve against **known state**: the current conversation, a remembered
artifact, or a result an agent just produced. Injecting recent history into the
reading is what makes "just open it" resolvable at all.

- If exactly one referent fits and it is known → use it, and name it back so the
  user can catch a mismatch ("opening the PDF you downloaded, `Assignment1.pdf`").
- If several materially different referents fit, or none is known → **ask which**,
  don't guess (a wrong file is a real cost). See
  [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]].
- Never fabricate a referent to avoid asking. "The file" with no known file is a
  missing fact, not a default.

Vision's own artifact state makes this concrete: after the browser agent reports a
download, its path/filename is *known state*, so "open the file you downloaded" is
resolvable; with no such prior result, it is a question.

## Worked example

> "make me a website for vision"

| Extracted | Value |
| --- | --- |
| Desired outcome | a website that represents Vision |
| Object | the Vision project/product |
| Quality bar | unstated — likely presentable, not throwaway |
| Constraints | none stated |
| Artifacts | a working site (at least a landing page) |
| Missing, material? | purpose (marketing vs docs vs app), scope (one page vs multi), existing site? |

The outcome is clear enough to *start*; the scope is not. That gap goes to
enhancement ([[Intent & Task Understanding Knowledge/02 - Prompt Enhancement\|02]])
and, where it changes the result, to a clarifying question — not to a silent guess
that Vision wanted a five-page marketing site.

## Anti-patterns

- Answering the literal words and missing the goal ("open it" → asking *what file
  format they prefer* instead of opening the known file).
- Treating Roman-Urdu/Hindi or a typo as a problem to flag rather than input to read.
- Resolving "that one" by picking the most recent thing when several fit.
- Extracting a rich outcome and quietly dropping the one "don't…" they included.
