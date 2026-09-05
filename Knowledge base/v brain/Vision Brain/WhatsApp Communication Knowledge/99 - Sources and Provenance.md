---
type: note
domain: WhatsApp Communication Knowledge
section: Provenance
created: 2026-09-04
---

# Sources and Provenance

Every project and claim behind this domain, with licence, metadata, retrieval date,
and an honest verified-vs-unverified split. **Retrieval date: 2026-09-04.**

## Systems investigated (GitHub metadata, 2026-09-04)

| Project | Repo | Category | Licence | Stars / forks | Last push | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **WPPConnect Server** | `wppconnect-team/wppconnect-server` | **B** (Web automation) | **Apache-2.0** | 1047 / 773 | 2026-09-03 | **✅ Selected** |
| WPPConnect (lib) | `wppconnect-team/wppconnect` | B | NOASSERTION | 3413 / 559 | 2026-09-03 | library under the server |
| WAHA | `devlikeapro/waha` | B (multi-engine) | Apache-2.0 | 7331 / 1720 | 2026-09-01 | strong alt; **Plus tier is paid** |
| whatsapp-web.js | `pedroslopez/whatsapp-web.js` | B (library) | MIT | ~15k (well-known) | active | needs a custom server wrapper |
| Baileys | `WhiskeySockets/Baileys` | **C** (protocol) | MIT | 10949 / 3347 | 2026-09-03 | lightest; browserless; fallback |

Categories: **A** official (paid) API · **B** WhatsApp Web automation · **C**
unofficial protocol libraries. The owner's preference is **B**.

## Why WPPConnect Server was selected

- **Category B** — drives a real logged-in WhatsApp Web session locally (the stated
  goal), via the maintained WA-JS layer.
- **Fully free, no paid tier.** Apache-2.0 end-to-end. WAHA is excellent and has the
  smoothest n8n docs, but its **Plus** tier is **paid** — to guarantee ₹0/$0 with no
  paywalled features we take WPPConnect Server (or WAHA **Core** only).
- **Fits Vision's stack** — Node.js (like n8n), runs directly (npm) or Docker, no new
  language/runtime. Self-hosted, loopback-only.
- **Verified capabilities** (from its README, 2026-09-04): REST API + **Swagger**
  (`/api-docs`); **webhooks** for incoming messages + status/presence/group/reaction/
  poll/revoke events; **persistent session** tokens + Chromium profile (file /
  MongoDB / Redis; default file = local); **QR-once** login (`/start-session` returns
  base64 QR); **send/receive** text + image + video + docs; **contacts list**;
  **groups**; **secret-key Bearer** auth; auto webhook file-download.
- **No calls** — matches the honest calling reality below.

**Alternatives kept documented:** WAHA **Core** (free) for its native n8n webhook
flow if a Dockerised multi-engine setup is later preferred; **Baileys** if a
browserless, low-RAM, protocol-level bridge is ever wanted (category C, different
ban nuance). whatsapp-web.js is the library others wrap — using WPPConnect Server
avoids writing our own server.

## Verified vs not verified

- **Verified by research:** each project's capabilities, licences, activity; that
  WhatsApp added E2E calls to WhatsApp **Web** ~2026-07-28; that **no** free stack
  exposes call media; that the official calling path is a **paid** Business API.
- **NOT run on this machine yet (no theatre):** QR login, a real inbound message
  round-trip, an outbound send, any call test. These need Vision's own WhatsApp
  **number + a phone to scan the QR** and carry **ban risk** — the owner's
  deliberate step. No PoC result is claimed until actually executed.

## Calling — verified sources

- WhatsApp Web calling rollout (~2026-07-28): WABetaInfo / 9to5Mac / explainx (Feb &
  July 2026 coverage). A **human** can call in the Web UI now.
- Programmatic call audio is **not** available to WPPConnect / whatsapp-web.js /
  Baileys — WebRTC + E2E (SRTP/OPUS); the encrypted media stream isn't exposed to
  automation. The only programmatic path is Meta's **paid** WhatsApp Business Calling
  API (developers.facebook.com / webrtc.ventures). Full analysis in
  [[WhatsApp Communication Knowledge/07 - WhatsApp Calling\|07]].

## Zero-cost analysis

- **Implementation cost: ₹0 / $0 recurring.** WPPConnect Server is Apache-2.0,
  self-hosted, local. No API subscription, no paid SaaS, no paid WhatsApp Business
  API, no telephony provider.
- **WAHA Plus is paid and is not used** (Core only, if WAHA is ever chosen).
- **Unavoidable, already-owned costs:** the PC and the internet connection. No new
  monetary dependency is introduced.

## Terms / account-risk analysis (not hidden)

- All category-B/C approaches are **unofficial** and **violate WhatsApp's Terms**
  (automated/unauthorised clients). **Ban risk is real.**
- Higher risk with: new numbers, volume, messaging non-contacts, bursts, spam
  patterns. Lower risk with: a dedicated owned number, low one-to-one volume,
  gradual warm-up, known contacts only. Mitigations in
  [[WhatsApp Communication Knowledge/11 - Reliability and Failure Recovery\|11]].
- This is a **personal** Vision account, **not** a mass-messaging/spam service.

## Vault cross-references (internal)

- [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]] — wording/voice of replies.
- [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|Intent & Task Understanding]] — understanding inbound requests.
- **Coding Knowledge** — engineering the bridge, if extended.
- Registry source of truth: `D:\n8n\workflows\agent-registry.json` (+ `_generate_hub.py`, `plan-registry.json`).

## Web sources

WABetaInfo (WhatsApp Web calls), 9to5Mac 2026-02-09, explainx 2026-07, freeCodeCamp
"Self-Hosted WhatsApp Bot with n8n and WAHA", indiehackers 2026 self-hosted
round-ups, project READMEs (WPPConnect Server, WAHA, Baileys), Meta WhatsApp Business
Calling API docs (for the rejected paid path).
