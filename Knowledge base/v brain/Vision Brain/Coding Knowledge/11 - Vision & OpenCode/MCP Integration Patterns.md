---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# MCP Integration Patterns

Connecting a capability to a model in this stack, and the decisions that keep the surface safe.

## Curate, never import

The default temptation with any OpenAPI or MCP surface is to import it whole. That was
evaluated and rejected here on evidence.

> [!danger] The finding that settled it
> OpenCode's OpenAPI schema has **188 operations**. Imported raw, the model would receive tools
> including `auth.set`, `config.update`, `credential.remove`, `global.dispose` - and
> **`permission.reply`, which would let Vision's model approve OpenCode's own permission
> prompts.** That does not weaken the approval mechanism; it removes it entirely.

The surface was curated to **two tools** instead, with n8n adapting between them.

The same reasoning applies to Obsidian: its MCP server exposes 16 tools, of which **6 read-only
tools are enabled** (`vault_read`, `vault_list`, `vault_get_document_map`, `search_query`,
`search_simple`, `tag_list`) and **10 mutating ones are denied**, including `vault_write`,
`vault_delete`, `vault_move` and `command_execute`.

**The rule: expose what the task needs, deny the rest, and re-examine after every dependency
update.** Fewer tools also improves selection accuracy - the security and quality arguments point
the same way.

## Transport

Open WebUI **0.11.3 supports MCP Streamable HTTP only**. Any server offering stdio alone needs a
bridge, which this stack deliberately avoids by using servers that speak Streamable HTTP
natively.

The MCP specification (revision 2026-07-28) defines exactly two standard transports - stdio and
Streamable HTTP - and the newer revision is stateless with per-request capability negotiation.
When an integration behaves strangely, **check which revision each side implements** before
debugging the transport.

## Trust

The specification states plainly that tool descriptions and annotations are **untrusted** unless
the server is trusted. A tool description is text from another party that lands in the model's
context and can carry instructions.

In practice here:
- Both MCP servers are local and operated by the user, so the trust question is answered by
  provenance, not by inspection.
- The tool surface is still curated, because trust in the server does not make 188 tools a good
  idea.
- TLS verification stays **on** for Obsidian's self-signed local certificate; the CA is trusted
  via `NODE_EXTRA_CA_CERTS` rather than verification being disabled.

## Authentication

- **n8n MCP endpoint**: bearer auth.
- **OpenCode server**: HTTP Basic, password generated (48 characters) and held outside source.
  Verified: unauthenticated -> 401.
- **Obsidian**: bearer token, stored in `webui.db` and in n8n's encrypted credential store.

**No credential appears in a prompt, a workflow name, a node label, registry metadata, a source
file or a commit.** That is a stated constraint of this project, not a general preference.

## Bounding results

Any MCP tool can return more than a context window holds. Bound at the tool boundary:

- The Knowledge Retriever caps at **6 notes per domain** and **6,000 characters** assembled.
- Anything that could return a large document truncates and says that it truncated, so the model
  knows its view is partial.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/MCP|MCP]]
- [[Coding Knowledge/04 - Agent Engineering/Tool Selection|Tool Selection]]
- [[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]]

## Sources

- MCP specification revision 2026-07-28 - <https://modelcontextprotocol.io/specification/latest> (MIT, fetched 2026-09-03). The 188-operation finding and the curation decision are recorded in `D:\opencode\README.md`. Tool allow/deny lists read from `opencode.jsonc` on 2026-09-03.
