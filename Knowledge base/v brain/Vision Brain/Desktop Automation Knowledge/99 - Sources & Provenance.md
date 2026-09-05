---
type: note
domain: Desktop Automation Knowledge
section: root
created: 2026-09-04
---

# Sources & Provenance

Where this domain's claims come from, how strong each kind is, and what was copied vs. derived.

Part of [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]].

## The three kinds of claim

Every note mixes these, and they carry different weight. **Never present one as another.**

| Kind | Weight | How it is marked |
| --- | --- | --- |
| **Upstream method** | A working reference design's approach — reasoned, not a guarantee for Vision's future executor | Attributed to the Hermes computer-use SKILL |
| **Platform fact** | Documented Windows behaviour, true regardless of executor | Cited to Microsoft Learn |
| **Project-verified** | Confirmed by Vision on this machine | Labelled *Vision-verified* + date |

> [!warning] The project-verified column is currently empty
> Vision has **no desktop-control executor installed** and has **run no desktop-automation tests**.
> Nothing in this domain is *Vision-verified*. Everything is upstream method or platform fact. When
> a desktop executor is eventually chosen and tested, record what was confirmed here with a date —
> and only then call it verified. This honesty is deliberate: the user's standing rule is *never
> claim something works when it has not been tested* ([[Identity/00 - Identity|Identity]]).

## Primary source — desktop method

**Hermes computer-use SKILL**
- Source name: Hermes Agent — `computer-use` skill
- Repository: <https://github.com/NousResearch/hermes-agent>
- File: <https://github.com/NousResearch/hermes-agent/blob/main/skills/autonomous-ai-agents/computer-use/SKILL.md>
- Raw: <https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/autonomous-ai-agents/computer-use/SKILL.md>
- Skill version: **2.0.0** · Platforms: macOS, Windows, Linux · Category: desktop automation
- License: **MIT** — `LICENSE` states "Copyright (c) 2025 Nous Research"
- Author/org: **Nous Research** (SKILL metadata also credits Francesco Bonacci / `f-trycua`)
- Retrieved: **2026-09-04** (from `main`; no pinned commit recorded — re-fetch to pin)
- How used: **summarised and derived.** Concepts restated in original prose — capture→act→verify
  loop, capture modes (SOM/vision/AX), background operation, accessibility grounding, the input
  action set, structured verdicts, the escalation ladder, recovery, and the safety boundaries.
  **No SKILL text copied verbatim.** Hermes-specific implementation details (exact CLI/tool
  signatures, install commands, non-Windows specifics) were deliberately **not** imported.
- Role in Vision: **reference material** for how a future desktop executor should be reasoned
  about. Not an installed component. Hermes is the *preferred, not chosen* candidate for the
  self-improving layer — see [[Agents/Self-Improving Agent Layer — Requirements|Requirements]].

## Primary source — Windows platform behaviour

**Microsoft UI Automation documentation**
- *UI Automation Control Patterns Overview* — <https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-control-patterns-overview>
- Docs source commit: `156931bb` (dotnet/docs) · Retrieved **2026-09-04**
- License: Microsoft docs are © Microsoft, reusable under **CC BY 4.0** (Microsoft Learn terms).
- How used: **summarised and derived.** The control-pattern list, their semantics, the
  providers/clients model, dynamic pattern availability, and element-property identity are restated
  from the docs. For the latest API, the page itself points to *Windows Automation API: UI
  Automation* (`learn.microsoft.com/windows/win32/winauto/entry-uiauto-win32`).
- Role in Vision: the platform truth desktop grounding relies on. Verify against the current docs
  for the machine's Windows build.

## How external material is used here

**Nothing is copied verbatim.** The method source is MIT (reuse permitted with attribution) and the
platform source is CC BY 4.0 (reuse permitted with attribution) — but a knowledge base that mirrors
its sources becomes a stale copy of documents better maintained upstream. So, as everywhere in this
vault: **synthesise and attribute, never paste.** See the
[[Coding Knowledge/99 - Sources & Provenance|Coding Knowledge]] and
[[3D & Blender Knowledge/99 - Sources & Provenance|3D & Blender]] equivalents.

## What is deliberately not here

- **No install/runtime instructions** for any desktop executor. Vision installs nothing in this
  task; when it does, that belongs in [[Integrations/00 - Integrations|Integrations]], not here.
- **No non-Windows specifics** beyond noting that accessibility names differ per OS. Vision's
  target is Windows 11.
- **No claim that Vision can control the desktop today.** It cannot; see the warning above.
- **No Hermes-specific tool signatures** copied as if they were Vision's interface.

## Reviewing a claim in this domain

1. Check whether it is labelled **upstream method**, **platform fact**, or **Vision-verified**.
2. Upstream method → treat as a strong prior for how to build/drive an executor, not as tested fact.
3. Platform fact → follow the Microsoft citation and confirm against the current Windows build.
4. Vision-verified → check the date; re-confirm if the stack changed. (None exist yet.)
5. If a claim turns out wrong, correct the note and record what taught you.

## Related

[[Desktop Automation Knowledge/00 - Desktop Automation Index|Domain index]] ·
[[Browser Knowledge/99 - Sources & Provenance|Browser Knowledge provenance]] ·
[[Coding Knowledge/99 - Sources & Provenance|Coding Knowledge provenance]]
