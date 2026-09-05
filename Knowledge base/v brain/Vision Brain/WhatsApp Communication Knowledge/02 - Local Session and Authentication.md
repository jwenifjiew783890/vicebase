---
type: note
domain: WhatsApp Communication Knowledge
section: Session & Authentication
created: 2026-09-04
---

# Local Session & Authentication

Vision's WhatsApp account is logged in **once** on this PC and stays logged in. No
QR every task, no fresh profile per run.

## How login works (WPPConnect Server, verified capability)

1. Start the bridge; call `POST /api/{session}/start-session`.
2. It returns a **base64 QR code**. The owner scans it **once** from the phone that
   holds Vision's WhatsApp number (WhatsApp → Linked Devices → Link a device).
3. WhatsApp Web links the PC as a companion device. From then on the bridge
   reconnects automatically using the stored session — **no re-scan** unless the
   device is unlinked or the token is deleted.

> Scanning the QR **links a real account** and begins WhatsApp-Web automation, which
> is against WhatsApp's Terms and carries ban risk. This is the owner's deliberate,
> informed step — see [[WhatsApp Communication Knowledge/11 - Reliability and Failure Recovery\|11]]
> and [[WhatsApp Communication Knowledge/99 - Sources and Provenance\|99]]. Use a
> number Vision owns, not a primary personal number.

## Where session state lives (kept local & protected)

- WPPConnect Server persists a **session token** and the **Chromium profile** for the
  session. Backends: **file** (default), MongoDB, or Redis. Default file storage
  keeps everything on this PC.
- Store it under the bridge's own directory (e.g. `D:\vision-whatsapp\tokens\`),
  readable only by the owner's account. Treat it like a credential: it grants
  message access to the account.
- **Do not** copy session tokens into n8n, into the vault, into agent tool inputs, or
  anywhere they'd be logged. n8n and the agents only ever see **message events** and
  call **messaging operations** — never the raw session.

## Persistence rules

- **One session, long-lived.** Reuse it across all tasks; never start a new profile
  per task.
- **Auto-reconnect** on transient drops; only re-QR if the session is genuinely
  invalidated (unlinked, logged out, token deleted) —
  [[WhatsApp Communication Knowledge/11 - Reliability and Failure Recovery\|11]].
- **Secret-key auth** on the bridge: WPPConnect Server issues per-session Bearer
  tokens from a server secret. n8n authenticates to the bridge with that token over
  **loopback only** (`127.0.0.1`) — the bridge is never exposed off-machine.

## Backups

Before any change to the bridge config, copy `config` + `tokens` aside (dated). The
session token is the expensive thing to lose — losing it means a re-scan.
