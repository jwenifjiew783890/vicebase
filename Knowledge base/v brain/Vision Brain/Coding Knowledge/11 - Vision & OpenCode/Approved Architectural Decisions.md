---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Approved Architectural Decisions

Settled decisions. These are not open for re-litigation during a task; if one needs to change, that is its own conversation.

> [!important] How to treat this note
> If a task seems to require violating one of these, **say so and stop**, rather than working
> around it. A constraint quietly bypassed is worse than a constraint challenged.

## Identity

**`OPEN WEBUI = VISION`.** Vision is a customised Open WebUI installation. There is no separate
Vision application, backend or core. The earlier Electron/React build is **abandoned** - not
paused, not a fallback. Do not revive it, reference it as current, or partially resurrect it.

## Knowledge

**Obsidian is the single source of truth.** Nothing is copied into Open WebUI Knowledge or into
any second store for retrieval purposes.

**No full-vault embedding or sync system.** Retrieval is on demand and domain-scoped. The
reasoning is in
[[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]].

**One Obsidian MCP server.** The Obsidian plugin *is* the MCP server. No bridge, no second
server, no proxy.

**Domain separation is structural.** `Memory/` (the user model, which decays) and the knowledge
domains (which do not) must not be collapsed. Personal preference is not evidence about the
world; a domain fact is not a fact about the user.

## Coding

**Coding runs through OpenCode.** No coding engine is built inside Vision, and OpenCode is not
replaced.

**The n8n wrapper adapts; it does not reimplement.** n8n curates the surface and enforces the
project allowlist. It does not do the coding.

**Writes are confined and doubly enforced** - the n8n `Resolve Project` allowlist and OpenCode's
own `external_directory: deny`.

## Orchestration

**The n8n agent hierarchy is locked.** Extend it by adding a registry entry; never restructure
`VISION - AGENTS`.

**`agent-registry.json` is the single source of truth**, and the architecture map is generated
from it so documentation cannot drift.

**No fake placeholders.** A FUTURE slot is marked `enabled: false`, `status: FUTURE`, and
`executor: NONE CONNECTED` - it is a declared gap, not a pretend capability.

**Plan-then-execute, not an agent tool loop.** Originally forced by the provider rejecting
LangChain's tool-result shape; retained because determinism, auditability and bounded cost
proved more valuable than flexibility.

## Security

**Certificate verification stays on.** Obsidian's self-signed local certificate is *trusted* via
`NODE_EXTRA_CA_CERTS`. Disabling verification is not an option.

**Credentials live in their own encrypted stores** - n8n credentials, environment variables, the
OpenCode password. Never in prompts, workflow names, node labels, registry metadata, source
files, or commits.

**`webui.db` is never reset or recreated.** It holds configuration, users, chats and the Obsidian
MCP key.

## Verification

**Static configuration is not proof.** A workflow that looks correct has not run. Claim success
only from a real execution with real output.

**Report gaps explicitly.** If a step was skipped or a test not run, say so. An unverified claim
of verification is worse than an admitted gap.

## Status of things not yet built

A **self-improving agent layer** is an approved requirement only. Nothing has been selected or
built. Recording that honestly matters more than a design sketch - see
[[Coding Knowledge/04 - Agent Engineering/Self-Improvement|Self-Improvement]].

---

## See also

- [[Coding Knowledge/04 - Vision Engineering Constraints|Vision Engineering Constraints]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]
- [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]]

## Sources

- Decisions recorded in the vault at [[Memory/14 - Decisions & Principles/Decision Log|the Decision Log]], in `D:\n8n\workflows\AGENT-REGISTRY.md`, and in `D:\opencode\README.md`. Restated here as constraints for engineering tasks.
