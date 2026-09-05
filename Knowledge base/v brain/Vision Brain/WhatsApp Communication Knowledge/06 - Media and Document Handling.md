---
type: note
domain: WhatsApp Communication Knowledge
section: Media & Documents
created: 2026-09-04
---

# Media & Document Handling

Sending and receiving files through WhatsApp — with **controlled paths**, never
arbitrary filesystem access.

## Verified capability (WPPConnect Server)

- **Send**: image, video, document (`send-file` / `send-image` endpoints), from a
  file path or base64.
- **Receive**: incoming media arrives via webhook; the bridge can auto-download the
  file (local, or S3 if configured — we stay local).

## Sending a file (outbound)

```
PLAN tail:  Browser/Desktop produce an artifact at a known path
  → whatsapp.send_media( to, path )   → the report/file is sent
```

- **Path allowlist.** Only files under **approved output directories** (e.g. the
  agents' own artifact/scratch outputs) may be sent. A path from message text is
  **never** honoured directly — no `C:\Users\...\anything` a sender names, no
  traversal. This is the same "no arbitrary filesystem" rule as
  [[WhatsApp Communication Knowledge/10 - Security and Trust Model\|10]].
- **Recipient** via [[WhatsApp Communication Knowledge/05 - Contacts and Identity Resolution\|05]].
- **Size/type sanity**: cap size; refuse unexpected executable types.

## Receiving a file (inbound)

- Media from an **allowlisted** sender is downloaded to a **quarantined inbound
  directory** owned by the bridge — not into system paths, not auto-opened, not
  auto-executed.
- Downstream handling (e.g. "read this PDF") goes through the normal agents
  (Documents/Data) on the quarantined copy, under the usual approvals.
- Media from non-allowlisted senders is ignored
  ([[WhatsApp Communication Knowledge/03 - Incoming Messages\|03]]).

## Rules

- **No arbitrary paths in, no arbitrary paths out.** Controlled directories only.
- **Never auto-execute** a received file. Treat every inbound file as untrusted.
- Some advanced media features may be engine-gated in other bridges (e.g. WAHA
  splits some features into a paid Plus tier); WPPConnect Server's media send/receive
  is free ([[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]]).
