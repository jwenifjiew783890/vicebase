---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Documentation

What must be written down, where it belongs, and why most documentation fails.

## The failure mode that defines the topic

**Documentation drifts and then lies.** A wrong document is worse than a missing one: it is
trusted, and it wastes the reader's time twice - once believing it, once discovering it was
false. So the first design question for any document is *what keeps this true?*

Ranked by how well they stay true:

1. **Executable** - tests, type signatures, schemas, CI-checked examples. Cannot drift silently.
2. **Adjacent** - docstrings and comments next to the code, updated in the same diff.
3. **Structural** - READMEs and ADRs about things that change slowly.
4. **Detached** - wiki pages far from the code. Assume these are stale unless dated and owned.

Push knowledge as far up that list as it will go. Prefer a test that demonstrates usage over a
paragraph describing it.

## The four kinds, which are not interchangeable

Confusing these is why so much documentation is unusable.

| Kind | Reader | Purpose |
| --- | --- | --- |
| **Tutorial** | New, learning | Get a first success, hand-held |
| **How-to guide** | Competent, has a task | Achieve one specific goal |
| **Reference** | Knows what they need | Look up exact behaviour, complete and dry |
| **Explanation** | Wants to understand | Why it works this way, what was rejected |

A reference page written as a tutorial is unusable for lookup; a tutorial written as reference
teaches nobody.

## What must exist

- **README**: what this is, how to run it, how to test it, where the config lives. First thing
  anyone reads, including an agent.
- **The why for non-obvious decisions**: an [[Coding Knowledge/09 - Engineering Practices/ADRs|ADR]]
  or a comment. Code shows what; only a human record shows why the obvious alternative was
  rejected.
- **Interface contracts**: the arguments, the return shape, the errors raised, and the
  preconditions the caller must satisfy.
- **Operational knowledge**: how to start, stop, check health, read the logs, recover. This is
  what is needed under pressure, and it is almost always the most neglected.
- **The constraints that are invisible locally**: "this must stay under 4 KB because the caller
  puts it in a header."

## Comments

Write comments for the **why**, the **why not**, and the **non-local constraint**. Never to
restate the code.

Worth writing:
- the reason for an unusual approach
- the alternative that was tried and failed, and how it failed
- the bug this guard prevents
- the assumption that would break this
- a link to the issue, spec or incident behind the line

Not worth writing: `// increment i`, or a header block restating the signature.

## Documentation for agents specifically

An agent reads documentation the same way a new engineer does, but with less ability to ask.
That raises the value of:

- **explicit constraints** stated as rules, not implied by convention
- **worked examples** with real values, not `foo`/`bar`
- **known failure modes** stated plainly
- **exact commands** including the working directory
- **versions**, since an agent cannot see which one is installed

This vault is built on that premise - see
[[Coding Knowledge/00 - Coding Knowledge|the domain root]].

---

## See also

- [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]]
- [[Coding Knowledge/09 - Engineering Practices/Documentation Practice|Documentation Practice]]
- [[Coding Knowledge/01 - Software Engineering/Maintainability|Maintainability]]

## Sources

- The four-kinds taxonomy is the Divio/Diataxis framework by Daniele Procida - <https://diataxis.fr/>; restated here, not reproduced. Practitioner synthesis otherwise.
