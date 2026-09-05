---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# Documentation Practice

Writing documentation that stays true and gets read - which is mostly about choosing what not to write.

## Write less, and put it closer to the code

Every document is a maintenance obligation. A wrong document is worse than a missing one,
because it is trusted and wastes the reader's time twice.

So the first question is never "what should we document?" but **"what can we make
self-documenting instead?"** A test, a type, a schema, a validated config or a well-named
function cannot drift silently; a paragraph can.

Ranked by how well it stays true: executable (tests, types, schemas) > adjacent (docstrings,
comments) > structural (README, ADR) > detached (a wiki page far from the code).

## What must be written

- **README** - what this is, how to run it, how to test it, where config lives. The first thing
  anyone reads, human or agent.
- **Why, for anything non-obvious** - an ADR, or a comment. Recoverable from nowhere else.
- **Interface contracts** - arguments, return shape, errors raised, preconditions.
- **Operational knowledge** - start, stop, health, logs, recovery. Most neglected, most needed
  under pressure.
- **Constraints not visible locally** - "must stay under 4 KB because the caller puts it in a
  header".

## What not to write

- Anything the code already says clearly
- Step-by-step guides for stable, discoverable UIs
- Architecture documents describing an aspiration rather than the system
- Anything you will not maintain

## Keeping it true

- **Update docs in the same change** as the code. A separate documentation task never happens.
- **Date it and own it.** A page with a date and a name can be assessed; an undated one is
  trusted or ignored arbitrarily.
- **Test the examples.** A code sample in CI cannot rot. Doc tests are documentation with a
  guarantee.
- **Generate what can be generated** - API schemas, CLI help, configuration references. Anything
  maintained beside the code will drift from it.
- **Delete aggressively.** A stale page removed is an improvement.

## Writing for the reader you have

Under pressure, mid-task, scanning. So:

- **The answer first**, context after.
- **Concrete over abstract** - real values, real paths, real commands.
- **Short sentences and short sections.**
- **Say what will go wrong**, not only the happy path. This is the highest-value paragraph in
  most technical documents.
- **Name the version.** Behaviour without a version is not a fact.

## Documenting for agents

An agent reads like a new engineer with less ability to ask. That raises the value of:

- explicit rules rather than implied conventions
- worked examples with real values
- known failure modes stated plainly
- exact commands including the working directory
- versions, since it cannot see what is installed
- **provenance** - so it can distinguish a documented fact from a practitioner opinion

This vault is built on those principles; see
[[Coding Knowledge/99 - Sources & Provenance|Sources & Provenance]].

## Failure modes

- **Documentation as a separate task**, therefore never done.
- **Aspirational architecture docs** describing what was intended.
- **Untested examples** that no longer run.
- **No dates, no owners.**
- **Tutorial written as reference**, or the reverse - neither is usable.
- **Documenting the obvious** while the non-obvious constraint stays in someone's head.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Documentation|Documentation]]
- [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]]
- [[Coding Knowledge/01 - Software Engineering/Maintainability|Maintainability]]

## Sources

- Diataxis documentation framework by Daniele Procida - <https://diataxis.fr/>; restated, not reproduced. Practitioner synthesis otherwise.
