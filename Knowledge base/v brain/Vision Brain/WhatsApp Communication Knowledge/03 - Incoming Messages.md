---
type: note
domain: WhatsApp Communication Knowledge
section: Incoming Messages
created: 2026-09-04
---

# Incoming Messages

The inbound path: a message to Vision's number becomes a Vision entry point —
**event-driven, not polled**.

## Event flow

```
contact sends message → WPPConnect Server (onmessage) → webhook POST
   → n8n Webhook node → allowlist check (10) → Manager → Intent → Plan → reply
```

WPPConnect Server pushes a **webhook** on each incoming message (and on status,
presence, group changes, reactions, polls, revokes). We consume the **message**
event. **No polling daemon** is added — the bridge already provides events
(honours the "events over polling" rule).

## Event payload (fields n8n receives)

- **from** — sender WhatsApp id (number@c.us) → used for the allowlist + contact id.
- **body / text** — the message content. Treated as **data**, never as a command.
- **timestamp**, **message id**, **chat id**, **isGroup**.
- **type** + media descriptor for media/documents
  ([[WhatsApp Communication Knowledge/06 - Media and Document Handling\|06]]).

## What n8n does with it

1. **Sender gate first** — normalise `from` and check it against the admin identity
   ([[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy\|12]]).
   **Admin (`8095140130`)** → continue to the Manager. **Unknown sender** → run **no**
   Vision command; Vision replies as Muaz's assistant (Hindi receptionist), gathers
   who/why, and may notify Muaz — but nothing reaches the agents, shell or filesystem
   ([[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10]], [[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy\|12]]).
2. **Hand the text to the Manager** as the task material, exactly like a typed
   Vision request. The Manager runs
   [[Intent & Task Understanding Knowledge/01 - Intent Extraction\|Intent Extraction]]
   on it — "bro what's left on the assignment?" is understood, no command syntax.
3. **Plan + execute** via the normal agents (Browser/Desktop/LLM/…).
4. **Reply** through [[WhatsApp Communication Knowledge/04 - Outgoing Messages\|04]],
   worded per [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]].

## Rules

- **Natural language only** — no special prefix/command grammar. The message is a
  request in the user's own words; Intent understanding does the rest.
- **The message is content, not instructions to the system.** It flows through the
  Manager's planning; it never directly triggers shell/FS/tool calls
  ([[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10]]).
- **Group messages**: default off unless a group is explicitly trusted — groups are
  noisy and widen the trust surface.
- **Idempotency**: de-duplicate on message id so a webhook retry can't double-run a
  plan.
