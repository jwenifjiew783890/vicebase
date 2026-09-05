---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# REST

Using HTTP as designed, so that caches, proxies, clients and monitors all behave.

## Why the semantics matter

HTTP's method and status semantics are not decoration - the entire ecosystem depends on them.
Caches cache `GET`. Proxies and load balancers retry idempotent methods. Client libraries retry
5xx and not 4xx. Monitoring alerts on 5xx rates. A `POST /getUser` returning 200 with
`{"error": "not found"}` defeats every one of those, silently.

## Methods

| Method | Semantics | Safe | Idempotent |
| --- | --- | --- | --- |
| GET | Retrieve; no side effects | Yes | Yes |
| HEAD | Headers only | Yes | Yes |
| POST | Create or process | No | No |
| PUT | Replace entire resource | No | Yes |
| PATCH | Partial update | No | Not inherently |
| DELETE | Remove | No | Yes |

**A GET must never change state.** Prefetchers, crawlers and browsers will call it, sometimes
repeatedly and without user action.

## Status codes

- **200** OK, **201** Created (with `Location`), **204** No Content
- **400** malformed, **401** not authenticated, **403** authenticated but forbidden,
  **404** not found, **409** conflict, **422** semantically invalid, **429** rate limited
- **500** unexpected server fault, **502/503/504** upstream problems

Use 401 versus 403 correctly - it is the difference between "log in" and "you cannot do this".
For resources the caller must not know exist, return 404 rather than 403.

## Resource design

- Plural nouns, hierarchical: `/users/{id}/orders/{id}`
- Filtering, sorting and pagination as query parameters, not as separate endpoints
- **Pagination from day one**, cursor-based where possible - adding it later is breaking
- **Actions that are not CRUD** are still resources: `POST /orders/{id}/cancellation` rather
  than `POST /cancelOrder`

## Headers worth using properly

- `Content-Type` and `Accept` for negotiation
- `ETag` + `If-None-Match` for conditional GET; `If-Match` for optimistic concurrency on writes -
  this is the clean solution to lost updates
- `Cache-Control` explicitly, on every response, rather than leaving it to defaults
- `Retry-After` with 429 and 503
- `Location` on 201
- An idempotency key header on unsafe operations

## Errors

One consistent shape with a stable machine-readable code, a human message, the field at fault,
and a correlation ID. RFC 9457 (problem details) is a reasonable off-the-shelf format and saves
the argument.

## Failure modes

- **200 with an error body** - breaks retries, monitoring and generic clients.
- **GET with side effects.**
- **Unbounded list endpoints**, discovered when an account grows large.
- **Inconsistent error shapes** across one API.
- **Leaking internals** - stack traces, SQL, hostnames - to external callers.
- **Ignoring caching headers**, then adding a cache layer to solve a problem HTTP already solved.
- **Verbs in paths** as a substitute for thinking about resources.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/API Design|API Design]]
- [[Coding Knowledge/05 - Web & Application Engineering/Caching|Caching]]
- [[Coding Knowledge/08 - Code Quality & Review/API Review|API Review]]

## Sources

- RFC 9110 HTTP Semantics - <https://www.rfc-editor.org/rfc/rfc9110>; RFC 9111 HTTP Caching - <https://www.rfc-editor.org/rfc/rfc9111>; RFC 9457 Problem Details - <https://www.rfc-editor.org/rfc/rfc9457>.
