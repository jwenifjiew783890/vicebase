---
type: MOC
role: vault root
created: 2026-09-03
---

# Vision Brain

> The global entry point for Vision's persistent knowledge. Every domain below is reachable
> from here, and every knowledge note is reachable from its domain.

Navigation is **hierarchical on purpose**: root → domain → subdomain → note. Notes are *not*
linked directly to this root; that would flatten the graph into a meaningless star.

---

## Knowledge domains

| Domain | Holds |
| --- | --- |
| [[Islamic Knowledge/00 - Index\|Islamic Knowledge]] | Qur'an, hadith, scholars, topics — source-traceable religious corpus |
| [[Knowledge/00 - Knowledge\|Knowledge]] | General technical and domain knowledge |
| [[Coding Knowledge/00 - Coding Knowledge\|Coding & Engineering Knowledge]] | **Populated.** Software engineering, languages, AI and agent engineering, web, DevOps, debugging, review, practices, practitioner experience, and this stack specifically — retrieved on demand by Vision and OpenCode |
| [[3D & Blender Knowledge/00 - 3D & Blender Knowledge\|3D & Blender Knowledge]] | **Populated.** 3D fundamentals, Blender behaviour, modelling, hard surface, sculpting, geometry nodes, materials, lighting, cameras, rendering, animation, simulation, environments, architectural visualisation, optimisation, pipelines, Python automation, debugging and production practice - retrieved on demand |
| [[Browser Knowledge/00 - Browser Knowledge\|Browser Knowledge]] | **Populated.** Browser automation and web-interaction — Auto Browser (Vision's production browser executor), its tools, sessions, observation, navigation, security, and general reference methodology. |
| [[Desktop Automation Knowledge/00 - Desktop Automation Index\|Desktop Automation Knowledge]] | **Populated (reference).** How to reason about controlling native Windows apps — computer-use fundamentals, Windows UI Automation, input, apps/windows/files, verification and safety. No desktop executor installed yet. |
| [[Website Development Knowledge/00 - Website Development Index\|Website Development Knowledge]] | **Populated.** How Vision designs and builds websites — planning & IA, UI/UX & design systems, Figma workflow & plugins, frontend implementation, responsive/accessibility (WCAG 2.2)/performance, testing with Auto Browser, visual/3D/motion assets. Cross-links Coding, 3D & Blender, Browser and Desktop knowledge; adds no agent or runtime. |
| [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|Intent & Task Understanding Knowledge]] | **Populated.** How Vision reads a rough, informal, incomplete request and turns it into an executable, safety-checked plan for the right agents — intent extraction, prompt enhancement, requirements/constraints/assumptions, task decomposition & agent selection, clarification vs safe defaults. Methodology for the planning layer; adds no agent or runtime. |
| [[Business Knowledge/00 - Business Knowledge\|Business Knowledge]] | Business, commercial and operational knowledge. |
| [[Image Knowledge/00 - Image Knowledge\|Image Knowledge]] | Image generation and visual-asset knowledge. |
| [[Research Knowledge/00 - Research Knowledge\|Research Knowledge]] | Research method and information-gathering knowledge. |

## The user model

| Domain | Holds |
| --- | --- |
| [[Memory/00 - Memory Index\|Memory]] | Current, structured user model — with temporal decay |
| [[Memories/00 - Memories\|Memories]] | Earlier free-form memory notes (historical) |
| [[Identity/00 - Identity\|Identity]] | How the user thinks, works and communicates |
| [[Preferences/00 - Preferences\|Preferences]] | Stated product, engineering and AI preferences |

## Work

| Domain | Holds |
| --- | --- |
| [[Projects/00 - Projects\|Projects]] | Vision and prior projects |
| [[Decisions/00 - Decisions\|Decisions]] | Architecture decisions and change log |
| [[Agents/00 - Agents\|Agents]] | Agent strategy |
| [[Integrations/00 - Integrations\|Integrations]] | External systems Vision connects to |

---

## Architecture rule

This vault is **external to Vision Core**. Vision reaches it through a controlled integration
(Obsidian MCP). Obsidian must remain optional — removing the integration must not break Vision.

## Domain separation

Two separations are deliberate and must not be collapsed:

- **`Memory/` vs `Islamic Knowledge/`** — personal memory is not religious evidence, and a user
  preference never becomes proof of a ruling. See
  [[Islamic Knowledge/99 - Source & Authenticity Rules|Source & Authenticity Rules §20]].
- **`Memory/` vs `Memories/`** — `Memory/` is the current structured model; `Memories/` holds
  the earlier free-form notes, kept as history.

---

## Intentionally not linked

Obsidian's **daily-notes** core plugin auto-creates a dated note (e.g. `2026-09-03.md`) when
the app opens. These are empty until you write in them, and they are **not** part of the
knowledge hierarchy — so they are deliberately left unlinked rather than given an artificial
parent. They will appear as isolated dots in Graph View; that is expected.

If you start using daily notes for real, give them a `Journal/` folder with its own MOC and
link it from this root.
