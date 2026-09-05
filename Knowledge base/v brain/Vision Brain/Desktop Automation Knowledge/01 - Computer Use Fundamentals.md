---
type: note
domain: Desktop Automation Knowledge
section: root
created: 2026-09-04
---

# Computer Use Fundamentals

How to reason about controlling a desktop at all. The rest of the domain is detail; this is the
loop everything hangs off.

Part of [[Desktop Automation Knowledge/00 - Desktop Automation Index|Desktop Automation Knowledge]].

## The loop: capture → act → verify

1. **Capture first.** Take a fresh observation of the target app *before* you touch it. You cannot
   reliably click what you have not just seen — window contents, dialog state and element
   positions change without notice.
2. **Act on a grounded element.** Prefer a named UI element over a raw pixel coordinate (see
   [[Desktop Automation Knowledge/02 - Windows UI Automation|Windows UI Automation]]).
3. **Verify the effect.** Read a signal that the action changed the state you expected — a new
   window, a changed value, focus moving. An action issued is not an action confirmed. Verdict
   handling lives in [[Desktop Automation Knowledge/05 - Verification Recovery & Safety|Verification, Recovery & Safety]].

The reference executor lets you fuse the last two: capture *after* an action in the same call
(an "act-and-recapture" option), so the result you read already reflects the new state. Use that
whenever the next decision depends on what the action did.

## Background operation is the point

The reference design operates the desktop **in the background**: its actions do not move the
user's real mouse cursor, do not steal keyboard focus, and do not switch virtual desktops. Any
on-screen cursor overlay is a *visual cue only* — the real OS cursor never moves. Practical
consequences:

- The user can keep working while an automation runs. Do not treat "the window isn't in front"
  as a blocker — input can be routed to an app's window without raising it.
- Do **not** raise or foreground windows for your own convenience. Only bring a window to the
  front when the user explicitly asks, or when an action genuinely cannot be delivered in the
  background (a deliberate escalation, not a default — see note 05).

## Capture modes

There is more than one way to observe, and the right one depends on what you need to decide.

| Mode | Returns | Use when |
| --- | --- | --- |
| **SOM** (set-of-marks, default) | Screenshot **+ numbered element overlays + an accessibility index** | The normal case. You get pixels *and* stable element handles to act on. |
| **Vision** | Plain screenshot, no overlays | The overlays would obscure exactly the thing you need to read (e.g. verifying rendered text under a mark). |
| **AX** | Accessibility tree only, no image | You only need structure and labels, not pixels — cheaper, and works for text-only reasoning. |

Default to SOM. Drop to Vision only to *verify* something the marks cover up. Use AX when a
screenshot would add nothing.

## Visual grounding vs. structural grounding

Two ways to know *where* something is:

- **Structural** — the element comes from the accessibility tree, with a real name and role. This
  is the reliable path. Act by element index/handle, not by pixel.
- **Visual** — you locate something by how it looks in the screenshot. This is a fallback, used
  only when the element is not exposed structurally (custom-drawn canvases, some game or media
  UIs). Pixel coordinates are an *escalation step*, never the first choice.

Why this matters: element handles survive minor layout shifts and read back reliably across
different models; pixel coordinates are brittle and model-dependent. Grounding is covered in full
in [[Desktop Automation Knowledge/02 - Windows UI Automation|Windows UI Automation]].

## How to reason about a new desktop task

1. Which app owns the target? Confirm it is running and reachable
   ([[Desktop Automation Knowledge/04 - Windows Apps Windows & Files|Windows Apps, Windows & Files]]).
2. Capture it in SOM. Read the tree, find the element by name/role.
3. Is the action sensitive (password, payment, 2FA, anything the user did not ask for)? If so,
   **stop and ask** ([[Desktop Automation Knowledge/05 - Verification Recovery & Safety|note 05]]).
4. Act on the element; recapture; verify the effect.
5. If unverifiable or a suspected no-op, do not blindly repeat — follow the escalation ladder.

> [!info] Provenance
> Method summarised from the **Hermes computer-use SKILL** (`computer-use`, v2.0.0), MIT-licensed,
> © 2025 Nous Research. Retrieved 2026-09-04. **Derived and restated, not copied.** Vision has not
> yet run any of this against a real executor, so nothing here is *Vision-verified*. Full source
> record in [[Desktop Automation Knowledge/99 - Sources & Provenance|Sources & Provenance]].
