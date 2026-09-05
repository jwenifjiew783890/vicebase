---
type: note
domain: WhatsApp Communication Knowledge
section: Reliability & Failure Recovery
created: 2026-09-04
---

# Reliability & Failure Recovery

WhatsApp Web automation is inherently less stable than an official API. Fail
**cleanly and visibly**, never silently.

## Failure modes and handling

| Failure | Detect | Handle |
| --- | --- | --- |
| Session dropped / disconnected | bridge status / webhook stops | auto-reconnect; report "WhatsApp offline" to the plan; **do not** silently drop a send |
| Session invalidated (unlinked/logged out) | start-session needs QR again | surface "re-link needed"; owner re-scans once ([[WhatsApp Communication Knowledge/02 - Local Session and Authentication\|02]]) |
| Send rejected (not a contact / invalid number) | REST error | return failure + reason to the Manager ([[WhatsApp Communication Knowledge/04 - Outgoing Messages\|04]]); never report success |
| WhatsApp Web UI/protocol change breaks the lib | errors spike | pin a known-good bridge version; update deliberately; the mature project tracks WA changes |
| Bridge process down | health check fails | Manager reports the channel is unavailable; other agents unaffected |
| Webhook retry (duplicate event) | message id | de-duplicate ([[WhatsApp Communication Knowledge/03 - Incoming Messages\|03]]) |

## Rules

- **Never fake success.** A send is "sent" only on a real positive result; otherwise
  it's a reported failure with the reason.
- **Isolate the blast radius.** If WhatsApp is down, the rest of Vision keeps working
  — the WhatsApp stage fails, the plan reports it, nothing else breaks.
- **Health check** the bridge before a plan that depends on it; short-circuit early
  with a clear message rather than hanging.

## Account-ban / Terms risk (read this)

WhatsApp Web automation is **against WhatsApp's Terms of Service**. Realistic risks:

- **Ban risk is real**, and higher for: brand-new numbers, high message volume,
  messaging many non-contacts, spam-like patterns, and rapid bursts.
- **Mitigations** (this is a personal assistant, not a mass-messaging tool):
  - Use a **dedicated number Vision owns** — never a primary personal number.
  - **Warm up** a new number gradually; keep volume low and human-paced.
  - **One-to-one** with known contacts; **no bulk**, no cold outreach.
  - Rate-limit; add natural spacing; don't run 24/7 blasting.
  - Accept that the account **can** be banned; keep nothing irreplaceable on it.
- This is disclosed plainly, not hidden. The owner takes on this risk knowingly when
  they scan the QR ([[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]]).
