---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Backend Architecture

Layering a server so that business rules survive changes to everything around them.

## The layering that works

```
transport   (HTTP handlers, WebSocket handlers, CLI, queue consumers)
    v        validate input, map to domain calls, map results to responses
service     (business rules, orchestration, transactions)
    v        knows nothing about HTTP
repository  (data access)
    v
database
```

The rule that gives this value: **the service layer must not know it is being called over
HTTP.** No request objects, no status codes, no framework types below the transport layer. Then
the same logic serves an HTTP endpoint, a queue consumer and a test, unchanged.

The inverse - business logic in route handlers - is the most common backend structure and the
most expensive, because nothing can be reused or tested without a web server.

## Request handling

- **Validate at the edge**, once, into a typed structure. Everything below assumes validity.
- **One transaction per request**, opened as late and closed as early as possible. Never hold a
  transaction across an external network call.
- **Return early on error.** Deeply nested happy paths are where edge cases hide.
- **Set a timeout on every outbound call**, and make the total request timeout shorter than the
  client's.
- **Make handlers idempotent** where the client can retry.

## Background work

Anything slow, retryable or non-essential to the response belongs on a queue: email, image
processing, exports, webhooks, indexing.

- **Persist the job before returning success** to the caller, or a crash loses it.
- **Jobs must be idempotent** - at-least-once delivery is the norm.
- **Bound retries** and route exhausted jobs to a dead-letter queue that someone actually looks
  at.
- **Monitor queue depth and age.** A growing backlog is the earliest signal of trouble, and it
  is invisible from request metrics.

## Configuration

From the environment, not the artefact - so the same build runs in every environment. Validate
all configuration **at startup** and fail immediately if something required is missing. A
service that starts successfully and fails on the first request that needs a missing variable
has converted a deploy-time error into a production incident.

## Statelessness

Keep request handling stateless so instances are interchangeable. In-memory session state,
in-memory caches assumed to be shared, and local file writes all break horizontal scaling and
produce the "works until we add a second instance" class of bug.

## Failure modes

- **Business logic in route handlers.**
- **The ORM as the domain model**, so persistence concerns dictate business structure.
- **Transactions held across HTTP calls**, causing lock pile-ups.
- **No request timeout**, so slow dependencies exhaust the worker pool.
- **Synchronous work that should be queued** - email in the request path is the classic.
- **Configuration read lazily**, failing in production rather than at boot.
- **Local state** assumed to be shared across instances.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/REST|REST]]
- [[Coding Knowledge/05 - Web & Application Engineering/Databases|Databases]]
- [[Coding Knowledge/01 - Software Engineering/Architecture Fundamentals|Architecture Fundamentals]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- The Twelve-Factor App - <https://12factor.net/> (repository CC BY 4.0, verified 2026-09-03); Martin Fowler, *Patterns of Enterprise Application Architecture* (2002) - cited, not reproduced.
