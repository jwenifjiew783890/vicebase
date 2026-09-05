---
type: note
domain: Browser Knowledge
created: 2026-09-04
---

# Observation & Element Grounding

How to read the current page and target the right element — the browser equivalent of "capture
first, ground on an element" from the desktop domain.

Part of [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]].

## Observe before you act

Never act on a page you have not just observed. Auto Browser gives several ways to look, each a
different cost/detail trade:

| Observation | Returns | Use when |
| --- | --- | --- |
| **`text` preset** | Accessibility outline + extracted text + interactables, **no screenshot** | The default for reasoning — cheap, structured, enough to choose an element |
| `browser.observe` | Combined current state | A general "what's on screen now" |
| `browser.screenshot` | A visual capture | You need pixels — verifying rendered layout, or a custom canvas |
| `browser.dom` | The DOM structure | You need the underlying document, not the rendering |
| `browser.console` / `browser.network` | Console log / network activity | Debugging why a page misbehaved |

**Prefer the accessibility outline / `text` preset over screenshots** for locating elements. It is
cheaper, more reliable, and gives you real element handles instead of pixels — the same lesson as
[[Desktop Automation Knowledge/02 - Windows UI Automation|desktop UIA grounding]]. Reach for a
screenshot to *verify appearance*, not to *find* things.

## Stable element ids — ground on the id, not the pixel

Auto Browser's controller **extracts interactables and tags them with stable element ids**. This is
the core of its perception model: the ids exist precisely so the model chooses an `element_id`
instead of guessing coordinates. Act on the id.

To get an id when the outline doesn't hand you the obvious one, use **`browser.find_elements`** with
a `query`:

- the query is **plain text or a regex**, matched **case-insensitively**,
- match on the accessible name / visible text of the control,
- if several match, disambiguate with a more specific query rather than picking blindly.

## Verify via page signals

After an action, confirm it worked from real signals rather than assuming. Auto Browser derives
action verification from **before/after page signals** — the ones worth checking:

- **URL** changed (navigation succeeded),
- **title** changed,
- **focus** moved to the expected field,
- **text / DOM** changed where you expected it to.

If none of the expected signals changed, treat the action as *not confirmed* and re-observe before
retrying — the browser analogue of the desktop `suspected_noop`
([[Desktop Automation Knowledge/05 - Verification Recovery & Safety|desktop note 05]]).

## Grounding discipline in one line

**Observe with the accessibility outline → pick or find an `element_id` → act on the id → confirm
via URL/title/focus/text/DOM.** Screenshots verify appearance; they are not how you locate things.

> [!info] Provenance
> The `text` observation preset, stable element ids, `browser.find_elements` query semantics, and
> before/after verification signals are **upstream capability** from the **Auto Browser** docs
> (README, `docs/architecture.md`, `docs/mcp-clients.md`; MIT, © LvcidPsyche; ~v1.5.0), retrieved
> 2026-09-04. The "prefer accessibility outline over screenshots" preference is also stated by the
> Browser Use reference ([[Browser Knowledge/10 - Reference Methodology/Browser Use (Reference Only)|Browser Use]]).
> **Derived, not copied.** Not yet *Vision-verified*. Record:
> [[Browser Knowledge/99 - Sources & Provenance|Sources & Provenance]].
