---
type: note
domain: Desktop Automation Knowledge
section: root
created: 2026-09-04
---

# Windows Apps, Windows & Files

Targeting the right application and window, handling file dialogs, and the special case of text
editors and Office apps. This absorbs three concerns that all reduce to "route input to the right
place, and use the right tool for text."

Part of [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]].

## Finding and targeting applications

- **List running apps** to discover what is available — the listing gives app names, process ids
  and window counts. Confirm the target is actually running before you try to act on it.
- **Focus an app to route input to it** without necessarily raising its window. Passing the app as
  the target of a capture/click/type sends the action to that app's frontmost window
  automatically.
- **Do not raise/foreground windows by default.** Input works in the background; raising a window
  disrupts the user. Raise only on explicit request or as a deliberate escalation.
- **Do not switch virtual desktops.** A background executor can drive elements on any desktop
  regardless of which one is visible; switching desktops disrupts the user for no benefit.

## Window handling

Windows expose the **Window** control pattern
([[Desktop Automation Knowledge/02 - Windows UI Automation|UIA]]) for state like minimise /
maximise / close, and dialogs are just windows. When an action spawns a new window (a dialog, a
picker, a message box), **recapture** — the new window is where the next elements live, and acting
on the old window's coordinates is a classic no-op.

## File dialogs

A file open/save dialog is a normal Windows dialog: it has an editable **File name** field (Value
pattern), a file list (often a Grid/Table), and buttons (Invoke). To drive one reliably:

1. Recapture once the dialog appears.
2. Type the **full path** into the File name field rather than clicking through the tree — it is
   faster and far less brittle than navigating folders by clicking.
3. Invoke **Open** / **Save**.

But prefer to avoid the dialog entirely when the goal is really file I/O — see below.

## Text editors, files, and the "use the right tool" rule

The single most important habit for reliability:

> **Do not synthesise keystrokes to edit files or run commands. Use file tools and a terminal.**

- To change a file's contents, use real **read / write / patch** file operations, not "type into
  the editor window". Typing is slow, races with autosave, and — critically — **some rich-text and
  Qt-based text controls silently discard synthetic keystrokes**. After one verified-lost attempt,
  stop typing and go through the filesystem, then reload the file in the app if the app must show
  it.
- To run a command, use a real **terminal/shell**, not "type into a Terminal window". A good
  executor detects terminal emulators and will route or refuse accordingly.
- `computer_use`-style desktop actions are for **desktop chrome** — menus, toolbars, dialogs,
  buttons. For *web page* content (page DOM, form fields, links) use the browser executor instead;
  desktop automation is not the tool for page content. Vision's browser executor is Auto Browser
  ([[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]]).

## WordPad and Office automation

The general pattern for a GUI word processor / Office app: the **ribbon or menu** is a tree of
Invoke/ExpandCollapse elements, the **document canvas** exposes the Text pattern, and **Save**
raises a file dialog handled as above. Ground on ribbon elements by name; do not memorise ribbon
coordinates, which move between versions and window sizes.

Two honest caveats specific to Vision's platform (Windows 11):

- **WordPad has been removed from current Windows 11** (24H2 and later; this machine is build
  26200). Treat "WordPad" as the *historical lightweight example* of rich-text automation. The
  real targets on this machine are **Notepad** (plain text) and **Microsoft Word** (if installed).
- For anything beyond trivial formatting, Word and Excel have **first-class automation surfaces**
  (COM/Office object model, Open XML for the files themselves) that are far more reliable than
  driving the GUI. Prefer the document/API route over clicking the ribbon when the outcome is a
  file, and fall back to UI automation only for things that genuinely require the live app.

> [!info] Provenance
> App/window handling, the don't-raise / don't-switch-desktop rules, the file-tools-over-typing
> rule, the rich-text/Qt keystroke-loss caveat, and the desktop-vs-browser split are **derived
> from the Hermes computer-use SKILL** (MIT, © 2025 Nous Research), retrieved 2026-09-04. Restated,
> not copied. WordPad's removal from Windows 11 and the Office automation surfaces are general
> platform fact — verify against current Microsoft docs and what is actually installed. Nothing
> here is *Vision-verified* yet. Record:
> [[Desktop Automation Knowledge/99 - Sources & Provenance|Sources & Provenance]].
