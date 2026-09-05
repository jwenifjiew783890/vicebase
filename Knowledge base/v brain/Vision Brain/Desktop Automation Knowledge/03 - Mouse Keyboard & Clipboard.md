---
type: note
domain: Desktop Automation Knowledge
section: root
created: 2026-09-04
---

# Mouse, Keyboard & Clipboard

Choosing and issuing an input action once you have grounded on an element
([[Desktop Automation Knowledge/02 - Windows UI Automation|Windows UI Automation]]). Every action
here is followed by verification ([[Desktop Automation Knowledge/05 - Verification Recovery & Safety|note 05]]).

Part of [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]].

## Target an element, not a pixel

Every input action can take an **element handle** or a **pixel coordinate**. Default to the
element handle. Pixel coordinates are a fallback for custom-drawn surfaces and an escalation step
after a background element click is confirmed to have done nothing — never the first move.

## Mouse

Available click types: **click, double-click, right-click, middle-click**. Each accepts:

- an element handle *or* a coordinate,
- optional **modifiers** (e.g. `Ctrl`, `Shift`, `Alt` held during the click),
- an option to **recapture immediately after**, so the returned state already reflects the click.

Right-click opens context menus; the menu items are themselves elements — recapture, then invoke
the item by name. Do not right-click and then blind-click a guessed menu position.

### Drag

- **Prefer element-to-element**: drag *from* one element *to* another. This survives layout shifts.
- **Use coordinates only for continuous surfaces** — a canvas selection, a slider you cannot set
  via the RangeValue pattern, a drawing gesture.

## Keyboard

Two distinct actions:

- **Type text** — enter a string into the focused control.
- **Press keys** — named keys and shortcuts: `Return`, `Escape`, `Tab`, `Ctrl+S`, `Ctrl+T`,
  `Alt+Tab`, arrow keys, etc.

### Windows key idioms

Vision's target is Windows 11, so use Windows idioms, not macOS ones:

| Intent | Windows | (macOS, for contrast) |
| --- | --- | --- |
| Save | `Ctrl+S` | `Cmd+S` |
| Copy / paste | `Ctrl+C` / `Ctrl+V` | `Cmd+C` / `Cmd+V` |
| App switcher | `Alt+Tab` | `Cmd+Tab` |
| Close window | `Alt+F4` | `Cmd+W` |

### Hard rules for typing

- **Never type secrets** — passwords, API keys, card numbers, tokens. If a field needs one, stop
  and hand it to the user. This is a safety boundary, not a preference
  ([[Desktop Automation Knowledge/05 - Verification Recovery & Safety|note 05]]).
- **Do not type into a text editor or terminal to edit files or run commands.** Use real file
  tools (read/write/patch) and a real terminal instead. Synthetic keystrokes into these are slower,
  lossy, and — for some rich-text/Qt controls — silently dropped. Detail in
  [[Desktop Automation Knowledge/04 - Windows Apps Windows & Files|Windows Apps, Windows & Files]].
- **Some key sequences are hard-blocked** by a safe executor (log out, lock screen, and dangerous
  shell patterns inside a "type" action). If a type is refused for matching a dangerous pattern,
  that is the guard working — reconsider, do not try to slip it past.

## Scroll

Scroll by **direction** (up/down/left/right) and **amount in ticks**, optionally targeting a
specific element or coordinate. Prefer scrolling the element that actually owns the scrollbar
(found via the Scroll control pattern) over scrolling "the window" and hoping.

## Clipboard

The clipboard is a legitimate transfer channel when direct typing is unreliable or when moving a
block of text between apps: set clipboard content, focus the target, paste with `Ctrl+V`. Two
cautions:

- The clipboard is **global and user-visible** — you are overwriting whatever the user had copied.
  Restore it if that matters.
- **Never place a secret on the clipboard** for the same reason you never type one. Clipboard
  contents are readable by other apps.

## Delivery and focus

Input is delivered in the background by default. If the executor reports it cannot deliver in the
background (`background_unavailable`), that is a signal to escalate deliberately — request
foreground delivery, which may require a separate focus approval — not to hammer the same
background action. Escalation order is in
[[Desktop Automation Knowledge/05 - Verification Recovery & Safety|Verification, Recovery & Safety]].

> [!info] Provenance
> Action set, drag/scroll semantics, the no-secrets and use-file-tools rules, and the
> background/foreground delivery model are **derived from the Hermes computer-use SKILL** (MIT,
> © 2025 Nous Research), retrieved 2026-09-04. Restated, not copied. Windows key idioms are
> general platform fact. Nothing here is *Vision-verified* yet. Record:
> [[Desktop Automation Knowledge/99 - Sources & Provenance|Sources & Provenance]].
