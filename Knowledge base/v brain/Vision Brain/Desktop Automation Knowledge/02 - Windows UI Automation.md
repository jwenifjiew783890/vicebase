---
type: note
domain: Desktop Automation Knowledge
section: root
created: 2026-09-04
---

# Windows UI Automation

Reliable desktop control on Windows means grounding on the **UI Automation (UIA)** tree, not on
pixels. This note is the "how do I know what I'm clicking" note.

Part of [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]].

## What UIA is

UI Automation is Microsoft's accessibility framework — the same tree screen readers use. Every
window exposes its controls as a tree of **automation elements**, and the framework is what makes
an element *addressable by name and role* rather than by where it happens to be drawn. A
desktop-control executor reads this tree to build the element index you act on.

The accessibility model differs per OS, which is why grounding is described generically upstream:
a button is `Button` in Windows UIA, `AXButton` on macOS, and `push button` in Linux AT-SPI. On
Vision's target (Windows 11), it is UIA.

## Element identity — what to match on

Each element carries properties. In rough order of how stable they are to match on:

| Property | What it is | Stability |
| --- | --- | --- |
| **AutomationId** | A developer-assigned stable id | Most stable — when present, prefer it |
| **ControlType** | The kind of control (Button, Edit, CheckBox, MenuItem…) | Stable |
| **Name** | The visible/accessible label | Usually stable; can be localized |
| **ClassName** | The underlying window class | Implementation detail — weak |
| **BoundingRectangle** | On-screen rectangle | Changes with layout — last resort |

Match on identity (AutomationId, ControlType + Name), not on position. Position is for the pixel
fallback only.

## Control patterns — what an element can *do*

UIA exposes behaviour through **control patterns**: a control advertises the patterns it supports,
and you interact through those. This is the desktop equivalent of "find the element, then know
which verb applies." The documented patterns include:

| Pattern | Controls it fits | The action it gives you |
| --- | --- | --- |
| **Invoke** | Buttons, anything "pressable" | Trigger it |
| **Value** | Edit boxes, date pickers | Get / set a single value |
| **RangeValue** | Sliders, spinners, progress | Get / set within a min–max range |
| **Toggle** | Check boxes, checkable menu items | Cycle on/off/indeterminate |
| **ExpandCollapse** | Menus, tree items, combo boxes | Open / close |
| **Selection / SelectionItem** | List boxes, combo boxes, tabs | Read the selection / select an item |
| **Text** | Edit controls, documents | Read/inspect textual content and ranges |
| **Scroll / ScrollItem** | Anything with scrollbars | Scroll, or bring an item into view |
| **Grid / GridItem / Table / TableItem** | Data grids, Explorer views, Excel | Address cells, read headers |
| **Window** | Top-level windows, dialogs, MDI children | Window-level state (min/max/close) |
| **Transform** | Design-surface objects | Move, resize, rotate |
| **Dock / MultipleView** | Toolbars; multi-view lists | Docking; switch representation |

Patterns are **dynamic**: a multiline edit box only advertises Scroll when it actually has more
text than fits. So re-check what a control supports *now*, from a fresh capture — do not assume a
pattern is present because it was last time.

Reasoning shortcut: decide the *verb* first (press / set text / toggle / choose / scroll), then
find a control that both matches the label and supports the matching pattern. If the obvious
control does not support the pattern you need, you have the wrong element.

## Element handles go stale

Element indices/handles are valid **only until the next capture**. After anything that could
redraw the UI, recapture and re-resolve. A stale handle should surface as an explicit error rather
than silently acting on the wrong thing — treat "stale element" as *recapture*, never as *retry
harder*.

## Windows-specific gotchas

- **Session 0 vs. the interactive desktop.** A process running in Windows *Session 0* (e.g. over
  SSH, or as some services) is isolated from the interactive desktop and will see empty captures /
  "no window". Desktop automation must run in the user's interactive session. If captures come back
  empty, check which session the executor is in before debugging anything else.
- **UWP / packaged apps** are hosted by `ApplicationFrameHost.exe`, which changes how their
  elements are reached — the real controls live under the frame host, not the visible window
  process. Expect an extra layer when grounding on Store apps.
- **Idioms are Windows idioms** — `Ctrl` where macOS uses `Cmd`, `Alt+Tab` for the app switcher.
  See [[Desktop Automation Knowledge/03 - Mouse Keyboard & Clipboard|Mouse, Keyboard & Clipboard]].

> [!info] Provenance
> Control-pattern names, semantics and the providers/clients model are **documented Microsoft
> platform behaviour**, from *UI Automation Control Patterns Overview* on Microsoft Learn
> (`learn.microsoft.com/dotnet/framework/ui-automation/ui-automation-control-patterns-overview`;
> docs git commit `156931bb`), retrieved 2026-09-04. The capture/grounding method and the
> per-OS accessibility names are **derived from the Hermes computer-use SKILL** (MIT, © 2025 Nous
> Research). Restated, not copied. Verify pattern availability against the current Microsoft docs
> for your Windows build. Full record in
> [[Desktop Automation Knowledge/99 - Sources & Provenance|Sources & Provenance]].
