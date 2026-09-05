---
type: note
domain: Website Development Knowledge
section: Frontend
created: 2026-09-04
---

# Frontend Implementation

The web-specific craft of turning a design into markup, styles and behaviour. State,
rendering strategy and component architecture live in
[[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]];
this note is the build-facing web layer.

## Semantic HTML

The document outline is the accessibility and SEO foundation — get it right and most of
both come free:

- One `<h1>` per page; headings in order (`h1→h2→h3`), never skipped for size.
- Landmarks: `<header> <nav> <main> <section>/<article> <aside> <footer>`. One `<main>`.
- Real elements for real things: `<button>` for actions, `<a href>` for navigation,
  `<ul>/<ol>` for lists, `<label>` bound to every input, `<table>` only for tabular data.
- `alt` on every meaningful image; empty `alt=""` on decorative ones.
- Avoid `<div onclick>` — it is invisible to keyboard and screen readers.

## Modern CSS

- **Layout with Flexbox and Grid.** Flexbox for one-dimensional rows/columns; Grid for
  two-dimensional page and card layouts. Floats and absolute positioning are last resorts.
- **Custom properties** (`--space-4`, `--color-primary`) carry the design tokens
  ([[Website Development Knowledge/02 - UI UX and Design Systems|02]]); theming = redefining them.
- **Fluid sizing**: `clamp()` for type and spacing that scales between breakpoints without a
  media query for every step.
- **Container queries** to make a component respond to *its container*, not just the viewport —
  the right tool for reusable cards/sidebars.
- **Logical properties** (`margin-inline`, `padding-block`) for direction-independent layout.
- Keep specificity flat; a utility-CSS approach (Tailwind) or a small token-driven stylesheet
  both avoid specificity wars. Avoid deep descendant selectors and `!important`.

## Responsive layout

Mobile-first: base styles are the narrow layout; `min-width` media/container queries add
complexity as space allows. Fluid grids and `max-width` on content. Test the real breakpoints
([[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|05]]).

## The three non-happy states

Every view that fetches or submits must handle **loading, empty, and error** — not only success.
A spinner that never resolves, a blank list with no "nothing here yet", or a silent failed
request all read as "broken". Design and build these explicitly.

## Forms

- `<label>` for every field; group with `<fieldset>/<legend>`; correct `type`/`inputmode`/
  `autocomplete` so mobile keyboards and password managers work.
- Validate on submit *and* on blur; show errors **next to the field**, tied with
  `aria-describedby`; never rely on colour alone.
- Disable-and-spinner the submit during the request; make it idempotent.
- Preserve entered data on error (WCAG 2.2 Redundant Entry). See
  [[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|05]].

## Routing, SEO & metadata

- Clean, stable, human-readable URLs mirroring the IA.
- Per-page `<title>` and `<meta name="description">`; **Open Graph**/Twitter tags for shareable
  cards; one canonical URL; `robots`/`sitemap.xml` as needed.
- Semantic HTML + server rendering is most of technical SEO. A content site that must rank
  should server-render (see the stack table in
  [[Website Development Knowledge/01 - Website Planning and Architecture|01]]).
- Structured data (schema.org JSON-LD) where rich results matter.

## Images & assets

- Formats: **AVIF → WebP → JPEG/PNG** fallback; SVG for icons/logos.
- Always set `width`/`height` (or `aspect-ratio`) to prevent layout shift (CLS).
- `srcset`/`sizes` for responsive images; `loading="lazy"` below the fold; `fetchpriority="high"`
  on the LCP image. More in
  [[Website Development Knowledge/07 - Visual Assets 3D and Motion|07]].

## Interaction & JS

- Progressive enhancement: the core content and links work without JS where feasible.
- Keep JS lean and code-split by route; defer non-critical scripts.
- Respect `prefers-reduced-motion` for any animation.
- For app-like state, follow
  [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]]
  (server state in a data layer, URL state in the URL, not everything in a global store).

## Browser compatibility & testing

Target current evergreen browsers; check any risky feature on caniuse; provide graceful
fallbacks. Verify in a real browser via
[[Website Development Knowledge/06 - Testing Deployment and Vision Executors|Auto Browser]].

## Failure modes

- `<div>` soup with `onclick` — inaccessible and unmaintainable.
- Desktop-first CSS retrofitted to mobile with overrides.
- No loading/empty/error states.
- Images with no dimensions (layout shift) and no modern format (bloat).
- Global CSS with runaway specificity and `!important`.

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Performance|Web Performance]]
- [[Coding Knowledge/02 - Programming & Languages/JavaScript|JavaScript]]

## Sources

MDN Web Docs (<https://developer.mozilla.org/>, CC BY-SA 2.5; facts restated) and web.dev
(<https://web.dev/>) for HTML/CSS/forms/images; WCAG 2.2 (<https://www.w3.org/TR/WCAG22/>) for
forms/semantics. Practitioner synthesis otherwise. See
[[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
