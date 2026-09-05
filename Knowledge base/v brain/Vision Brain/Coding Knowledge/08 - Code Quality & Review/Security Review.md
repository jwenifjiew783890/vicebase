---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# Security Review

Reviewing a change for the vulnerability classes that actually cause breaches.

## Where to look first

Security defects concentrate at boundaries. In a diff, go straight to:

1. **Anywhere untrusted input enters** - request handlers, file uploads, message consumers,
   webhook receivers, and anything parsing a document or a URL.
2. **Anywhere a structured string is built** - SQL, shell, HTML, paths, URLs, templates.
3. **Anywhere an authorization decision is made or should be.**
4. **Anywhere a secret is handled.**
5. **New dependencies.**

## The checklist

**Input**
- Validated at the boundary, into a typed structure, with an allowlist rather than a denylist?
- Length and size bounds on everything, including nested structures?
- File uploads: type verified by content not extension, size capped, stored outside the web root,
  filename not used as a path?

**Injection**
- SQL parameterised - no string interpolation anywhere, including in "internal" queries?
- Subprocess calls use an argument array, never `shell=True` with interpolation?
- No `eval`, `exec`, or dynamic import of anything derived from input?
- Deserialisation is JSON with a schema - never `pickle`, `yaml.load`, or language-native
  serialisation of untrusted data?

**Authorization** (the most common serious finding)
- Does every handler that takes an object ID check that the actor may access *that object*?
- Is the check at the data-access layer, so it cannot be forgotten on a new path?
- Are background jobs, exports and admin tools also covered, or do they bypass the middleware?
- Mass assignment - can a request body set `role`, `account_id` or `is_admin`?

**Output**
- Escaped for its context - HTML, attribute, JavaScript, URL - by a template engine, not by hand?
- No internal detail in errors returned to users: stack traces, SQL, hostnames, versions?

**Secrets**
- Nothing hard-coded, nothing logged, nothing in a URL, nothing in a client bundle?
- Read from a proper store, and rotatable?

**Network**
- Server-side fetches of user-supplied URLs: destination allowlisted, private and link-local
  addresses rejected, redirects re-validated?
- TLS verification on - and if a private CA is involved, is it *trusted* rather than verification
  disabled?

**Resource**
- Bounds on request size, result count, recursion depth, and any loop driven by input?
- Rate limiting on authentication and on expensive endpoints?

## Reviewing for the "impossible"

The most productive question is: **what if this input is hostile?** Not malformed - hostile.
Someone who knows the code, is patient, and is trying to get something specific.

The second most productive: **what does this trust that it should not?** A header, a cookie, a
client-supplied ID, a filename, a redirect target, a tool description, a retrieved document.

## When to escalate

Anything touching authentication, cryptography, payment, personal data at scale, or a new
external interface deserves a second reviewer. **Do not implement cryptography** - use a
maintained library, and if a change is writing its own, that alone is the finding.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]
- [[Coding Knowledge/05 - Web & Application Engineering/Authorization|Authorization]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]

## Sources

- OWASP Top Ten - <https://owasp.org/www-project-top-ten/>; OWASP Code Review Guide and Cheat Sheet Series - <https://cheatsheetseries.owasp.org/> (CC BY-SA 4.0, verified 2026-09-03; synthesised, not copied).
