---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Web Security

The attack classes that account for most real breaches, and the structural defences against each.

## The principle underneath all of it

**Never build a structured thing by concatenating strings.** SQL, HTML, shell commands, LDAP
queries, XML, file paths, and URLs. Every injection vulnerability is a variation of this, and
every fix is the same: use the mechanism that keeps data and structure separate - parameters,
argument arrays, real serialisers, template engines with auto-escaping.

## The classes that matter

**Broken access control.** The most common serious finding: an endpoint that authenticates but
does not check ownership. Structural fix in
[[Coding Knowledge/05 - Web & Application Engineering/Authorization|Authorization]].

**Injection (SQL, command, template).** Parameterised queries; argument arrays instead of
`shell=True`; never `eval`. Escaping by hand is not a solution.

**Cross-site scripting (XSS).** Attacker JavaScript running in your page's origin, which means
full access to the session. Defences: context-aware output escaping (a template engine, not
manual replacement), avoid `innerHTML` and `dangerouslySetInnerHTML`, sanitise any HTML you must
accept (DOMPurify), and a **Content-Security-Policy** as the backstop that makes an escaping
mistake non-fatal.

**Cross-site request forgery (CSRF).** Another site causing an authenticated request from the
user's browser. Defences: `SameSite=Lax` or `Strict` cookies, plus anti-CSRF tokens on
state-changing requests. Not relevant to `Authorization: Bearer` APIs, which browsers do not
attach automatically.

**Server-side request forgery (SSRF).** Your server fetching a URL supplied by a user, used to
reach internal services and cloud metadata endpoints. Defences: allowlist destinations, resolve
DNS and validate the resulting IP is not private or link-local, disable redirects or re-validate
after each, and prefer a dedicated egress proxy.

**Insecure deserialisation.** Never deserialise untrusted data with a format that can construct
arbitrary objects - Python `pickle`, Java serialisation, PHP `unserialize`, YAML `load` without
`safe_load`. Use JSON with a schema.

**Path traversal.** `../` in a user-supplied filename. Reject rather than resolve, and confine
to a base directory verified after resolution.

**Vulnerable dependencies.** Frequently the actual entry point. Automated scanning, a
maintained lock file, and a routine update cadence.

**Secrets exposure.** In source control, in logs, in error pages, in client-side bundles, in
image layers. Assume any secret ever committed is compromised, and rotate it.

## Headers worth setting

- `Content-Security-Policy` - the single most effective XSS mitigation
- `Strict-Transport-Security` - forces HTTPS
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options` / CSP `frame-ancestors` - clickjacking
- Explicit, narrow CORS. `Access-Control-Allow-Origin: *` with credentials is a common and
  serious misconfiguration.

## Operational rules

- **Validate input at the boundary, encode at output.** They are different operations and both
  are required.
- **Fail closed.** An error in a security check must deny, never allow.
- **Least privilege** for database users, service accounts and API keys.
- **Log security events** - authentication failures, authorization denials, validation
  rejections - without logging the secrets themselves.
- **Keep dependencies current.** Most exploited vulnerabilities have had a patch available.
- **Rate-limit** authentication, expensive endpoints and anything that sends mail or messages.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Authentication|Authentication]]
- [[Coding Knowledge/05 - Web & Application Engineering/Authorization|Authorization]]
- [[Coding Knowledge/08 - Code Quality & Review/Security Review|Security Review]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]

## Sources

- OWASP Top Ten - <https://owasp.org/www-project-top-ten/>; OWASP Cheat Sheet Series - <https://cheatsheetseries.owasp.org/> (CC BY-SA 4.0, verified 2026-09-03; synthesised in our own words, not copied); MDN on CSP and CORS - <https://developer.mozilla.org/> (CC BY-SA 2.5).
