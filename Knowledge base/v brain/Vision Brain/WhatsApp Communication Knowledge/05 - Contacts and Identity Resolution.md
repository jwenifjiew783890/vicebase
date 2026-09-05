---
type: note
domain: WhatsApp Communication Knowledge
section: Contacts & Identity Resolution
created: 2026-09-04
---

# Contacts & Identity Resolution

Turning "message Ahmed" into a **verified** WhatsApp target — safely. The system must
**never** accept an arbitrary, unverified contact/number/target from message text.

## Resolution order

1. **Explicit phone number**, when the user gives one (validated E.164-ish format).
2. **Known / saved WhatsApp contact** — resolved via WPPConnect `get-contact` /
   contact list against a **maintained allowlist/address book** the owner controls.
3. **Clearly resolved contact name** — a name that maps to exactly one saved,
   trusted contact.
4. **Ambiguous → confirm.** More than one match, a fuzzy name, or no confident match
   → **ask the owner** which contact (or refuse) before sending. Never guess a
   recipient.

## Rules

- **Controlled targets only.** Recipients come from the owner's trusted address book
  or an explicitly-supplied number — not scraped from arbitrary text, not a number a
  stranger messaged in.
- **Confirmation on material ambiguity** (Part 4 requirement): if getting it wrong
  would message the wrong person, confirm. Silence is not consent.
- **Separate "who asked" from "who to message".** An inbound message from an
  allowlisted sender authorises *acting*; it does not authorise messaging *anyone* —
  the recipient still goes through this resolution.
- **Identity for inbound** ([[WhatsApp Communication Knowledge/03 - Incoming Messages\|03]]):
  the sender id (`from`) is normalised and matched against the **admin identity**
  (`8095140130` → `918095140130@c.us` — the only trusted controller today,
  [[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy\|12]]); an
  unknown sender is handled as a receptionist interaction and never reaches
  contact-resolution for outbound at all.

## Address book

- A small, owner-curated mapping `name → whatsapp id`, stored locally (not derived
  from arbitrary chats). The owner expands it deliberately.
- Cross-check against Vision's people memory
  (`Memory/06 - Relationships & People`) for *display* only — the **authoritative**
  send target is the curated WhatsApp id, never a guessed one.
