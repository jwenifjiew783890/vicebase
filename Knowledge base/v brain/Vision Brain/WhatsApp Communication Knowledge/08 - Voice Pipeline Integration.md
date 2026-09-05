---
type: note
domain: WhatsApp Communication Knowledge
section: Voice Pipeline Integration
created: 2026-09-04
---

# Voice Pipeline Integration

The **desired** future pipeline for a spoken WhatsApp call, and an honest statement
of where it is blocked. Vision's voice stack is unchanged and **not** replaced.

## The desired pipeline (future, not active)

```
Incoming call audio → STT (Vision's Whisper) → Vision LLM → OmniVoice TTS
                    → WhatsApp call audio out
```

Outbound: `Manager → call plan → (call connected) → OmniVoice speaks → capture reply
→ STT → LLM → …`.

The brain and voice are the existing ones — **LLM = Vision's brain, STT = Vision's
Whisper, TTS = OmniVoice/VoiceStudio**. This note would only add the *plumbing*
between a live call's audio and that pipeline.

## Two ways to get the call audio — and where each stands

The two missing arrows are **read remote audio → STT** and **write OmniVoice → call**.
There are two ways to get them; the second is the one investigated 2026-09-04.

### Approach 1 — raw WebRTC/SRTP interception (rejected)

Reach into the E2E-encrypted call media directly. Neither WPPConnect/whatsapp-web.js
nor Baileys expose it, and the browser WebRTC sandbox does not hand out raw SRTP
([[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07]]). **Not possible for free — abandoned.**

### Approach 2 — Windows audio-**device** routing (investigated, coherent, UNPROVEN)

The key insight: **you do not need the encrypted stream.** WhatsApp Web does the WebRTC
normally; we take the audio **after it is decrypted** (playback) and inject **before it
is encrypted** (the browser's microphone input), using ordinary Windows audio devices:

```
remote caller ─(WhatsApp WebRTC, decrypted by the browser)→ default RENDER device
        → WASAPI loopback capture → Vision Whisper (STT) → Vision LLM
        → OmniVoice (Option D) → a virtual-cable INPUT (playback)
        → the same cable's OUTPUT, selected as the browser's mic
        → WhatsApp Web getUserMedia → encrypted by the browser → caller hears Vision
Call control (accept/end): WA-JS 4.6 in the SAME browser session.
```

**Component status (honest):**

| Piece | Finding (2026-09-04) |
| --- | --- |
| **Call control** (accept/offer/end/reject, `incoming_call` event) | WA-JS exposes `WPP.call.accept/offer/end/reject`; **v4.5.1 (2026-08) fixed accept/reject/end** on WhatsApp's VoIP stack. So programmatic **accept is real** — with reliability caveats (wa-js issue #3372, events not always firing). |
| **Inject OmniVoice → mic** | Needs a **virtual audio cable** (e.g. VB-CABLE) whose *Output* Windows presents as a microphone. **None installed on this machine, and installing one needs admin + a reboot** (this session is not elevated). Blocked pending that install. |
| **Capture remote audio** | **WASAPI loopback** on the render endpoint can capture what the browser plays — no cable and no stream access needed. Untested (needs a live call to produce audio). |
| **Browser must be HEADFUL** | Confirmed catch: a **headless** browser (WPPConnect Server's default) does **not** expose usable audio devices to `getUserMedia`. The call must run in a **headful** browser with mic permission granted. |
| **STT / LLM / TTS** | All exist and work (Whisper; Vision LLM; OmniVoice Option D, ~0.9–1.7 s warm). |

**Approach 2 — LIVE TEST RESULT (2026-09-04): audio bridge PROVEN; calling BLOCKED at the WhatsApp-Web layer.** PoC at `D:\vision-voice\whatsapp-call-poc\`. VB-CABLE was installed, a **headful** WhatsApp-Web session reused the existing login (no QR, WA-JS 4.6), and the admin placed **real** calls.

- **Audio routing — PROVEN both directions, echo-safe.** OmniVoice → `CABLE Input` →
  `CABLE Output` (Vision → the call mic; corr **1.006**); caller-render → **WASAPI
  loopback** → STT (corr **0.933**); and Vision's output does **not** leak into the STT
  capture (**isolation RMS 0.000** → no self-echo). Device-targeted output + mic
  privacy verified. This half is done and reusable.
- **Call-control API present.** WA-JS 4.6 exposes `call.accept/end/offer` and
  `enableCallInterface()` ran fine on the headful, logged-in session.
- **THE BLOCKER — WhatsApp *Web* does not do calls.** On real admin calls the Web
  session got **no** `incoming_call` event, **no** entry in WhatsApp's own call store,
  and **no** call UI ever appeared (screenshotted mid-ring). WhatsApp's own Web UI says
  it outright: *"Download WhatsApp for Windows — get extra features like voice and video
  calling."* The call rings the phone and the **native** desktop app; it never reaches
  the automatable **Web** client, so WA-JS's `accept` has nothing to accept.

**Conclusion:** the WPPConnect / WhatsApp-**Web** route **cannot** answer calls — not
because of encrypted streams (that is sidestepped), but because the Web client has **no
calling feature at all**. Not a guess: tested on real calls with visual proof.

**Remaining candidate (unproven):** the **native WhatsApp Windows app** *does* receive
calls and uses the OS audio devices — so answering via **desktop UI automation**
(Vision's Desktop agent clicking "Accept" + reading call state) on top of this same,
already-proven VB-CABLE + loopback routing could work. Different architecture, not yet
tested. Messaging + async voice-notes remain the shipped voice-on-WhatsApp path.
[[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07]] has the capability table.

## What already works (and can be used now)

Everything except the call itself:

- **STT** — Vision's Whisper (proven in the voice work).
- **LLM** — Vision's brain, unchanged.
- **OmniVoice TTS** — proven; warm synth ~0.9 s (see `D:\vision-voice\`).
- So a **voice-note** style interaction is feasible *without* a live call: receive a
  WhatsApp **audio message** → STT → LLM → OmniVoice → send a WhatsApp **audio
  message** back. This is asynchronous voice, not a live call, and it rides the
  normal messaging capability — a realistic near-term "voice on WhatsApp" that does
  **not** need the blocked call-media hooks. (To be validated in a later PoC; not
  yet run.)

## Rule

Do **not** claim live-call voice works. If/when a free stack can place/answer a call
*and* expose its audio, revisit — until then, the voice pipeline attaches to
**messages and voice-notes**, never to a live call. No faking, no "should work".
