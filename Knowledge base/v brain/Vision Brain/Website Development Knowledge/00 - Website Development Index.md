---
type: MOC
role: domain index
domain: Website Development Knowledge
created: 2026-09-04
---

# Website Development Knowledge

How Vision **designs and builds websites** — the workflow from a user's brief to a
deployed, accessible, responsive site. This domain owns the *design-and-build*
side; the *engineering internals* (auth, backend, caching, databases, security,
performance mechanics, frontend state/rendering) live in **Coding Knowledge** and
are cross-linked, never duplicated.

> Vision is the reasoning layer. Figma, AI generators and code executors are
> tools it directs — none of them is "the brain".

## Notes

| Note | Covers |
| --- | --- |
| [[Website Development Knowledge/01 - Website Planning and Architecture\|01 · Planning & Architecture]] | Goal, audience, pages, IA, requirements, and the stack decision |
| [[Website Development Knowledge/02 - UI UX and Design Systems\|02 · UI/UX & Design Systems]] | Hierarchy, type scale, spacing, colour, components, states, tokens |
| [[Website Development Knowledge/03 - Figma Workflow and Plugins\|03 · Figma Workflow & Plugins]] | Wireframe→component→Auto Layout→variants→variables→handoff; curated plugins |
| [[Website Development Knowledge/04 - Frontend Implementation\|04 · Frontend Implementation]] | Semantic HTML, modern CSS, responsive, states, forms, SEO, images |
| [[Website Development Knowledge/05 - Responsiveness Accessibility and Performance\|05 · Responsive, A11y & Performance]] | Breakpoints, WCAG 2.2 rules, Core Web Vitals |
| [[Website Development Knowledge/06 - Testing Deployment and Vision Executors\|06 · Testing, Deployment & Executors]] | Build→inspect→test→fix loop; Auto Browser / Desktop use; AI web design |
| [[Website Development Knowledge/07 - Visual Assets 3D and Motion\|07 · Visual Assets, 3D & Motion]] | SVG/raster/icons, media, animation, WebGL/Three.js, Blender→glTF |
| [[Website Development Knowledge/99 - Sources and Provenance\|99 · Sources & Provenance]] | Every external source, licence and retrieval date |

## The default workflow (a recommendation, not a ritual)

```
Brief → Requirements → Information architecture → Wireframe → Design system
→ Figma design → Prototype → Frontend implementation → Browser testing
→ Accessibility & performance review → Fixes → Final validation → Deployment
```

**Skip stages the project does not need.** A one-page landing site does not need a
formal IA document or a Figma prototype; it needs a design-system decision, a build,
and a browser test. A ten-page app with auth needs every stage. Match ceremony to risk.

## Stack decision, in one place

No framework is universally best. Choose from the requirements
([[Website Development Knowledge/01 - Website Planning and Architecture|see 01]]):

| Situation | Default choice |
| --- | --- |
| Static content, few pages, no app state, must be simple & fast | **Semantic HTML + CSS + a little vanilla JS** |
| Rich client interactivity, an app that lives in the browser | **React (or Svelte/Vue)** as an SPA — accept the JS cost |
| Content site that must be SEO-strong *and* interactive | **Next.js / SvelteKit / Astro** — server-render, hydrate selectively |
| Mostly content with islands of interactivity | **Astro** (ship HTML, hydrate only the islands) |
| Styling | **Utility CSS (Tailwind)** for speed & consistency, or plain CSS with custom properties + a token layer |

Reach for a framework when it earns its bundle. A full SPA for a brochure site is a
common, expensive mistake (per [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]]).

## Quick rules Vision should never forget

- **Semantic HTML first.** A `<button>` is a button; landmarks (`header/nav/main/footer`),
  one `<h1>`, headings in order. ARIA only where semantics fall short.
- **Design tokens before pixels.** Decide a type scale, a spacing scale (a 4/8px
  system), and a colour set *once*; reference them everywhere.
- **Mobile-first, fluid.** Design the narrow layout first; add breakpoints where the
  content breaks, not at fixed device widths.
- **Contrast ≥ 4.5:1** for body text, **≥ 3:1** for large text and UI components;
  **interactive targets ≥ 24×24 CSS px** (WCAG 2.2). Visible focus on everything.
- **Every async view has three states**: loading, empty, error — not just success.
- **Budget the bundle and the images.** AVIF/WebP, explicit width/height (no layout
  shift), lazy-load below the fold. Target LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1.
- **Build → inspect → test → fix → retest.** Open the real site in **Auto Browser**
  ([[Website Development Knowledge/06 - Testing Deployment and Vision Executors|06]]),
  read the console, check responsiveness, then correct.
- **AI generators (Figma Make, design-to-code) draft; Vision reviews and owns the
  result.** Never ship generated code unread.

## How this domain is used

Retrieved on demand when Vision is asked to design or build a website. Implementation
runs through the existing **Coding Agent → OpenCode**; validation through the
**Browser Agent → Auto Browser**. This domain adds *no* new agent and *no* new
runtime — it is knowledge only.
