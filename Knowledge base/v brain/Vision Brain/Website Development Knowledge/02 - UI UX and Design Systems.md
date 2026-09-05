---
type: note
domain: Website Development Knowledge
section: Design
created: 2026-09-04
---

# UI/UX and Design Systems

A design system is a small set of decisions made once — type, space, colour, components —
then reused everywhere. Consistency is not a nicety; it is what makes a site feel built
rather than assembled.

## Visual hierarchy first

The eye should land where you want it. Establish, in order: one clear focal point per view
(usually the hero headline + primary action), then supporting content, then everything else.
Achieve it with **size, weight, colour, and whitespace** — not decoration. Whitespace is the
cheapest, most effective design tool; crowded is the default failure.

## Type scale

Pick a base size (16px body is the safe default) and a modular scale, so sizes relate
instead of being arbitrary. A ~1.25 (major third) ratio is a reliable choice:

| Role | Size (px, ~1.25 scale) | Notes |
| --- | --- | --- |
| Body | 16 | never below 16 for primary text |
| Small / caption | 13–14 | metadata, labels |
| h3 | 20 | |
| h2 | 25 | |
| h1 | 31–39 | hero can go larger, fluid with `clamp()` |

Line-height ~1.5 for body, ~1.1–1.25 for headings. Line length 60–75 characters. Limit the
site to **1–2 typefaces** (e.g. one for headings, one for body) and 2–3 weights.

## Spacing system

Use a single spacing scale based on a 4px (or 8px) unit: `4, 8, 12, 16, 24, 32, 48, 64, 96`.
Every margin, padding and gap is a value from the scale. This alone removes most "slightly
off" misalignment. Space is *related* to the type scale — generous, consistent rhythm reads
as quality.

## Colour system

Define roles, not one-off hex values:

| Token | Purpose |
| --- | --- |
| `--bg`, `--surface` | page and card backgrounds |
| `--text`, `--text-muted` | primary and secondary text |
| `--primary` (+ hover/active) | brand / primary action |
| `--accent` | sparing emphasis |
| `--border` | dividers, outlines |
| `--success/--warning/--danger` | status |

Rules: keep the palette small; ensure every text/background pair meets contrast
([[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|05]]);
provide a dark-mode set by redefining tokens under `prefers-color-scheme`, not by rewriting
components. Never rely on colour alone to carry meaning.

## Components & states

Think in reusable components (button, card, input, nav, badge), each with **every state
designed**, not just the resting one:

- **Interactive**: default, hover, focus (visible ring), active, disabled.
- **Data**: loading, empty, error, success — the three non-happy states are where quality
  shows and amateurs stop.
- **Content**: short and overflowing (long names, missing images) — design both.

A button is one component with variants (primary/secondary/ghost, sizes), not five buttons.

## Design tokens

Tokens are the contract between design and code. Express them as CSS custom properties
(`--space-4`, `--text-lg`, `--color-primary`) or a Tailwind config. The same names should
appear in Figma (as variables/styles) and in code, so a change propagates once. This is what
makes a "design system" real rather than a mood board.

## Naming

Name by **role, not appearance**: `--color-primary` not `--blue`; `.card` not `.box-shadow-thing`;
a Figma component `Button/Primary` not `Rectangle 47`. Appearance-based names lie the moment
the design changes. Meaningful, consistent naming is what makes handoff and reuse work
([[Website Development Knowledge/03 - Figma Workflow and Plugins|03]]).

## Failure modes

- Arbitrary sizes and spacings ("16… 15… 18…") instead of a scale.
- A 12-colour palette nobody can keep coherent.
- Only the happy path designed; loading/empty/error improvised in code.
- Decoration standing in for hierarchy; everything shouting at once.
- Tokens in Figma and hard-coded values in CSS drifting apart.

## See also

- [[Website Development Knowledge/03 - Figma Workflow and Plugins|Figma Workflow & Plugins]]
- [[Website Development Knowledge/04 - Frontend Implementation|Frontend Implementation]]
- [[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|Responsive, A11y & Performance]]

## Sources

Practitioner synthesis; type/spacing/token practice aligned with established design-system
literature and Figma's design-systems guidance (<https://www.figma.com/>). Accessibility of
colour per WCAG 2.2 (<https://www.w3.org/TR/WCAG22/>). See
[[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
