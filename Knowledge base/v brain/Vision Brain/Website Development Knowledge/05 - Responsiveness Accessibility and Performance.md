---
type: note
domain: Website Development Knowledge
section: Quality
created: 2026-09-04
---

# Responsiveness, Accessibility and Performance

The three qualities users feel immediately and that separate a professional site from a
draft. Treat them as build requirements, not a final polish.

## Responsiveness

- **Mobile-first**: build the narrow layout, then add space/columns at `min-width` breakpoints
  ([[Website Development Knowledge/01 - Website Planning and Architecture|breakpoint table in 01]]).
- Break where **content** breaks, not at device names. Use fluid units (`%`, `fr`, `clamp()`,
  `min()/max()`) so layouts flex between breakpoints.
- Tap targets comfortable on touch; no horizontal scroll; test at 320px up to wide desktop.
- Cap content width and line length for readability on large screens.

## Accessibility — WCAG 2.2, the practical subset

Aim for **Level AA**. The rules that catch almost everything:

| Rule | Requirement | WCAG |
| --- | --- | --- |
| **Contrast — text** | ≥ 4.5:1 normal, ≥ 3:1 large (≥24px, or ≥18.66px bold) | 1.4.3 (AA) |
| **Contrast — non-text** | ≥ 3:1 for UI components, focus indicators, meaningful graphics | 1.4.11 (AA) |
| **Target size** | Interactive targets ≥ **24×24 CSS px** (exceptions: spacing, inline, equivalent, UA, essential) | 2.5.8 (AA) |
| **Keyboard** | Everything operable by keyboard; logical tab order; no keyboard trap | 2.1.1 (A) |
| **Focus visible** | A clear, visible focus indicator — never `outline:none` without a replacement | 2.4.7 (AA) |
| **Focus not obscured** | The focused element is not entirely hidden by sticky headers/overlays | 2.4.11 (AA) |
| **Semantics / name-role-value** | Real elements or correct ARIA; every control has an accessible name | 4.1.2 (A) |
| **Labels & instructions** | Visible label per input; errors identified in text | 3.3.1–3.3.2 (A) |
| **Redundant entry** | Don't force re-entering info already given in the same process | 3.3.7 (A, new in 2.2) |
| **Alt text** | Meaningful images described; decorative images `alt=""` | 1.1.1 (A) |
| **Reduced motion** | Honour `prefers-reduced-motion`; no motion that can't be disabled | 2.3.3 / 2.2.2 |
| **Reflow / zoom** | Usable at 200% zoom and 320px without loss of content | 1.4.10 (AA) |

Colour must never be the *only* signal (add an icon, text, or pattern). Test with keyboard
only, with a screen reader where possible, and with a contrast checker
([[Website Development Knowledge/03 - Figma Workflow and Plugins|Stark, in Figma]]).

## Performance — Core Web Vitals

The field targets (Google/web.dev, at the 75th percentile of loads):

| Metric | Good | Measures |
| --- | --- | --- |
| **LCP** (Largest Contentful Paint) | ≤ **2.5 s** | when the main content is visible |
| **INP** (Interaction to Next Paint) | ≤ **200 ms** | responsiveness to input (replaced FID, 2024) |
| **CLS** (Cumulative Layout Shift) | ≤ **0.1** | visual stability (no jumping) |

How to actually hit them:

- **LCP**: optimise the hero image (AVIF/WebP, right size, `fetchpriority="high"`, preload),
  server-render or inline critical CSS, cut render-blocking JS/CSS, use a CDN.
- **INP**: keep the main thread free — small JS, break up long tasks, avoid heavy work on
  input, debounce; prefer CSS for animation over JS.
- **CLS**: set `width`/`height` or `aspect-ratio` on media, reserve space for embeds/ads,
  don't inject content above existing content, preload fonts (`font-display: swap`).
- General: compress and cache assets, lazy-load below the fold, code-split by route, minify.
  Deep mechanics in
  [[Coding Knowledge/05 - Web & Application Engineering/Web Performance|Web Performance]] and
  [[Coding Knowledge/05 - Web & Application Engineering/Caching|Caching]].

## The overlap is the point

These three reinforce each other: semantic HTML aids accessibility *and* SEO; smaller assets
help performance *and* mobile; stable layout helps CLS *and* usability. Build them together,
not in three separate passes.

## Failure modes

- `outline: none` with no replacement — keyboard users lost.
- Contrast that looks fine to the designer but fails 4.5:1.
- Tap targets under 24px crammed together on mobile.
- A giant unoptimised hero image tanking LCP.
- Layout shift from images and web fonts loading without reserved space.
- Motion with no `prefers-reduced-motion` escape.

## See also

- [[Website Development Knowledge/04 - Frontend Implementation|Frontend Implementation]]
- [[Website Development Knowledge/06 - Testing Deployment and Vision Executors|Testing & Validation]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Performance|Web Performance]]

## Sources

WCAG 2.2 — W3C (<https://www.w3.org/TR/WCAG22/>, <https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/>);
Target Size 24px per SC 2.5.8 (<https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>).
Core Web Vitals — web.dev (<https://web.dev/articles/vitals>, <https://web.dev/articles/inp>), retrieved
2026-09-04. MDN (<https://developer.mozilla.org/>, CC BY-SA 2.5) for CSS. See
[[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
