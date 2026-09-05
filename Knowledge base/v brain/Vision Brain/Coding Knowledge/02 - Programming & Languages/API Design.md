---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# API Design

Designing an interface other people depend on - where the cost of a mistake is that you can never take it back.

## The governing constraint

**Anything you expose, you must support.** Every field, every status code, every accidental
behaviour becomes a contract the moment someone depends on it. So expose the minimum that does
the job; adding later is easy, removing is not.

## Naming and shape

- **Resources are nouns, plural**: `/users`, `/users/{id}/orders`. Verbs live in the method.
- **Consistency beats correctness of taste.** Pick `snake_case` or `camelCase` and never mix.
- **Never expose internal identifiers or internal structure.** A response that mirrors your
  table schema means every schema change is a breaking API change.
- **Return objects, not bare arrays**, at the top level - `{"items": [...], "next": "..."}`
  leaves room to add fields without breaking parsers.
- **Absent and null are different.** Decide which you mean and be consistent; this distinction
  matters enormously for partial updates.

## HTTP semantics that carry meaning

| Method | Semantics | Idempotent |
| --- | --- | --- |
| GET | Read, no side effects, cacheable | Yes |
| POST | Create or process | No |
| PUT | Replace the whole resource | Yes |
| PATCH | Partial update | Not inherently |
| DELETE | Remove | Yes (repeat returns 404 or 204) |

Status codes: 400 malformed, 401 not authenticated, 403 authenticated but not permitted, 404
not found (or hidden for authz reasons), 409 conflict, 422 semantically invalid, 429 rate
limited (with `Retry-After`), 5xx *your* fault. Returning 200 with `{"error": ...}` breaks
every generic client, retry policy and monitor.

## Errors

An error response should carry: a **stable machine-readable code**, a human message, the
**field** at fault where applicable, and a **correlation ID**. Consumers switch on the code, so
the code must never change meaning; the message may.

Never leak stack traces, SQL, internal hostnames or library versions to an external consumer.

## Versioning and compatibility

**Additive changes are safe**; everything else breaks someone.

Breaking: removing or renaming a field, changing a type, changing the meaning of a value, adding
a required request field, tightening validation, changing a default, changing pagination
semantics, changing an error code.

Version in the URL (`/v1/`) for clarity, or by header for elegance - but pick one. Support the
old version for a stated window, publish a deprecation timeline, and instrument usage so you
know who is still on it. **Deprecation without measurement is a guess.**

## Operational design

- **Pagination on every list endpoint from day one.** Retrofitting it is a breaking change.
  Prefer cursor-based over offset.
- **Idempotency keys on unsafe operations**, so a client that times out can retry safely.
- **Rate limits stated in headers**, with `Retry-After` on 429.
- **Bound every response.** No endpoint should be able to return unbounded data.
- **Timeouts and payload size limits** declared and enforced.
- **A machine-readable schema** (OpenAPI, JSON Schema) generated from the code, not maintained
  beside it, or it will drift.

## Failure modes

- **Leaking the database schema** as the API shape.
- **Overloading one endpoint** with a `type` parameter that changes the response shape.
- **Chatty design** forcing N calls to render one screen.
- **Unbounded list endpoints** discovered when a customer's account grows.
- **Inconsistent errors** - three formats across one API.
- **Breaking changes shipped as patches** because nobody defined what breaking means.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/REST|REST]]
- [[Coding Knowledge/08 - Code Quality & Review/API Review|API Review]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- RFC 9110 (HTTP semantics) - <https://www.rfc-editor.org/rfc/rfc9110>; RFC 9457 (problem details for HTTP APIs) - <https://www.rfc-editor.org/rfc/rfc9457>; Google API Improvement Proposals - <https://google.aip.dev/>. Facts restated, text not copied.
