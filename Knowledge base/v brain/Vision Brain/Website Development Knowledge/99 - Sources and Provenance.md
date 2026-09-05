---
type: note
domain: Website Development Knowledge
section: Provenance
created: 2026-09-04
---

# Sources and Provenance

Every external source behind this domain, with licence, retrieval date, and what it is used
for. Nothing here reproduces copyrighted material beyond fair, attributed restatement of
facts; opinions and structure are practitioner synthesis.

**Retrieval date for all web sources: 2026-09-04** (unless noted).

## Standards & specifications (primary)

| Source | URL | Licence | Used for | Derived? |
| --- | --- | --- | --- | --- |
| WCAG 2.2 (W3C Recommendation) | <https://www.w3.org/TR/WCAG22/> | W3C Document Licence | Accessibility rules (contrast, keyboard, focus, semantics) | Facts restated |
| WCAG 2.2 — What's New | <https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/> | W3C Document Licence | New 2.2 criteria (2.4.11, 2.4.13, 2.5.8, 3.3.7…) | Facts restated |
| SC 2.5.8 Target Size (Minimum) | <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html> | W3C Document Licence | 24×24 CSS px target size + exceptions | Facts restated |
| glTF (Khronos) | <https://www.khronos.org/gltf/> | Khronos | Web 3D format guidance | Facts restated |

## Official documentation (primary)

| Source | URL | Licence | Used for | Derived? |
| --- | --- | --- | --- | --- |
| MDN Web Docs | <https://developer.mozilla.org/> | CC BY-SA 2.5 | HTML/CSS/forms/images/media facts | Facts restated |
| web.dev (Google) | <https://web.dev/> | CC BY 4.0 (site content) | Core Web Vitals, performance, responsive | Facts restated |
| web.dev — Web Vitals / INP | <https://web.dev/articles/vitals>, <https://web.dev/articles/inp> | CC BY 4.0 | LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 (75th pct) | Facts restated |
| Figma Help Center | <https://help.figma.com/> | © Figma (facts restated only) | Auto Layout, variables, variants, Dev Mode, accessibility | Facts restated |
| Figma Config 2026 recap | <https://www.figma.com/blog/config-2026-recap/> ; <https://help.figma.com/hc/en-us/articles/39582753756695> | © Figma | Current features: Motion, shaders, generative plugins, Code Layers, MCP connectors | Facts restated |
| Figma Make / Design-to-Code | <https://www.figma.com/make/> ; <https://www.figma.com/solutions/design-to-code/> ; <https://www.figma.com/ai/> | © Figma | AI web design, code generation, Figma MCP server | Facts restated |
| Figma Community (plugins) | <https://www.figma.com/community> ; <https://www.figma.com/community/accessibility> | © respective authors | Curated plugin table | Names/roles listed |
| model-viewer | <https://modelviewer.dev/> | Apache-2.0 (project) | Dropping glTF/GLB on a page | Facts restated |

## Community & secondary (used with care)

Plugin landscape cross-checked against multiple current listings (e.g. builder.io, protopie.io,
line25, browserstack accessibility guide, 2026 round-ups). These are **recommendations**, not
verified facts; the plugin *facts* (what a plugin does, its licence tier) should be confirmed on
each plugin's Figma Community page before relying on a paid tier. Specific plugins named:
**Stark**, **A11y – Color Contrast Checker**, **Iconify**, **Design Lint**, **Zeplin**,
**ProtoPie** — each on figma.com/community.

## Vault cross-references (internal, not external sources)

This domain deliberately reuses, rather than duplicates:

- [[Coding Knowledge/05 - Web & Application Engineering/00 - Web & Application Engineering|Web & Application Engineering]]
  — backend, REST, databases, auth, caching, web security, web performance internals, frontend
  state/rendering architecture.
- [[Coding Knowledge/02 - Programming & Languages/JavaScript|JavaScript]] — language depth.
- [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] — creating and
  optimising 3D assets (this domain covers only putting them on the web).
- [[Image Knowledge/00 - Image Knowledge|Image Knowledge]] — image generation.
- [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]] and
  [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]] —
  the executors used for validation.

## Provenance rules honoured

- Priority order followed: official standards → official docs → mature references → curated
  community.
- Facts restated and attributed; no verbatim copying of substantial copyrighted text.
- Recommendations distinguished from verified facts (plugins, tool choices).
- Where a fact could change (Figma features, plugin tiers, framework advice), the retrieval date
  is recorded and re-verification is expected before high-stakes use.
