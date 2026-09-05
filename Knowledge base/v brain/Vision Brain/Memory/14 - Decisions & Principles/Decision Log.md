---
type: stable
category: decisions
last_verified: 2026-09-03
confidence: high
---

# 14 — Decisions & Principles

Durable architectural decisions with their reasoning. The formal ADR set lives
in [[Vision Architecture Decisions]] (ADR-001 … ADR-012) and remains valid;
this note records decisions made **since**, plus the standing principles.

## Standing principles

> **Specialised software does specialised jobs. Vision unifies the user
> experience.**

> **Prefer native MCP where supported** — avoid unnecessary adapters and custom
> integration code.

> **Reuse before rebuilding.** Vision's value is integration and product
> experience, not reimplementation.

`[user 2026-09-03]` `[vault]`

---

## DEC-2026-09-02-A — Open WebUI *is* Vision

**Date:** 2026-09-02
**Context:** A standalone Electron/React/TypeScript Vision app had reached
step 6 of 7 (see [[Memory/09 - Projects/Vision - Abandoned Electron Build|the historical record]]).
**Decision:** Vision becomes the Open WebUI v0.11.3 codebase, customised in
place. The Electron build is abandoned and must not be revived.
**Reason:** Avoid maintaining a duplicate application; Open WebUI already
provided what the Electron build was rebuilding by hand.
**Alternatives:** Continue the Electron build; wrap Open WebUI inside it.
**Result:** Phase 1 rebrand completed 2026-09-02.
**Status:** ACTIVE

---

## DEC-2026-09-03-A — Obsidian via the plugin's own native MCP server

**Date:** 2026-09-03
**Context:** Obsidian needed to become Vision's external knowledge layer.
**Decision:** Register the Obsidian *Local REST API with MCP* plugin (v5.1.0)
directly as an MCP tool server at `https://127.0.0.1:27124/mcp`. No bridge
process, no custom Vision code, no Open WebUI source changes.
**Reason:** The plugin already *is* an MCP Streamable HTTP server — exactly the
transport Vision supports. A bridge would have been pure overhead.
**Alternatives:** stdio MCP community server + adapter (rejected — Vision has
no stdio transport); an OpenAPI wrapper over the REST API (rejected —
unnecessary).
**Result:** Search/read/write/delete verified from chat; survives restart.
**Status:** ACTIVE

---

## DEC-2026-09-03-B — Least privilege on the Obsidian tool surface

**Date:** 2026-09-03
**Decision:** Expose 15 of the plugin's 16 MCP tools; block `command_execute`.
**Reason:** `command_execute` runs any of ~195 arbitrary Obsidian commands
including `app:delete-file` — far beyond the search/read/write the integration
needs.
**Result:** Enforced via the connection's tool filter; reversible in Admin
Settings.
**Status:** ACTIVE

---

## Inherited decisions (unchanged, still binding)

| Decision | Reason |
| --- | --- |
| Do not rebuild mature capabilities | Use specialised software instead |
| n8n remains external | It is the workflow automation engine |
| Obsidian remains external | It is the persistent knowledge store; the vault is never copied into Vision |
| Vision is not locked to one model or runtime | ADR-004, ADR-005 |
| Plugins/integrations stay outside core | ADR-008; removal must not break Vision |
| Hardware advises, never constrains architecture | ADR-010 |

## Template for future decisions

```
Decision:
Date:
Context:
Reason:
Alternatives considered:
Result:
Status:
```
