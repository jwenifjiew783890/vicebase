---
type: note
domain: Browser Knowledge
section: Reference Methodology
created: 2026-09-04
status: reference-only
---

# Browser Use (Reference Only)

> [!warning] Supplemental browser-automation methodology — reference only
> **Vision uses [Auto Browser](https://github.com/LvcidPsyche/auto-browser) as the production
> browser executor.** Browser Use is captured here only for its general methodology. Vision does
> **not** run Browser Use, and none of its setup/runtime instructions are Vision's production
> setup. Where its ideas are useful, they are already folded into
> [[Browser Knowledge/10 - Reference Methodology/00 - Reference Methodology|Reference Methodology]]
> and the always-on Browser notes.

Part of [[Browser Knowledge/10 - Reference Methodology/00 - Reference Methodology|Reference Methodology]].

## What it is

Browser Use is a direct browser-control tool that drives Chrome over the **Chrome DevTools Protocol
(CDP)** for automation, scraping, testing, screenshots and general site/app work. Homepage
<https://browser-use.com>. It is a *different architecture* from Auto Browser (which uses Playwright
`launchServer`/`connect`, not a raw CDP attach) — noted only so the two are not confused.

## The general concepts worth keeping

These are the transferable ideas; they match how Vision should reason about *any* browser control:

- **When to use a browser** — tasks needing interaction (clicking, typing), a logged-in session,
  JavaScript rendering, or a bot-protected page.
- **When *not* to use one** — "a basic fetch of public information needs no browser. If a plain HTTP
  request can read it — a public page, an API, docs — use `curl` or your fetch tool." This is the
  single most useful discipline: don't pay for a browser you don't need.
- **Capture/observe before acting**, and **prefer accessibility trees over screenshots** for
  locating elements.
- **First-navigation discipline** — the first navigation for a task opens *a new tab* rather than
  reusing an unknown one, so tab state is preserved across steps/invocations.
- **Remote/cloud browsers** for concurrency, captchas, or rate-limiting — a scaling trade-off, not a
  correctness requirement.

## What was deliberately *not* imported

- **Installation and runtime setup** (CLI install, `mac-approve` and similar platform gotchas) —
  those are Browser Use's operational details, not Vision's. Vision's browser runtime is Auto
  Browser.
- **Its CDP-specific mechanics** as if they were Vision's interface.
- **Any framing of Browser Use as an executor for Vision.** It is not.

## If you're deciding what to actually run

Use **Auto Browser** ([[Browser Knowledge/01 - Auto Browser Architecture|Architecture]]). This note
exists so the *methodology* is on record, not to offer a second executor. Do not propose replacing
Auto Browser with Browser Use.

> [!info] Provenance
> Summarised from the **Browser Use SKILL** (`browser-use`), file
> <https://github.com/browser-use/browser-use/blob/main/skills/browser-use/SKILL.md>, MIT-licensed,
> © 2024 Gregor Zunic, retrieved **2026-09-04**. **Derived and restated, not copied**; no install
> instructions imported. Reference only. Full record:
> [[Browser Knowledge/99 - Sources & Provenance|Sources & Provenance]].
