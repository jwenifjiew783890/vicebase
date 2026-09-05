---
type: note
domain: Browser Knowledge
created: 2026-09-04
---

# Sources & Provenance

Where this domain's claims come from, how strong each kind is, and what was copied vs. derived.

Part of [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]].

## The three kinds of claim

| Kind | Weight | How it is marked |
| --- | --- | --- |
| **Upstream capability** | What Auto Browser's own repo/docs describe | Attributed to Auto Browser + version |
| **Reference method** | General or Browser-Use methodology — informational | Labelled *reference only* |
| **Project-verified** | Confirmed by Vision's own integration testing | Labelled *Vision-verified* + date |

> [!warning] The project-verified column is currently empty
> Vision has **not** integration-tested Auto Browser (or any browser executor) end-to-end.
> Everything here is **upstream capability** or **reference method**. Nothing is *Vision-verified*.
> When Vision registers Auto Browser as an MCP server and drives a real page, record what was
> confirmed — port, transport, session limits, tool names, approval behaviour — here, with a date.
> Until then, verify before you rely. The user's standing rule is *never claim something works when
> it has not been tested* ([[Identity/00 - Identity|Identity]]).

## Primary source — the production executor

**Auto Browser**
- Source name: Auto Browser
- Repository: <https://github.com/LvcidPsyche/auto-browser>
- Files used: `README.md`, `docs/architecture.md`, `docs/mcp-clients.md`
  (<https://github.com/LvcidPsyche/auto-browser/tree/main/docs>)
- Version: **~v1.5.0** (release highlights; no pinned commit recorded — re-fetch to pin)
- License: **MIT** (stated in repo)
- Author/org: **LvcidPsyche**
- Retrieved: **2026-09-04**
- How used: **summarised and derived.** MCP-native control-plane architecture, controller +
  browser-node, Playwright `launchServer`/`connect`, transports and `127.0.0.1` binding, tool
  profiles (`curated`/`full`) and the `browser.*` / `harness.*` tools, the session/auth-profile/
  `docker_ephemeral`/noVNC model, the perception→act→verify loop, and the security layer
  (allowlist, approvals, audit, PII scrubbing, Witness receipts, compliance presets). **No repo
  text copied verbatim**; config keys and tool names are quoted only as identifiers.
- Role in Vision: **the production browser executor.** This is the source of truth for browser
  *execution*. It is not yet installed/registered in Vision — that is a future integration step,
  not part of this knowledge task.

## Supplemental source — reference only

**Browser Use SKILL**
- Source name: Browser Use — `browser-use` skill
- Repository: <https://github.com/browser-use/browser-use>
- File: <https://github.com/browser-use/browser-use/blob/main/skills/browser-use/SKILL.md>
- Raw: <https://raw.githubusercontent.com/browser-use/browser-use/main/skills/browser-use/SKILL.md>
- License: **MIT** — `LICENSE` states "Copyright (c) 2024 Gregor Zunic"
- Author/org: **Browser Use** (Gregor Zunic / Magnus Müller); homepage <https://browser-use.com>
- Retrieved: **2026-09-04**
- How used: **summarised and derived**, for *general methodology only* — when to use a browser vs.
  a plain fetch, capture/observe before acting, prefer accessibility trees over screenshots,
  first-navigation-opens-the-tab discipline, and remote-browser trade-offs. **No installation or
  runtime instructions imported as Vision's setup.**
- Role in Vision: **reference only — NOT Vision's browser executor.** Kept in
  [[Browser Knowledge/10 - Reference Methodology/Browser Use (Reference Only)|the reference subfolder]]
  and labelled as such wherever cited. Vision uses **Auto Browser** for execution.

## How external material is used here

**Nothing is copied verbatim.** Both sources are MIT (reuse permitted with attribution), but a
knowledge base that mirrors its sources becomes a stale copy. As everywhere in this vault:
**synthesise and attribute, never paste.** See the
[[Coding Knowledge/99 - Sources & Provenance|Coding Knowledge]] and
[[Desktop Automation Knowledge/99 - Sources & Provenance|Desktop Automation]] equivalents.

## What is deliberately not here

- **No full duplication of either project.** Concepts and the operational model only — not the code,
  not the whole docs tree.
- **No Browser Use as an executor.** It is reference methodology; the executor is Auto Browser.
- **No install/runtime setup** for Auto Browser as if it were done. Registration is a future
  [[Integrations/00 - Integrations|Integrations]] step.
- **No claim that any of this is tested in Vision.** It is not, yet.

## Reviewing a claim in this domain

1. Check the label: **upstream capability**, **reference method**, or **Vision-verified**.
2. Upstream capability → confirm against the live Auto Browser server / current docs before relying.
3. Reference method → useful reasoning, not a Vision guarantee; the executor is still Auto Browser.
4. Vision-verified → check the date; re-confirm if the stack changed. (None exist yet.)
5. If a claim turns out wrong, correct the note and record what taught you.

## Related

[[Browser Knowledge/00 - Browser Knowledge|Domain index]] ·
[[Desktop Automation Knowledge/99 - Sources & Provenance|Desktop Automation provenance]] ·
[[Coding Knowledge/99 - Sources & Provenance|Coding Knowledge provenance]]
