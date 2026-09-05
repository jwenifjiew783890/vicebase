---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# WebSockets

Persistent bidirectional connections, and the operational cost that is usually underestimated.

## When you actually need one

Only when the **server must push** without being asked, at low latency: live collaboration,
chat, multiplayer, live dashboards, streaming progress.

Not needed for: occasional updates (poll), one-way server-to-client streams (Server-Sent Events
are simpler, work over plain HTTP, and reconnect automatically), or request/response (that is
HTTP).

**Prefer SSE for one-way streaming.** It is dramatically less operational work, and most
"real-time" requirements are one-way.

## What changes when the connection is persistent

- **The server holds state per connection.** Memory scales with connected clients, not with
  request rate.
- **Load balancing needs sticky routing** or a shared backplane (Redis pub/sub, a message bus),
  because the client is attached to one instance.
- **Deploys drop every connection.** Clients must reconnect, and the application must survive
  a reconnect storm when a thousand clients return simultaneously - stagger with jittered
  backoff.
- **Authentication happens once**, at connect. Long-lived connections must handle token
  expiry mid-connection; decide whether to re-authenticate or close.
- **Proxies and load balancers idle-timeout** connections. Heartbeats are required, not optional.

## Protocol discipline

- Define a **message envelope** with a type field and a version from the start.
- **Sequence numbers** so clients can detect gaps after a reconnect.
- **Server-side state resync on reconnect** - the client must be able to ask "what did I miss?",
  or it will silently diverge.
- **Back-pressure**: if a client cannot keep up, buffer bounded and then drop or disconnect.
  An unbounded per-connection send buffer is a memory exhaustion vector.
- **Validate every inbound message.** A WebSocket is an open door for the whole session; it
  needs the same input validation as any endpoint, on every message.

## Security

- `wss://` always.
- **Check the `Origin` header on the handshake** - WebSockets are not subject to the same-origin
  policy, and cookie-based auth without an origin check is cross-site WebSocket hijacking.
- Authorise **per message**, not only at connect, for anything sensitive - permissions can change
  during a long-lived session.
- Rate-limit inbound messages per connection.
- Cap message size and connection count per user.

## Failure modes

- **No heartbeat**, so half-open connections accumulate: the server believes clients are
  connected and messages vanish.
- **No reconnect logic**, or reconnect without backoff, producing a thundering herd after a
  deploy.
- **State assumed in sync** after a reconnect, so the client shows stale data indefinitely.
- **Unbounded send buffers.**
- **No origin check** on the handshake.
- **Using WebSockets where polling would do**, buying a large operational burden for nothing.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/REST|REST]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- RFC 6455 (WebSocket protocol) - <https://www.rfc-editor.org/rfc/rfc6455>; MDN on WebSockets and Server-Sent Events - <https://developer.mozilla.org/> (CC BY-SA 2.5, facts restated); OWASP guidance on cross-site WebSocket hijacking - <https://cheatsheetseries.owasp.org/> (CC BY-SA 4.0).
