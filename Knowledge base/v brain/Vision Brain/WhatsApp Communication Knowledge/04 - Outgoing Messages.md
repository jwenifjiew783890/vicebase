---
type: note
domain: WhatsApp Communication Knowledge
section: Outgoing Messages
created: 2026-09-04
---

# Outgoing Messages

Vision-initiated messages: the Manager places a **send** stage in a plan; the
WhatsApp capability delivers it and reports the result back.

## The operation

`whatsapp.send_message( to, text )` → WPPConnect Server `POST /api/{session}/send-message`
→ returns a delivery result (queued/sent + message id, or an error).

- **to** comes from controlled contact resolution
  ([[WhatsApp Communication Knowledge/05 - Contacts and Identity Resolution\|05]]) —
  never a raw, unverified target pulled from message text.
- **text** is worded by the LLM under
  [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]]
  (natural, register-matched).

## As a plan stage

```
PLAN: Contact Person
  1. resolve contact            → 05
  2. prepare message (LLM)      → Conversation Knowledge
  3. whatsapp.send_message      → this note
  4. report result to the user  → success/failure surfaced, not assumed
```

Or as the tail of a larger plan:

```
Browser Agent downloads the report → Desktop Agent saves it
  → whatsapp.send_message("done — report is saved to …")
```

## Rules

- **Report the real result.** Surface sent / failed (with the reason) back into the
  plan. Never assume delivery — WhatsApp can reject (not a contact, invalid number,
  session down [[WhatsApp Communication Knowledge/11 - Reliability and Failure Recovery\|11]]).
- **Confirm sensitive sends.** Messaging a *new* person, anything with money or
  personal-data implications, or a bulk of recipients → confirm with the owner first
  ([[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10]]). Replying
  to an allowlisted inbound thread needs no extra confirmation.
- **No bulk / no spam.** One-to-one, human-paced. This is a personal assistant
  channel, not a broadcast tool — bulk sending is the fastest route to a ban
  ([[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]]).
- **Rate-limit** outbound sends and space them; never blast.
