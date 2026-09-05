---
type: MOC
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Coding & Engineering Knowledge

The engineering domain of the Vision Brain. Everything Vision and OpenCode consult when they design, write, review, debug or operate software.

Part of [[Vision Brain]].

> [!important] How this domain is meant to be used
> **Retrieval is on demand and scoped.** Nothing here is copied into Open WebUI Knowledge,
> embedded wholesale, or mirrored into another database. OpenCode reaches it live through the
> Obsidian MCP tools (`search_query`, `search_simple`, `vault_list`, `vault_read`) and reads
> only the notes a task actually needs. The vault stays the single source of truth.

## The two shelves

**The six notes at this level are the always-applicable ones.** They are deliberately the only
markdown files in the domain root, because Vision's n8n Knowledge Retriever lists a domain
folder non-recursively and takes at most six notes. Anything an agent should have *by default*
lives here; everything else is reached by search.

| | Note | Read it when |
| --- | --- | --- |
| 01 | [[Coding Knowledge/01 - Engineering Principles\|Engineering Principles]] | Any design or implementation decision |
| 02 | [[Coding Knowledge/02 - Debugging Method\|Debugging Method]] | Something is broken and the cause is unknown |
| 03 | [[Coding Knowledge/03 - Code Review Standards\|Code Review Standards]] | Reviewing a diff, or writing code that will be reviewed |
| 04 | [[Coding Knowledge/04 - Vision Engineering Constraints\|Vision Engineering Constraints]] | Touching anything in the Vision stack |
| 05 | [[Coding Knowledge/05 - Failure Patterns\|Failure Patterns]] | Before committing to an approach |
| 99 | [[Coding Knowledge/99 - Sources & Provenance\|Sources & Provenance]] | Checking where a claim came from |

## Sections

| # | Section | Holds |
| --- | --- | --- |
| 01 | [[Coding Knowledge/01 - Software Engineering/00 - Software Engineering\|Software Engineering]] | Architecture, patterns, modularity, testing, CI/CD |
| 02 | [[Coding Knowledge/02 - Programming & Languages/00 - Programming & Languages\|Programming & Languages]] | Python, JS/TS, C/C++, Rust, shells, SQL, APIs, concurrency, memory |
| 03 | [[Coding Knowledge/03 - AI Engineering/00 - AI Engineering\|AI Engineering]] | LLMs, RAG, tool calling, evaluation, context, MCP |
| 04 | [[Coding Knowledge/04 - Agent Engineering/00 - Agent Engineering\|Agent Engineering]] | Planners, orchestrators, multi-agent, permissions, sandboxing |
| 05 | [[Coding Knowledge/05 - Web & Application Engineering/00 - Web & Application Engineering\|Web & Application]] | Frontend, backend, REST, WebSockets, DBs, authn/authz, caching |
| 06 | [[Coding Knowledge/06 - DevOps & Infrastructure/00 - DevOps & Infrastructure\|DevOps & Infrastructure]] | Docker, WSL, Linux, Windows services, networking, deployment |
| 07 | [[Coding Knowledge/07 - Debugging & Problem Solving/00 - Debugging & Problem Solving\|Debugging & Problem Solving]] | The diagnostic disciplines, one per failure class |
| 08 | [[Coding Knowledge/08 - Code Quality & Review/00 - Code Quality & Review\|Code Quality & Review]] | Review, refactoring, technical debt, security and API review |
| 09 | [[Coding Knowledge/09 - Engineering Practices/00 - Engineering Practices\|Engineering Practices]] | Requirements, system design, ADRs, release and change management |
| 10 | [[Coding Knowledge/10 - Engineering Experience/00 - Engineering Experience\|Engineering Experience]] | Practitioner judgement: heuristics, incidents, trade-offs, what fails |
| 11 | [[Coding Knowledge/11 - Vision & OpenCode/00 - Vision & OpenCode\|Vision & OpenCode]] | This stack specifically — architecture, constraints, proven fixes, known failure modes |
| 12 | [[Coding Knowledge/12 - Reliability Engineering/00 - Reliability Engineering\|Reliability Engineering]] | SLOs, error budgets, toil, on-call, incidents, postmortems, load, stability antipatterns |

## What separates the sections

> [!note] Agent-facing instructions live in the repository, not here
> `D:\vision\AGENTS.md` is the [AGENTS.md](https://agents.md/) file OpenCode reads
> automatically from the project root: identity, run commands, the architectural
> constraints, and a pointer back to this domain. It carries the *rules*; this domain
> carries the *knowledge*. Do not duplicate one into the other.

Sections 01-09 are **transferable engineering knowledge**: true regardless of what is being
built. Section 10 is **practitioner judgement** - heuristics and incident lessons, which are
weaker evidence than a specification but far more useful than nothing, and are labelled as
such. Section 11 is **project-specific fact** about this machine and this stack; it expires
when the stack changes, and it says so.

Never present a section 10 heuristic as if it were a section 01 rule, or a section 11
project fact as if it were general engineering practice.

Section 12 is **extracted from sources that grant no reuse licence**, so every note there
carries a provenance callout separating the source's concepts from our own synthesis. It is
the worked example of the method in [[Coding Knowledge/99 - Sources & Provenance\|Sources & Provenance]].

## Rules for adding to this domain

1. **Actionable or absent.** A note earns its place by changing what an engineer would do.
   Restating a definition does not.
2. **Provenance.** Documented behaviour cites the documentation. Practitioner judgement is
   labelled as judgement. Something learned in this project cites the run that taught it.
3. **Never reproduce a source.** Extract the concept and write original prose.
   Sources granting no reuse licence — the Google SRE books, *Release It!*, most
   engineering books — are read for understanding and written from memory, with the
   concepts credited and nothing copied. Each such note states which ideas are the
   source's and which are ours. Policy and method:
   [[Coding Knowledge/99 - Sources & Provenance\|Sources & Provenance]].
4. **Failure modes are the payload.** Most notes here carry a *Failure modes* section, because
   knowing how something breaks is worth more to an agent than knowing how it works.
5. **Link, do not duplicate.** One concept, one note.
6. **Keep the root at six.** Adding a seventh always-on note means demoting one first.

## Related domains

The coding workflow reaches these sibling domains when a task crosses into them. They are separate
domains on purpose — this domain is not duplicated into them.

- [[Website Development Knowledge/00 - Website Development Index|Website Development Knowledge]] —
  the **design-and-build workflow layer for websites** (planning & IA, UI/UX & design systems,
  Figma, frontend implementation, responsive/accessibility/performance, testing, deployment).
  This domain owns the web *engineering internals* — backend, auth, caching, databases, web
  security, and frontend state/rendering architecture, in
  [[Coding Knowledge/05 - Web & Application Engineering/00 - Web & Application Engineering|section 05]];
  Website Development owns the *design/build workflow* and cross-links back here. **Retrieve it for
  any website design or build task.**
- [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] — the Python that
  drives Blender and the 3D asset pipeline.
- [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]] ·
  [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]] — the
  executors a coding task uses to validate a build and to drive native apps.
