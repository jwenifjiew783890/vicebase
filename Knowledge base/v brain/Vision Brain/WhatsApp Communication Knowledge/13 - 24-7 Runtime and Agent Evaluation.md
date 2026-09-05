---
type: note
domain: WhatsApp Communication Knowledge
section: Runtime
created: 2026-09-04
---

# 24/7 WhatsApp Runtime & Agent Evaluation

Evaluation of whether Vision's current WhatsApp stack should be **kept or replaced**
for permanent 24/7 operation, plus the architecture of the persistent call watcher
built on 2026-09-04. Companion to
[[WhatsApp Communication Knowledge/07 - WhatsApp Calling|07]] (what calling can/can't do)
and [[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy|12]] (trust).

## The decisive constraint

Everything below follows from one fact that no library changes:

> **WhatsApp call *audio* is E2E-encrypted WebRTC/SRTP negotiated inside the client.
> No automation library — none — can inject or extract call audio.**

So "call support" in any project's README must be read carefully. Distinguish five
different things, because projects advertise (1)–(2) and people assume (5):

| # | Capability | Achievable free? |
| --- | --- | --- |
| 1 | Call **detection** (an event fires) | ✅ Baileys `call` event; WA-JS `incoming_call` |
| 2 | Call **control** (accept/reject/end signalling) | ✅ WA-JS 4.6 `call.accept/reject/end` |
| 3 | Audio **capture** of the caller | ❌ via library — ✅ via **WASAPI loopback** (OS layer) |
| 4 | Audio **injection** into the call | ❌ via library — ✅ via **VB-CABLE virtual mic** (OS layer) |
| 5 | Full AI **conversation** in a call | only by combining 1–4 at the **OS** layer |

**Consequence: a hybrid is not a compromise, it is the only correct architecture.**
Messaging belongs to a protocol/web library; calling belongs to the native Windows app
plus OS audio routing. Forcing one system to do both produces a worse result.

## Candidates evaluated (2026)

| Candidate | Kind | Verdict for Vision |
| --- | --- | --- |
| **WPPConnect / WA-JS** (current) | Browser (Chromium) automation of WhatsApp Web | **KEEP.** Actively maintained (WA-JS 4.5.0 released 2026-07-31; 4.4.3 2026-07-30; we run **4.6.0**). Already authenticated, session-persistent, LID→phone resolution proven, admin allowlist enforced, n8n wired, real Manager replies delivered. |
| **Baileys** (WhiskeySockets) | Protocol-level TS/WebSocket, **no browser** | Strongest *technical* alternative — most actively maintained low-level lib (~9.6k stars), far lighter than a Chromium session, and uniquely offers a **protocol-level `call` event** (caller JID, status `offer/ringing/reject/accept`). Rejected **for now**: migration cost + re-auth risk against a working session, and it still cannot carry call audio. |
| **Evolution API** | REST server over Baileys/whatsmeow | Free, OSS, excellent n8n story, big 2026 traction. Rejected: needs Docker + Postgres/Redis for a **single-user** need — heavier than the whole current bridge. |
| **WAHA** | Dockerised WhatsApp HTTP API | Core is MIT but **one session per container**; multi-session is paid (WAHA Plus). Fine for our 1 session, but adds Docker and replaces working code with no capability gain. |
| **whatsapp-web.js** | Browser automation | Same class as WPPConnect, no advantage over the incumbent. |
| **MCP WhatsApp servers** | MCP wrappers | Thin wrappers over the above libraries; add an abstraction layer without adding capability. Vision already reaches WhatsApp through n8n. |

**Decision rule applied:** replacement requires *measurable superiority for our use case*.
No candidate can do the one thing we actually lacked (call audio), and none beats a
working, authenticated, n8n-integrated session at messaging. **Verdict: KEEP WPPConnect
for messaging; add a native-Windows watcher for calls.**

Honest note on the runner-up: if the browser session ever becomes a reliability problem,
**Baileys is the migration target** — lighter, no Chromium, and its native `call` event
would replace the fallback half of the watcher's detection. Migrate only against a proven
PoC, never by swapping the live session.

## The persistent call watcher

`D:\vision-whatsapp-callwatcher\watcher.py` — a small local service. **Not** an
orchestrator: no LLM, no memory, no planning, no personality. It detects and controls
WhatsApp call UI and reports events. Vision remains the brain.

### Why it is event-driven, not a screenshot loop

Windows **UI Automation supports real event subscription**, and this was verified on this
machine before building (`uia_event_probe.py`): a `UIA_Window_WindowOpenedEventId` handler
registered on the desktop root fired a genuine callback carrying window name, PID and
class. Requirements discovered:

- `sys.coinit_flags = 0` (**MTA**) must be set *before* importing `comtypes`, so callbacks
  arrive on COM RPC threads and no message pump is needed. Setting the apartment after
  import raises `Cannot change thread mode after it is set`.

Detection is therefore:

- **Primary — UIA event subscription:** `WindowOpened` (call window appears) and
  `WindowClosed` (call ends). Idle cost ≈ zero; no screen capture at any point.
- **Safety net — cheap win32 sweep:** `EnumWindows` title check every 2s, filtered to the
  WhatsApp PID. This is a few string comparisons on existing handles — no screenshots and
  no UIA tree walk — and exists only to catch a call window that was already open when the
  watcher started, or a missed event. UIA work happens **only** after a candidate is found,
  and then only inside **that one window's** subtree.

### Lifecycle events emitted

`watcher_started`, `whatsapp_detected`, `whatsapp_unavailable`, `incoming_call`,
`caller_identified`, `caller_authorized`, `caller_rejected`, `call_accept_withheld`,
`watcher_armed` / `watcher_disarmed`, `call_accepted`, `call_connected`, `call_ended`,
`call_failed`, `watcher_stopped`, `watcher_crashed`.

Each is appended to `logs\events.jsonl` **and** POSTed to
`http://127.0.0.1:5678/webhook/whatsapp-call-event` (loopback n8n), mirroring the messaging
bridge's `whatsapp-in` convention. n8n being down never breaks call handling.

### Caller verification (identity, not display name)

Authorization uses **normalized phone identity** via the same rule as `bridge.js`
`normalize()` → `91XXXXXXXXXX`. Allowlist: `918095140130`.

The saved name **"Admin" is display metadata and is never sufficient on its own.** The
watcher records which one it actually matched:

- `identity_source: "phone_number"` + number on the allowlist → **strong** →
  `caller_authorized`.
- `identity_source: "display_name"` (the call UI exposed only the saved contact name, which
  WhatsApp often does) → **weak** → accepted *only* while an operator has explicitly armed
  the watcher, and the event records that basis honestly.
- Anything else → `caller_rejected`, left ringing. No auto-decline, no Vision control;
  the unknown-contact policy in
  [[WhatsApp Communication Knowledge/12 - Admin and Contact Trust Policy|12]] applies.

### Acceptance is gated

`auto_accept_authorized` is **false** by default. Acceptance requires an explicit
`POST /arm {token, seconds}` on loopback (bounded, max 1h). Un-armed, the watcher detects
and reports but emits `call_accept_withheld` instead of answering.

Accept/Decline are invoked through the **UIA `InvokePattern`** on the control whose Name is
`"Accept call"` (fallback `LegacyIAccessible.DoDefaultAction`) — a semantic invoke, **not a
coordinate click**. This is strictly better than the earlier PoC, which clicked the button's
reported (x,y).

### Startup, duplicates, recovery

- **Startup:** Scheduled Task *Vision WhatsApp Call Watcher*, trigger **AtLogOn**, action
  `.venv\Scripts\pythonw.exe watcher.py` (no console window).
- **Why a logon task and not a Windows service:** UI Automation can only see an
  **interactive desktop session**. A session-0 service would be blind to the WhatsApp
  window — as is WhatsApp itself, which also only runs in the user session.
- **Recovery:** task restarts every 1 min, up to 999 times, no execution time limit.
- **Duplicate protection:** the loopback health port **is** the lock — a second instance
  fails to bind and exits. (`MultipleInstances IgnoreNew` on the task as well.)
- **WhatsApp process detection:** `psutil` name check every 15s → `whatsapp_detected` /
  `whatsapp_unavailable`. Optional, rate-limited relaunch via `whatsapp://` is **off** by
  default.

### Health / observability

`GET http://127.0.0.1:8794/health` → status, uptime, `whatsapp_running`, `whatsapp_pid`,
`armed`, `accepts`, `active_call`, detection mode.
`GET /events` → last 30 lifecycle events. `POST /arm` / `/disarm` (token).

### Security boundaries

Loopback-bind only; inspects/invokes **only** windows owned by the WhatsApp process
(PID-checked); invokes **only** controls named `Accept call` / `Decline call`; executes no
arbitrary commands; reads no arbitrary files; auto-accept off by default and token-gated;
no LLM and no memory, so it cannot be prompt-injected into doing anything else.

### Resource usage

Idle: ~**54 MB** RSS, ~**0.2s** CPU total after startup. The Chromium messaging bridge
remains the heavier component by far.

## Reliability finding: duplicate bridge sessions (2026-09-04)

The messaging bridge was found reporting `status:"browserClose", loggedIn:false` while its
HTTP port still answered. Root cause: **two `bridge.js` processes were running at once**
(PIDs 14316, 15632), competing for the same WhatsApp session directory — the exact
"two systems competing for one account" failure mode. The bridge has **no autostart task**
and no single-instance guard of its own, so a manual restart can silently double it.

**Recommended (not yet applied):** collapse to one process, then give the bridge the same
treatment the watcher already has — an AtLogOn scheduled task plus a single-instance lock.
Fixing this is a prerequisite for genuine 24/7 messaging.

## Known limitations

1. The call UI may expose only the saved display name, not the number — see the weak/strong
   identity split above. Not faked, and recorded per event.
2. `call_ended` relies on the call window closing; a call that ends without the window
   closing would be missed until the next window event.
3. Audio (STT→LLM→TTS) is deliberately **not** wired into the watcher yet — call control
   must prove reliable first.
4. UIA requires an interactive session: if the user is logged out or the session is locked
   at the console level, detection stops.
5. Unofficial WhatsApp automation always carries WhatsApp-ToS/ban risk on the account.
