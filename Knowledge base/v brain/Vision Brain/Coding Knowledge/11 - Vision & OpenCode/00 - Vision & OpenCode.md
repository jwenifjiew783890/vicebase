---
type: MOC
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Vision & OpenCode

This stack specifically: what it is, what it must not become, and what has already been learned the hard way.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

> [!warning] Evidence grade and expiry
> This section is **project-specific fact**, measured on this machine. It is the most useful
> section for a task inside this stack and the **first to go stale** - versions change, ports
> change, decisions are superseded. Every note carries the date it was verified. If a claim here
> contradicts the running system, the running system is right; correct the note.

| Note | Holds |
| --- | --- |
| [[Coding Knowledge/11 - Vision & OpenCode/Vision Architecture\|Vision Architecture]] | What the components are and how they connect |
| [[Coding Knowledge/11 - Vision & OpenCode/OpenCode Workflows\|OpenCode Workflows]] | How coding actually runs |
| [[Coding Knowledge/11 - Vision & OpenCode/MCP Integration Patterns\|MCP Integration Patterns]] | Curating a tool surface safely |
| [[Coding Knowledge/11 - Vision & OpenCode/n8n Integration Patterns\|n8n Integration Patterns]] | The orchestration layer and its sharp edges |
| [[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns\|Obsidian Retrieval Patterns]] | How knowledge is actually retrieved |
| [[Coding Knowledge/11 - Vision & OpenCode/Approved Architectural Decisions\|Approved Architectural Decisions]] | Settled decisions, not open for re-litigation |
| [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints\|Known Constraints]] | Hard limits of the components in use |
| [[Coding Knowledge/11 - Vision & OpenCode/Proven Solutions\|Proven Solutions]] | Fixes verified by real execution |
| [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes\|Known Failure Modes]] | Ways this stack has actually broken |

## The one-line summary

**`OPEN WEBUI = VISION`.** Obsidian is the knowledge; n8n orchestrates; OpenCode does the
coding. Nothing is duplicated into a second store, and no coding engine exists inside Vision.
