---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Agent Memory

What persists between sessions, where it lives, and why most memory systems fail by remembering too much.

## Four different things called "memory"

Conflating them is the source of most confusion.

| Kind | Lifetime | Holds | Mechanism |
| --- | --- | --- | --- |
| **Working** | One turn | The context window | Nothing to build - it is the prompt |
| **Episodic** | A session | What happened this session | Conversation state, summarised |
| **Semantic** | Indefinite | Durable facts about the user and world | A store the agent reads and writes |
| **Procedural** | Indefinite | How to do things - skills, standards | Documents, retrieved on demand |

Most "give the agent memory" requests mean **semantic**. Most value in practice comes from
**procedural** - a good standards corpus changes behaviour more than remembering a preference.

## The failure mode that defines the topic

**Remembering too much.** A system that stores everything accumulates stale, contradictory and
trivial facts, and retrieval then surfaces noise that actively degrades answers. Memory quality
falls as volume rises, past a fairly early point.

So the design questions in order are: *what is worth storing at all*, *what makes it stale*, and
*what removes it*.

## Design rules

**1. Write few things, deliberately.** Durable preferences, decisions and constraints - not
transcript. "Prefers blunt answers" is memory; "asked about X on Tuesday" is a log.

**2. One fact per record.** Atomic records can be updated, contradicted and deleted
individually. A blob cannot.

**3. Record provenance and time.** When was this learned, from what, how confident. Without
this, you cannot resolve a contradiction later, and you cannot decay.

**4. Contradiction is an event to resolve, not to average.** When new information conflicts with
old, keep the new, keep the old as history, and record that it changed. Never blend them.

**5. Decay, and prefer derived decay.** Relevance falls with age at different rates for
different facts. Deriving strength from age at read time avoids any background job -
*this stack does exactly that: decay lives in a tool and strength is computed, so nothing runs
on a timer.*

**6. Retrieve scoped, not wholesale.** Fetch what the current task needs. Injecting the whole
memory store is the fastest way to make a system worse.

**7. Separate memory from knowledge.** A personal preference is not evidence about the world,
and a domain fact is not a fact about the user. *This vault enforces that separation
structurally between `Memory/` and the knowledge domains, and it must not be collapsed.*

**8. Make it inspectable and correctable.** The user must be able to see what is remembered and
delete it. Memory that cannot be audited becomes a source of unexplainable behaviour.

## Storage choices

- **Files in a structured hierarchy** - inspectable, diffable, greppable, editable by a human.
  Best default for small volumes, and what this stack uses.
- **A database** - when volume, querying or concurrency demand it.
- **A vector store** - only when the corpus is large enough that navigation fails. Adds
  embedding drift, staleness and opacity.

Choose the simplest that works. A vector store for 200 facts is strictly worse than 200 files.

## Failure modes

- **Storing conversation transcripts as memory.** Volume without value.
- **No deletion path.** A wrong fact becomes permanent, and it will be retrieved forever.
- **Silent overwriting** of a contradicted fact, destroying the history that explains it.
- **Injecting all memory into every prompt** - context burned, quality lowered.
- **No provenance**, so a hallucinated "fact" is indistinguishable from an observed one.
- **Cross-domain contamination** - personal preference leaking into factual retrieval.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]
- [[Coding Knowledge/04 - Agent Engineering/State Management|State Management]]
- [[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]]

## Sources

- Practitioner synthesis. The derived-decay design and the Memory/knowledge separation are this project's, recorded in the vault at `Memory/99 - Memory Rules`.
