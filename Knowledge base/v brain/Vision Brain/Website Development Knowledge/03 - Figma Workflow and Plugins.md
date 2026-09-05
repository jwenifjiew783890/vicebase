---
type: note
domain: Website Development Knowledge
section: Figma
created: 2026-09-04
---

# Figma Workflow and Plugins

Figma is the primary design surface in this workflow. Used well it produces a design that a
developer (or Vision's coding executor) can implement without guessing. Figma's own
documentation is the primary source for Figma-specific practice (help.figma.com).

## The Figma build order

1. **Wireframe / low-fidelity** — structure and hierarchy in grey boxes before any colour.
   Settle the layout and content order first.
2. **Page & layer hierarchy** — organise frames per page/breakpoint; name layers by role
   (see naming, below). A tidy layer tree is the difference between a usable file and a mess.
3. **Components** — turn every repeated element (button, card, input, nav) into a **component**.
   Design once, instance everywhere; edit the main component to change all instances.
4. **Auto Layout** — Figma's flexbox-like system. Use it on everything: it makes components
   resize, reflow and respond like real CSS, and it is the single biggest lever for designs
   that translate cleanly to code. Set padding, gap, and resizing (hug/fill/fixed) deliberately.
5. **Variants** — collect a component's states/sizes (Primary/Secondary, hover/disabled,
   sm/md/lg) into one component set with properties, mirroring code props.
6. **Variables** — hold design tokens (colour, spacing, radius, type) as **variables**, and
   support modes (light/dark, breakpoints). This is how the Figma file and the code share one
   source of truth. Prefer variables over one-off styles for anything reused.
7. **Prototyping** — wire flows and interactions to test behaviour and hand reviewers something
   clickable. Keep it as complex as the decision needs, no more.
8. **Dev Mode / handoff** — developers inspect specs, tokens, and measurements in Dev Mode;
   **Code Connect** maps Figma components to real code components so the handoff shows *your*
   code, not generic CSS.

## Accessibility inside Figma

Design accessibly, do not bolt it on: check text/background **contrast** against WCAG AA/AAA,
set a sensible **reading/focus order**, annotate **alt text** intent, and size **touch targets**
(≥ 24×24, ideally ≥ 44px) — the Stark plugin does all of this on-canvas. Figma's accessibility
guidance and community accessibility plugins are the reference.

## Config 2026 — current capabilities to know

Verified from Figma's Config 2026 announcement (help.figma.com, retrieved 2026-09-04):

- **Figma Motion** — production-ready animation in the design file (keyframes, easing, spring).
- **Custom Shader Effects & Fills** — WebGPU-based visual effects, promptable.
- **Generative Plugins** — prompt the Figma agent to build small reusable plugins in-file.
- **Weave tools** — AI image workflows (background replace, aspect changes) on the canvas.
- **Enhanced Figma Agent** — custom skills, web search, **MCP connectors**, file attachments.
- **Code Layers** (early access) — bring working code into the canvas as a layer, with GitHub
  integration.
- **Figma Make** and **design-to-code** — generate HTML/CSS/JS from a design/prompt, with a
  **Figma MCP server** to build designs into production. See
  [[Website Development Knowledge/06 - Testing Deployment and Vision Executors|06 · AI web design]].

## Curated plugins — categories, not a pile

Install the fewest plugins that earn their place. Recommendations verified 2026-09-04; confirm
licence in-Community before relying on paid tiers.

| Plugin / category | What it does | Use when | Avoid when | Status | Source |
| --- | --- | --- | --- | --- | --- |
| **Stark** (accessibility) | Contrast (WCAG AA/AAA), vision simulation, focus order, alt-text annotation, touch-target checks | Any real site — accessibility from day one | You only need a one-off contrast check | Freemium (free core; paid advanced) | figma.com/community |
| **A11y – Color Contrast Checker** | Fast per-layer contrast ratio vs WCAG | Quick contrast spot-checks | You need a full audit → use Stark | Free | figma.com/community |
| **Iconify** (icons) | Insert from 200k+ open-source icons (many icon sets) | Consistent icon set without hunting SVGs | Brand needs bespoke icons | Free | figma.com/community |
| Design-system utilities (e.g. **Design Lint**, token/style tools) | Find inconsistent styles, detached values, missing tokens | Keeping a system coherent as it grows | Tiny one-off file | Free/freemium | figma.com/community |
| Wireframing kits | Grey-box UI kits for fast low-fi | Early structure exploration | You already have a component library | Free/freemium | figma.com/community |
| Responsive/layout helpers | Frame/breakpoint and layout-grid helpers | Setting up multi-breakpoint frames | Auto Layout already covers it | Free/freemium | figma.com/community |
| Developer handoff (**Zeplin**, Dev Mode-native) | Specs, tokens, assets for developers | Design→dev handoff at scale | Dev Mode + Code Connect already suffice | Freemium | figma.com/community |
| Animation/prototyping (e.g. **ProtoPie** bridge, Figma Motion) | Higher-fidelity interaction/motion | Motion is core to the product | A static brochure site | Varies | figma.com/community |
| Content/image generation (Weave, image plugins) | Placeholder or generated imagery | Filling comps, exploring visuals | Final production assets (verify rights) | Varies | figma.com/community |
| Maps / data-viz | Embed maps or charts as design content | Data-heavy pages | Decorative use | Varies | figma.com/community |
| Typography/font tools | Type scale, font pairing, specimen | Establishing a type system | Scale already decided | Free/freemium | figma.com/community |

**Rule:** a plugin is worth installing only if it removes real, repeated manual work. Prefer
native Figma features (Auto Layout, variables, Dev Mode) over a plugin that duplicates them.

## Failure modes

- Designing in absolute pixels with no components — nothing reusable, nothing translatable.
- Skipping Auto Layout, then handing developers a design that cannot reflow.
- Tokens as one-off styles, so light/dark and code drift apart.
- A dozen plugins installed "just in case", slowing the file and confusing handoff.
- Accessibility checked at the end (or never) instead of on the canvas.

## See also

- [[Website Development Knowledge/02 - UI UX and Design Systems|UI/UX & Design Systems]]
- [[Website Development Knowledge/06 - Testing Deployment and Vision Executors|Testing, Deployment & Executors]]
- [[Image Knowledge/00 - Image Knowledge|Image Knowledge]] (generated imagery)

## Sources

Figma Help Center & Config 2026 (<https://help.figma.com/>, <https://www.figma.com/blog/config-2026-recap/>),
Figma Make / design-to-code (<https://www.figma.com/make/>, <https://www.figma.com/solutions/design-to-code/>),
Figma Community plugins (<https://www.figma.com/community>). Plugin facts as verified 2026-09-04.
Accessibility per WCAG 2.2 (<https://www.w3.org/TR/WCAG22/>). Full provenance in
[[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
