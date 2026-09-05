---
type: note
domain: WhatsApp Communication Knowledge
section: Calling
created: 2026-09-04
---

# WhatsApp Calling

**The honest reality (2026-09-04): messaging works; programmatic WhatsApp *calls* do
not, with any free local automation.** This note says exactly what is and isn't
possible so no one builds on a false assumption.

## What changed in 2026

WhatsApp **did** roll out end-to-end-encrypted **audio/video calls on WhatsApp Web**
(rolled out ~July 28 2026). So a **human** can now place and receive WhatsApp calls
in the browser UI. The existence of that button is **not** the same as being able to
drive a call programmatically.

## What the free stacks can and cannot do (revised 2026-09-04)

Split into **call control** (signalling) and **call audio** (media) — they are different
problems, and WA-JS 4.6 changed the control side.

| Capability | Control — WA-JS 4.6 (our stack) | Audio (media) |
| --- | --- | --- |
| Send/receive messages, media | ✅ | — |
| **Detect** an incoming call (`incoming_call`) | ✅ (events; caveat: wa-js #3372, not always firing) | — |
| **Reject** / **End** a call | ✅ (`call.reject` / `call.end`, fixed v4.5.1, 2026-08) | — |
| **Accept** an incoming call | ✅ (`call.accept`, fixed v4.5.1) | audio still needs a path ↓ |
| **Place** (offer) a call | ✅ (`call.offer`) | audio still needs a path ↓ |
| **Inject** OmniVoice into the call | ❌ via the encrypted stream | **maybe** via Windows **device routing** (VB-CABLE as mic) — Approach 2, [[WhatsApp Communication Knowledge/08 - Voice Pipeline Integration\|08]]; **UNPROVEN** |
| **Capture** the caller's audio | ❌ via the encrypted stream | **maybe** via **WASAPI loopback** on the render device — Approach 2, [[WhatsApp Communication Knowledge/08 - Voice Pipeline Integration\|08]]; **UNPROVEN** |

**Correction to the earlier note:** call **control** (accept/offer/end/reject) is **now
possible** with WA-JS 4.6 — the old "answer ❌" was outdated. What remains unsolved for
free is the **audio**, and even there a **device-routing path exists that does not need
the encrypted stream** — investigated but **not yet proven** (see below and
[[WhatsApp Communication Knowledge/08 - Voice Pipeline Integration\|08]]).

## Why call audio is blocked

WhatsApp calls are **WebRTC** with **E2E encryption** (ICE + DTLS + **SRTP**, OPUS
codec). The media stream is negotiated and encrypted end-to-end inside the WhatsApp
client. The automation libraries operate on the **messaging** layer (Baileys speaks
the message protocol; WPPConnect/whatsapp-web.js drive the WhatsApp-Web message
store/DOM). **Neither exposes the encrypted call media stream**, and the browser's
WebRTC sandbox does not hand raw SRTP to page automation. So there is **no
programmatic hook** to push synthesized audio into a call or to pull the remote
audio out for STT.

## Two paths to call audio: paid (proven) vs device-routing (free, unproven)

- **Paid, proven:** Meta's **WhatsApp Business Calling API** (WebRTC to Meta's servers).
  Excluded by the zero-cost rule; noted for completeness only.
- **Free, unproven:** the **Windows audio-device-routing** approach — take the audio
  *after* the browser decrypts it (WASAPI loopback) and inject *before* it re-encrypts
  (a virtual-cable "mic"), so **no access to the encrypted stream is needed**. WA-JS 4.6
  supplies the call control. This is now the **candidate to test**, not a dismissed
  workaround — see [[WhatsApp Communication Knowledge/08 - Voice Pipeline Integration\|08]].

## The real remaining blockers (revised — not "raw stream access")

The old blocker ("get the encrypted stream") is **sidestepped** by device routing. What
actually stands in the way of a proven live call, honestly:

> 1. **A virtual audio cable must be installed** (e.g. VB-CABLE) — an **elevated driver
>    install + reboot**; not installed here and not doable from a non-admin session.
> 2. **The WhatsApp-Web session must be HEADFUL** with mic permission — a **headless**
>    browser exposes no audio devices to `getUserMedia`. WPPConnect's default headless
>    server mode will not carry call audio.
> 3. **A live WhatsApp-Web session** (QR login) must exist, and a **real call from the
>    owner** must be placed — neither can be done unattended.
> 4. **Reliability** — WA-JS call events don't always fire (#3372); **echo/feedback** and
>    **turn-based latency** are real risks; and the media path is **entirely unproven
>    end-to-end**.

**Tested end-to-end 2026-09-04** (full write-up in [[WhatsApp Communication Knowledge/08 - Voice Pipeline Integration\|08]]):
blockers 1–3 were all **cleared** — VB-CABLE installed, a **headful** WhatsApp-Web session
reused the login (no QR, WA-JS 4.6), and the admin placed **real** calls. The **audio
routing is PROVEN** both ways (Vision→mic corr 1.006, caller→STT corr 0.933, isolation
0.000). **But the calls never reached the Web session** — no `incoming_call` event, no
entry in WhatsApp's own call store, no call UI (screenshotted mid-ring). WhatsApp's Web UI
states it: *"Download WhatsApp for Windows — get extra features like voice and video
calling."*

> **Verdict:** the WhatsApp-**Web** route **cannot** answer calls, because Web has **no
> calling feature** — the call rings the phone/native app, never the automatable Web
> client. The one unproven path left is the **native Windows app + desktop UI automation**
> (Desktop agent clicks Accept) on the same, already-proven VB-CABLE + loopback routing.
> No faking; messaging + voice-notes remain the shipped path.

## Consequence for the capability surface

The WhatsApp capability exposes **no call operations** today. `start_call` /
`get_call_state` / `end_call` are **not** implemented — building fake call operations
would be exactly the "invented results" the design forbids. Messaging is the shipped
capability.

## Unknown-call behavior (policy for when/if it becomes possible)

The trust rules for a call from a non-admin live in
[[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy\|12]]. Honestly
today, since call **audio** can't be answered, the feasible path on a detected incoming
call is: **detect** the call event (partial in WPPConnect, reliable in Baileys),
optionally **decline** it, then follow up by **message** with the Hindi receptionist
script and **notify Muaz** ([[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy\|12]]).
The spoken "Namaste, main Muaz ka assistant hoon…" answer is the **intended** behavior
for if/when a free stack can carry call audio — documented, not claimed to work.
