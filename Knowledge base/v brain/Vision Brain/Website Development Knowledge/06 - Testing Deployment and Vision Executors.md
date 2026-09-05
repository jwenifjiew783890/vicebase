---
type: note
domain: Website Development Knowledge
section: Validation
created: 2026-09-04
---

# Testing, Deployment and Vision Executors

A website is not done when it renders once on the builder's screen. It is done when it is
verified — in a real browser, at real sizes, against the acceptance criteria.

## The loop: build → inspect → test → fix → retest

1. **Build** a coherent slice (a page or section), not the whole site blind.
2. **Inspect** — open it in a real browser, look at it, read the console.
3. **Test** against the checklist below.
4. **Fix** the real issues found (don't paper over them).
5. **Retest** — confirm the fix and that nothing else broke.

Repeat per slice. Small loops beat one big reveal.

## What to test

| Category | Checks |
| --- | --- |
| **Functional** | Every link navigates; every button does its thing; flows complete |
| **Visual** | Layout matches the design; spacing/type/colour consistent; no overflow/overlap |
| **Responsive** | Mobile, tablet, desktop; no horizontal scroll; content reflows sensibly |
| **Accessibility** | Keyboard-only pass; visible focus; contrast; semantics; alt text (see 05) |
| **Performance** | LCP/INP/CLS in range; asset sizes; no obvious jank |
| **Console / runtime** | No errors or 404s in the console/network |
| **Links & assets** | No broken links, images, or fonts |
| **Forms** | Validation, error messages, success, data preserved on error |
| **States** | Loading, empty, error render correctly — not just success |
| **Security basics** | HTTPS; no secrets in client; inputs validated; deps sane |
| **Browser compat** | Works across current evergreen browsers |

## Using Vision's executors (do not modify them)

Vision already has two production executors; the website workflow *uses* them, it does not
change them.

**Browser Agent → Auto Browser → Chrome** — for anything that needs a real browser:
- Open the running site, navigate, click links/buttons, fill forms.
- Read the page (title, headings, visible text, elements) to verify content and structure.
- Capture screenshots for visual inspection.
- Observe the console/network for errors and broken requests.
- Resize/emulate for responsive checks where supported.
*This is the primary validation tool for a website.* See
[[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]].

**Desktop Agent → Windows-MCP → desktop apps** — only when the task genuinely needs the OS:
- Handling local files outside the browser, or a desktop design/asset application.
- Opening a folder, saving/locating a file, driving a native app.
*Do not use it for anything a browser can do* — browser navigation and web testing belong to
Auto Browser. See [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]].

| Need | Executor |
| --- | --- |
| Visual / browser / responsive / console testing of the site | **Auto Browser** |
| Navigate or interact with the live web page | **Auto Browser** |
| Local file handling outside the browser; a desktop app | **Desktop Agent** |
| Implement / edit the site's code | **Coding Agent → OpenCode** |

## AI-assisted web design — assistant, not brain

Current AI web workflows (Figma Make, design-to-code, prompt-to-prototype, v0-style
generators, the Figma MCP server) can accelerate stages — but Vision stays the orchestrator
and reviewer. A sound sequence:

1. **Plan** the requirements and IA (Vision's reasoning) — never skip to generation.
2. **Design** in Figma (or generate a first draft with Figma Make), then curate it.
3. **Prototype** to check the flow.
4. **Generate code** (Figma Make / design-to-code) *or* implement via OpenCode.
5. **Test in a browser** (Auto Browser) and **visually inspect**.
6. **Correct** — Vision reviews generated code and output; never ship it unread.
7. **Deploy**.

Rules: the AI tool proposes; Vision decides. Generated code is a draft to review, not a
result to trust. Keep the design system as the constraint so generation stays coherent.

## Deployment (essentials)

- Static sites → any static host/CDN; ensure HTTPS, caching headers, and a custom 404.
- App/SSR → a platform that runs the framework; set env/secrets server-side only.
- Before go-live: run the full checklist above, check metadata/OG tags, sitemap/robots, and
  a real-device pass. Keep the source in version control.
- Depth in [[Coding Knowledge/06 - DevOps & Infrastructure/00 - DevOps & Infrastructure|DevOps & Infrastructure]]
  (if present) and [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]].

## Failure modes

- "It renders on my screen" treated as "done".
- Testing only the happy path and only on desktop.
- Ignoring console errors and broken network requests.
- Letting a generator's output ship unreviewed.
- Using the Desktop Agent for things the browser should do (or vice versa).

## See also

- [[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|Responsive, A11y & Performance]]
- [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]]
- [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]]

## Sources

Figma Make / design-to-code / MCP server (<https://www.figma.com/make/>,
<https://www.figma.com/solutions/design-to-code/>), retrieved 2026-09-04. Core Web Vitals —
web.dev (<https://web.dev/>). Practitioner synthesis for the testing loop. See
[[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
