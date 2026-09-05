---
type: episodic
category: events
last_verified: 2026-09-03
confidence: high
---

# 15 — Important Events

Episodic memory: things that happened, when. Only events with a reliable
source and date.

---

## 2026-09-02 — Vision Phase 1 complete: Open WebUI rebranded to Vision

Open WebUI v0.11.3 customised in place — branding, theme, icon set, verified
running baseline. Deliberately excluded: all integrations, deferred to later
phases.

Licence position: the rebrand relies on Open WebUI Licence clause 4(i)
(single-user deployment, under 50 users in any rolling 30 days). If Vision is
ever deployed beyond that, branding must be reverted or a licence obtained.

`[verified 2026-09-03]` — repo `VISION.md`

---

## 2026-09-02 → 2026-09-03 — The Electron Vision build was abandoned

The standalone Electron/React/TypeScript application (steps 1–6 of 7 complete)
was dropped in favour of the Open WebUI base.
See [[Memory/09 - Projects/Vision - Abandoned Electron Build|the historical record]].

`[user 2026-09-03]` — exact date of the decision `UNKNOWN`.

---

## 2026-09-03 — n8n connected to Vision over MCP

A self-hosted n8n instance (`127.0.0.1:5678`) was registered in Vision as an
MCP tool server (`n8n_vision_test`) and a workflow executed successfully
through it.

`[user 2026-09-03]` `[verified 2026-09-03]` — the registration and a successful
MCP session were observed directly.

Also stated by the user, not independently verified: n8n AI Assistant
configured, Docker sandbox configured, NVIDIA-hosted GPT-OSS 120B tested.

---

## 2026-09-03 — Vision Phase 2.1 complete: Obsidian connected

Obsidian 1.13.7 + *Local REST API with MCP* v5.1.0 connected to Vision as a
native MCP tool server. Verified end-to-end from the chat interface: tool
discovery, vault search, note read, note create, note append, read-back,
delete. Survives restart with authentication intact.

Architecture: no bridge process, no custom Vision code, **zero Open WebUI
source changes**. TLS verification kept on via a custom CA bundle.

`[verified 2026-09-03]` — repo `VISION-OBSIDIAN-INTEGRATION.md`.
Decisions: [[Memory/14 - Decisions & Principles/Decision Log|DEC-2026-09-03-A and -B]].

---

## 2026-09-03 — This memory system created

The `Memory/` structure was initialised in the Vision Brain vault from the
existing vault notes, the user's memory-initialisation brief, and facts
verified on the machine. No chat history export was supplied.

---

## Template

```
## YYYY-MM-DD — Title

What happened, in a few lines.

[source] — evidence
```
