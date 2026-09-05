---
type: note
domain: Website Development Knowledge
section: Planning
created: 2026-09-04
---

# Website Planning and Architecture

Decide what to build and how before writing a line of markup. Most website failures
are planning failures wearing a CSS costume.

## Start from the brief, not the layout

Answer these before designing anything. If the user did not say, ask or state an
assumption explicitly:

| Question | Why it decides the build |
| --- | --- |
| **Goal** | One primary action the site must drive (buy, sign up, read, contact). Everything serves it. |
| **Audience** | Their devices, context, technical comfort — sets breakpoints, tone, performance budget. |
| **Pages / views** | The real content inventory. A "site" is a list of pages, each with a job. |
| **Information architecture** | How pages group and relate; the navigation is its visible shape. |
| **Functional requirements** | Forms, search, auth, payments, dynamic data — these decide the stack. |
| **Visual direction** | Brand, mood, references. Vague here means rework later. |
| **Constraints** | Performance, SEO, accessibility level, security, deadline, who maintains it. |
| **Acceptance criteria** | How you will *know* it is done and correct. Write them now. |

## Information architecture & navigation

- **Content inventory first**: list every page and its single purpose. Cut pages that
  have no purpose.
- **Group by the user's mental model**, not the org chart. Labels are the user's words.
- **Navigation depth ≤ 2–3 for most sites.** If you need more, the IA is wrong.
- **Every page reachable in a few clicks**; primary actions reachable from anywhere.
- **URL structure mirrors the IA** — readable, stable, lowercase, hyphenated.

## Responsive breakpoints

Design **mobile-first**. Add a breakpoint where the *content* stops looking right, not
at device names. A workable default set (min-width):

| Token | ~Width | Typical shift |
| --- | --- | --- |
| base | 0 | single column, stacked |
| `sm` | 640px | larger type, more padding |
| `md` | 768px | two columns, inline nav |
| `lg` | 1024px | full multi-column layout |
| `xl` | 1280px | max content width, generous whitespace |

Constrain line length to ~60–75 characters and cap content width (~1100–1280px) so
text stays readable on large screens.

## Choosing the implementation stack

Drive the choice from requirements, never fashion. See the table in
[[Website Development Knowledge/00 - Website Development Index|the index]] for the summary;
the reasoning:

- **Static HTML/CSS/JS** — few pages, content rarely changes, no app state. Fastest to
  load, cheapest to host, least to break. The right default for landing/portfolio/marketing.
- **React / Svelte / Vue (SPA)** — genuinely app-like interactivity, lots of client state.
  Cost: JS payload, slower first paint, SEO needs care.
- **Next.js / SvelteKit / Astro (meta-framework)** — need SEO *and* interactivity, or
  server rendering. Astro is ideal for content-heavy sites with interactive "islands".
- **Component library** (Radix, shadcn/ui, Material, etc.) — use when you need accessible,
  battle-tested primitives fast; do not hand-roll a modal or combobox.
- **Utility CSS (Tailwind)** — consistency and speed; pairs with a token layer. Plain CSS
  with custom properties is fine for small sites and avoids a build step.

## Backend, APIs, auth — flag early, defer to Coding Knowledge

Identify, do not design here:

- **Backend needed?** Only if there is data to store, logic to hide, or secrets to keep.
  A static site with a form can often use a form service or a single serverless function.
- **APIs / integrations** — list them, their auth, their rate limits, their failure modes.
- **Authentication** — if present, it dictates a server. Use a library, never hand-roll.
- **Performance & security constraints** — set the budget (Core Web Vitals) and the
  baseline (HTTPS, no secrets in the client, input validation) up front.

For all of these, defer to
[[Coding Knowledge/05 - Web & Application Engineering/00 - Web & Application Engineering|Web & Application Engineering]]
(Backend, REST, Databases, Authentication, Authorization, Web Security).

## Acceptance criteria — write them before building

A site is "done" when it: serves the goal, works on mobile and desktop, has no console
errors, passes basic accessibility (contrast, keyboard, semantics), loads fast, and every
link/form/interaction works. Turn each into a checkable item — that list *is* the test plan
([[Website Development Knowledge/06 - Testing Deployment and Vision Executors|06]]).

## Failure modes

- Designing pages before the content inventory exists.
- Choosing a framework before knowing if there is any app state.
- Fixed device-width breakpoints that break on the next device.
- No stated goal, so every section competes for attention.
- Auth/payment discovered late, forcing a stack rewrite.

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]]
- [[Coding Knowledge/05 - Web & Application Engineering/Backend Architecture|Backend Architecture]]
- [[Website Development Knowledge/02 - UI UX and Design Systems|UI/UX & Design Systems]]

## Sources

Practitioner synthesis. Rendering/stack trade-offs restated from web.dev
(<https://web.dev/>) and MDN (<https://developer.mozilla.org/>, CC BY-SA 2.5).
Full provenance in [[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
