---
type: note
domain: WhatsApp Communication Knowledge
section: Architecture
created: 2026-09-04
---

# WhatsApp Architecture

Where the WhatsApp capability sits, and why it is a **dedicated local bridge** rather
than a job for an existing agent.

## Three families of approach (and which we use)

| | Approach | Cost | Fit |
| --- | --- | --- | --- |
| **A** | Official **WhatsApp Business Cloud API** / Business Calling API | **Paid** (Meta) | ❌ Rejected — violates the zero-cost rule; heavyweight; not "our own logged-in number" |
| **B** | **WhatsApp Web automation** (WPPConnect / whatsapp-web.js / WAHA WEBJS) | Free, self-host | ✅ **Chosen** — drives a real logged-in WhatsApp Web session locally |
| **C** | **Unofficial protocol** libraries (Baileys) | Free, self-host | ➖ Considered — lightest (no browser) but protocol-level; kept as a documented fallback |

We use **B**, per the owner's preference for controlling a real logged-in
Web/Desktop session locally. The chosen implementation is **WPPConnect Server**
(see [[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]]).

## Why a dedicated bridge, not Auto Browser or Windows-MCP

The control surface was chosen deliberately (not assumed):

- **Not Auto Browser.** The Browser Agent / Auto Browser is a *general, allowlisted*
  browser executor for arbitrary web tasks. WhatsApp needs a **single, persistent,
  authenticated** session with **event push** and robustness against WhatsApp Web's
  changing DOM. A mature bridge (WPPConnect uses the maintained WA-JS layer) is far
  more reliable for this than scripting the DOM through the general browser, and it
  keeps the authenticated WhatsApp session **isolated** from general browsing.
- **Not Windows-MCP.** The Desktop Agent / Windows-MCP is for OS-level UI and would
  only matter for **audio routing during a call** — and call audio is **not
  achievable** anyway ([[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07]]).
  So Windows-MCP has no role here today.
- **A dedicated bridge (chosen).** Its own process + its own persistent browser
  profile, exposing a small local REST/webhook surface that n8n talks to. This is
  the least-invasive, most reliable option, and it cooperates with the other agents
  through the Manager rather than duplicating them.

## The data flow

```
Inbound:  contact → WhatsApp → Vision's number → WPPConnect Server (webhook)
          → n8n webhook → Manager → Intent → Plan → agents/LLM/OmniVoice
          → send_message → reply

Outbound: Manager → Plan stage "whatsapp.send_message" → WPPConnect REST
          → WhatsApp → contact
```

The bridge is **thin**: it moves messages and events in and out. All *deciding*
happens upstream in the Manager. This is the boundary that keeps WhatsApp a
capability and not a second brain.

## Boundaries

- The bridge exposes **only** messaging operations (send/read/media/contacts) — no
  shell, no filesystem browsing, no arbitrary HTTP. Security in
  [[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10]].
- The bridge **holds the WhatsApp session**; it does not hand session tokens to n8n
  or to any agent tool ([[WhatsApp Communication Knowledge/02 - Local Session and Authentication\|02]]).
