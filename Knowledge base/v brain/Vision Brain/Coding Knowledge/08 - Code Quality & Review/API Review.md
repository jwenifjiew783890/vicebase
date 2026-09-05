---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# API Review

Reviewing an interface other people will depend on, where the mistakes cannot be taken back.

## The governing question

**What will we be unable to change after this ships?** Every exposed field, status code, default
and accidental behaviour becomes a contract as soon as someone depends on it. Review with that
permanence in mind, because a design flaw here outlives every implementation detail.

## Checklist

**Shape**
- Does the response mirror the database schema? If so, every schema change becomes a breaking
  API change.
- Are internal identifiers or internal structure exposed?
- Is the top level an object rather than a bare array, leaving room to add fields?
- Naming consistent with the rest of the API - one case convention throughout?
- Are absent and null distinguished deliberately?

**Semantics**
- Correct HTTP methods; GET has no side effects.
- Correct status codes; no 200 with an error body.
- Idempotent where the method implies it.
- Is there an idempotency mechanism on unsafe operations, so a client that times out can retry?

**Bounds**
- Pagination on every list endpoint - present from the start, since adding it is breaking?
- A maximum page size that the server enforces?
- Response size bounded for every endpoint?
- Request size and rate limits?

**Errors**
- One consistent shape, with a **stable machine-readable code** consumers can switch on.
- The field at fault identified where applicable.
- A correlation ID.
- Nothing internal leaked.

**Evolution**
- Is this change additive? If not, it is breaking - and is that acknowledged?
- Is there a version strategy, and does this fit it?
- Is anything being deprecated, with a timeline and usage measurement?

**Documentation**
- Is the schema generated from the code rather than maintained beside it? A hand-maintained spec
  drifts, and a drifted spec is worse than none.

## Breaking changes, named explicitly

Removing or renaming a field. Changing a type. Changing the meaning of a value. Adding a
required request field. Tightening validation. Changing a default. Changing pagination
semantics. Changing an error code. Changing ordering that clients may rely on.

**Tightening validation is the one that surprises people** - rejecting input you previously
accepted breaks existing callers even though the new behaviour is more correct.

## Questions worth asking every time

- How does a client discover it did something wrong, specifically enough to fix it?
- What happens when this returns 10,000 items?
- How does a client retry safely after a timeout?
- What does a caller do when this is down?
- If we need to change this in six months, what is the migration path?

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/API Design|API Design]]
- [[Coding Knowledge/05 - Web & Application Engineering/REST|REST]]
- [[Coding Knowledge/08 - Code Quality & Review/Architecture Review|Architecture Review]]

## Sources

- RFC 9110 - <https://www.rfc-editor.org/rfc/rfc9110>; Google API Improvement Proposals - <https://google.aip.dev/>. Synthesised.
