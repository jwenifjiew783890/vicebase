---
type: stable
category: project
project: Vision
status: active
last_verified: 2026-09-03
confidence: high
---

# 09 — Vision (current, canonical)

## The fundamental fact

```
OPEN WEBUI = VISION
```

Not "Vision + Open WebUI". Vision **is** the Open WebUI codebase, customised
in place. No second frontend, no second backend, no Vision orchestration
layer. `[user 2026-09-03]` `[verified 2026-09-03]`

| | |
| --- | --- |
| Base | Open WebUI **v0.11.3** |
| Upstream commit | `2a960a59fe1dbbd35282f0556b3666d81102e781` |
| Repo | `D:\vision` |
| Runs on | `http://127.0.0.1:8080` |
| Licence basis | Open WebUI Licence clause 4(i) — single-user deployment under 50 users |

`[verified 2026-09-03]` — see `VISION.md` in the repo.

## Architectural principle

> **Specialised software does specialised jobs. Vision unifies the user
> experience.** `[user 2026-09-03]`

Vision reuses Open WebUI's existing extension points — Tools, Functions,
Skills, MCP, OpenAPI — rather than growing a bespoke plugin or agent
framework. `[user 2026-09-03]`

## Phase status

| Phase | Scope | State |
| --- | --- | --- |
| 1 | Rebrand Open WebUI → Vision (branding, theme, verified baseline) | **Done** 2026-09-02 |
| 2.1 | Obsidian integration via native MCP | **Done** 2026-09-03 |

`[verified 2026-09-03]`

### Phase 2.1 outcome

Obsidian is connected through the plugin's **own native MCP Streamable HTTP
server** — no bridge, no custom code, no Open WebUI source changes. Vision can
search, read, create, append and delete vault notes from chat. Survives
restart. Full write-up: `VISION-OBSIDIAN-INTEGRATION.md` in the repo.
See [[Memory/14 - Decisions & Principles/Decision Log|DEC-2026-09-03-A]].

## External systems (deliberately outside Vision)

Discussed or in progress: **Obsidian** (connected), **n8n** (connected),
OpenCode, OmniVoice, image-generation backends, desktop control, browser
control, Figma, Blender, further MCP servers. `[user 2026-09-03]`

Target shape:

```
Vision
 ├── Models · Agents · Tools · Memory · Automation
 └── External systems
       ├── Obsidian        (knowledge / memory)   ← connected
       ├── n8n             (workflow automation)  ← connected
       ├── OpenCode · OmniVoice
       ├── desktop / browser control
       ├── image generation · Figma · Blender
       └── future systems
```

## Model architecture requirement

Must support local, LAN, API and cloud models across multiple providers, with
runtime/provider separation. **Vision must never be permanently designed around
one model.** `[user 2026-09-03]` `[vault]` — consistent with ADR-004/005 in
[[Vision Architecture Decisions]].

## Related

[[Memory/09 - Projects/Vision - Abandoned Electron Build|Historical: the abandoned Electron build]] ·
[[Memory/10 - Technical Environment/Technical Environment|10 — Technical Environment]] ·
[[Vision Architecture Decisions]]
