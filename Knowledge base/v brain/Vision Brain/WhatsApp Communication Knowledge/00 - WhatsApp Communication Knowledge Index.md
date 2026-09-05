---
type: MOC
role: domain index
domain: WhatsApp Communication Knowledge
created: 2026-09-04
---

# WhatsApp Communication Knowledge

How Vision uses a **real, logged-in WhatsApp account on this PC** as another
interface to the *same* Vision — to receive messages, act on them, and reply, and
(where a person drives it) to send messages to contacts. WhatsApp is an
**execution channel / capability**, not intelligence.

> **WhatsApp is not the brain.** The brain stays: Vision's LLM, [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]]
> for *how* it talks, [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|Intent & Task Understanding]]
> for *what* a request means, the **Manager / Plan Registry** for *what to do*, and
> the existing agents (Browser, Desktop, OpenCode…) + OmniVoice for doing/speaking
> it. This domain adds **no** second orchestrator and **no** second brain.

## The architecture (one Vision, another door)

```
PHONE → WhatsApp → Vision's own number → local WhatsApp bridge (WPPConnect Server)
      → webhook event → n8n → VISION - AGENTS (Manager)
      → Intent & Task Understanding → Plan → Browser / Desktop / LLM / OmniVoice
      → result → WhatsApp reply → PHONE
```

Reverse (Vision-initiated): `Manager → Plan → resolve contact → WhatsApp capability
(send_message / send_media) → contact`. The WhatsApp capability is one more **stage
type** the Manager can place in a plan — it cooperates with Browser/Desktop, it does
not replace them.

## Selected system (evidence-based — see [[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]])

**WPPConnect Server** (`wppconnect-team/wppconnect-server`, Apache-2.0) — a
self-hosted local **WhatsApp Web automation** bridge: REST + Swagger + **native
webhooks**, persistent session tokens, QR-once login, send/receive/media/contacts/
groups, secret-key auth. **Zero recurring cost, fully open, no paid tier.** It
**does not do calls** — see [[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07]].

## Notes

| Note | Covers |
| --- | --- |
| [[WhatsApp Communication Knowledge/01 - WhatsApp Architecture\|01 · Architecture]] | Where the bridge sits; A/B/C approaches; why a dedicated bridge (not Auto Browser) |
| [[WhatsApp Communication Knowledge/02 - Local Session and Authentication\|02 · Session & Auth]] | QR-once, persistent tokens, where session state lives, keeping it local |
| [[WhatsApp Communication Knowledge/03 - Incoming Messages\|03 · Incoming Messages]] | Webhook events → n8n → Manager; metadata; events over polling |
| [[WhatsApp Communication Knowledge/04 - Outgoing Messages\|04 · Outgoing Messages]] | Manager-invoked `send_message`; delivery result back to the plan |
| [[WhatsApp Communication Knowledge/05 - Contacts and Identity Resolution\|05 · Contacts & Identity]] | Controlled resolution: explicit number / saved contact / confirm on ambiguity |
| [[WhatsApp Communication Knowledge/06 - Media and Document Handling\|06 · Media & Documents]] | Send/receive files with controlled, non-arbitrary paths |
| [[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07 · Calling]] | **Honest reality:** messaging works; programmatic call audio does **not** |
| [[WhatsApp Communication Knowledge/08 - Voice Pipeline Integration\|08 · Voice Pipeline]] | The desired STT→LLM→OmniVoice call pipeline and exactly why it's blocked today |
| [[WhatsApp Communication Knowledge/09 - n8n Manager and Plan Integration\|09 · n8n / Manager / Plan]] | Registry source-of-truth, the agent+tools entry, plan stages |
| [[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10 · Security & Trust]] | Allowlist, message≠command, confirmations, no shell/FS/creds |
| [[WhatsApp Communication Knowledge/11 - Reliability and Failure Recovery\|11 · Reliability]] | Session drops, reconnect, clean failure reporting, ban-risk mitigation |
| [[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy\|12 · Admin & Contact Trust]] | The admin identity (`8095140130`); admin = owner interaction; unknown = Hindi receptionist with zero control; notifying Muaz; "who called?" recall |
| [[WhatsApp Communication Knowledge/13 - 24-7 Runtime and Agent Evaluation\|13 · 24/7 Runtime & Agent Evaluation]] | Keep-or-replace verdict (WPPConnect vs Baileys / Evolution / WAHA), the five distinct levels of "call support", and the event-driven native-WhatsApp call watcher (UIA subscription, arming, recovery) |
| [[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99 · Sources & Provenance]] | Every project examined, licence, metadata, retrieval date, ToS/ban analysis |

## What is verified vs not (no theatre)

- **Verified by research (2026-09-04):** the capability set of each project, licences,
  activity, that WPPConnect Server exposes REST+webhook+persistent-session, that
  **none** of the free libs carry call audio.
- **Not yet run here:** the live PoC (QR login, a real phone message round-trip, an
  outbound send). Those need Vision's own WhatsApp **number + a phone to scan the QR**
  and carry **account-ban risk** ([[WhatsApp Communication Knowledge/11 - Reliability and Failure Recovery\|11]],
  [[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]]) — so they are
  the owner's deliberate step, documented, never faked.

## How this domain relates to the others

- [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]] → *how* the WhatsApp reply is worded (casual, register-matched, voice-style when spoken).
- [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|Intent & Task Understanding]] → *what* an incoming message means and how it's planned.
- **Manager / Plan Registry** → *what to do*. This domain only *communicates through WhatsApp*.
- **Coding Knowledge** → the engineering of the bridge service, if it is ever extended.
