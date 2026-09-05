---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Obsidian Retrieval Patterns

How knowledge is actually fetched from the vault, and the constraints that shape how notes must be written.

## Two consumers, two mechanisms

**1. OpenCode - search and read, on demand.** The primary path for coding. Its agents have
`search_query`, `search_simple`, `vault_list`, `vault_get_document_map` and `vault_read`, and
their prompts instruct them to consult the vault for documented standards before writing code.
They can navigate the **full hierarchy**, at any depth.

**2. The n8n Knowledge Retriever - inject a bounded block.** Used by `knowledge_mode: inject`
agents. It has hard limits that directly constrain how a domain folder must be laid out:

| Limit | Value | Consequence |
| --- | --- | --- |
| Listing depth | **Top level only** | Subfolders are skipped entirely |
| Notes per run | **6** | Only the first six top-level `.md` files are read |
| Assembled size | **6,000 characters** | Later notes are dropped |
| Ranking | **None** | `query` is accepted but not used to rank - order is the listing order |

**This is why `Coding Knowledge/` has exactly six numbered notes at its root** and everything
else in subfolders: the six always-applicable notes are what an inject-mode consumer would
receive, and the depth is reached by search.

The Coding Agent itself is `knowledge_mode: executor`, so it uses path 1 - but the layout serves
both.

## How the retriever behaves

- Folders arrive as **data from the registry**; nothing in the shared components names a domain.
  That is what lets a new domain be added without touching them, and it has been verified by
  grepping the shared components for domain names.
- A folder that does not exist yet **404s and is dropped** - so a domain can be declared before
  its notes exist.
- Obsidian returns a note as **plain markdown**, and n8n wraps a non-JSON body as `{data: "..."}`.
  `content` is only present when the API answers with JSON. Read `j.data || j.content`.
- It **never returns zero items** - a sentinel is emitted instead, because an empty node would
  silently halt the calling agent.

## What this means for writing notes

1. **Notes must be readable whole.** They are fetched entire, not chunked. A note that only makes
   sense alongside three others is a poor unit of retrieval.
2. **Front-load the operative content.** With a 6,000-character assembly budget, the useful part
   must be near the top.
3. **Self-contained sections.** Include enough context that a section read in isolation is
   meaningful.
4. **Structure is the index.** With no relevance ranking in the inject path, and search as the
   entry point in the OpenCode path, MOC notes and clear titles do the work a reranker would
   otherwise do.
5. **Scope by folder.** Domain separation is enforced by which folders an agent declares -
   metadata filtering by another name, and it is what prevents cross-domain contamination.

## Why the vault is not embedded

Deliberate, and worth restating because it looks like an omission:

- The corpus is **structured and navigable**. Reading three known notes is more accurate,
  cheaper and far more debuggable than similarity search over their fragments.
- Embedding would create a **second store** that must be kept in sync - a synchronisation
  problem, a staleness problem, and a duplicate source of truth.
- Obsidian already has its own search index, reachable over the same API.
- **Obsidian stays the single source of truth**, which is a stated constraint of this project.

See [[Coding Knowledge/03 - AI Engineering/RAG|RAG]] for the general form of this argument -
*when not to build a RAG pipeline*.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Retrieval|Retrieval]]
- [[Coding Knowledge/03 - AI Engineering/RAG|RAG]]
- [[Coding Knowledge/11 - Vision & OpenCode/n8n Integration Patterns|n8n Integration Patterns]]

## Sources

- Retriever behaviour read directly from `D:\n8n\workflows\vision-knowledge.json` on 2026-09-03 (nodes `Plan Reads` and `Assemble Knowledge` carry the limits in code). OpenCode tool grants from `opencode.jsonc`.
