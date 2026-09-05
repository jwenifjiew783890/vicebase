---
type: episodic
category: project-history
project: Vision (v0 - Electron)
status: ABANDONED
superseded_by: "Memory/09 - Projects/Vision"
last_verified: 2026-09-03
confidence: high
---

# 09 — Vision, Abandoned Electron Build (HISTORICAL)

> [!warning] This describes a project that no longer exists.
> The standalone Electron / React / TypeScript Vision application is
> **abandoned and must not be revived.** `[user 2026-09-03]`
> Current Vision is [[Memory/09 - Projects/Vision|Open WebUI v0.11.3]].

Kept because the *reasoning* is still valuable and several vault notes still
describe this build as if it were live.

## What it was

A from-scratch desktop AI application:

- Electron · React · TypeScript · Vite · electron-vite
- Tailwind CSS · Radix UI · Zustand
- contextIsolation, secure preload bridge, explicit IPC allow-list, Zod validation
- Planned: xterm.js + node-pty/ConPTY terminal, Three.js/R3F "Vision Orb"

`[vault]` — [Vision Technical Stack](Projects/Vision/Vision%20Technical%20Stack.md.md)

## How far it got

Steps 1–6 completed: foundation, design system, secure IPC, settings,
application shell, chat UI (with streaming, cancellation, attachments,
history, `ModelProvider` abstraction). Step 7 — the 3D Orb — was next and was
never reached. `[vault]` — [Vision Current Status](Projects/Vision/Vision%20Current%20Status.md.md), [Vision Roadmap](Projects/Vision/Vision%20Roadmap.md.md)

## Why it was abandoned

`[inferred — CONFIDENCE: MEDIUM]` No explicit reason was recorded in the
vault. The decision is consistent with the user's own stated principle —
*prefer mature infrastructure over rebuilding* ([Lessons Learned](Memories/Lessons%20Learned.md.md) #5,
ADR-003) — since Open WebUI already provided chat, models, tools, RAG, memory,
agents and a terminal that this build was reconstructing by hand.

**This inference needs user confirmation.** Logged in
[[Memory/98 - Conflicts & Review Queue|98 — Conflicts & Review Queue]].

## What survived the change

The *principles* carried over intact and remain current:

- Vision is the platform; models/runtimes/agents/plugins are replaceable (ADR-001)
- Body vs engine separation (ADR-002)
- Provider/runtime abstraction; no Ollama lock-in (ADR-004, ADR-005)
- Plugins stay outside core (ADR-008)
- Obsidian is external knowledge (ADR-009)
- Hardware neutrality (ADR-010)
- Incremental development, always runnable (ADR-012)

What did **not** survive: the Electron stack, the step 1–7 roadmap, the
hand-built IPC/settings/chat layers, and the Orb as an immediate deliverable.

## Vault notes still written in this build's present tense

These describe the abandoned architecture as current and should be read as
historical: [Vision Technical Stack](Projects/Vision/Vision%20Technical%20Stack.md.md), [Vision Current Status](Projects/Vision/Vision%20Current%20Status.md.md),
[Vision Roadmap](Projects/Vision/Vision%20Roadmap.md.md), [Vision Development Timeline](Projects/Vision/Vision%20Development%20Timeline.md.md), [[Important Memories]],
[Things Vision Should Remember](Memories/Things%20Vision%20Should%20Remember.md.md) (final section).
