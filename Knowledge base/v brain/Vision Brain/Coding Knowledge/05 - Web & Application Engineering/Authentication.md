---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Authentication

Proving who someone is. The area where writing it yourself is most likely to be a mistake.

> [!danger] Use a library or a provider
> Password hashing, session management, token signing, MFA and account recovery are all solved,
> and all subtly wrong when hand-rolled. Use a maintained library (or an identity provider) and
> spend the effort on authorization instead, which cannot be outsourced.

## Passwords

- **Hash with a memory-hard function**: Argon2id preferred, bcrypt or scrypt acceptable. Never
  a plain hash - MD5, SHA-256 or anything unsalted is a breach waiting to be published.
- **Never log, never email, never store recoverable.** Reset, do not retrieve.
- **Minimum length over composition rules.** Long passphrases beat mandated symbols; enforce a
  reasonable minimum and check against known-breached password lists.
- **Rate limit and lock out** on repeated failure, keyed by account *and* by IP.
- **Constant-time comparison** for any secret comparison.

## Sessions versus tokens

| | Server sessions | JWT / stateless tokens |
| --- | --- | --- |
| Revocation | Immediate | **Hard** - the token is valid until expiry |
| State | Server-side store | None needed |
| Size | Small cookie | Larger, sent on every request |
| Best for | Web apps with a browser | Service-to-service, short-lived access |

**Revocation is the deciding factor.** If you need to log someone out immediately, disable an
account, or respond to a compromise, stateless tokens fight you. The usual compromise is short
access tokens (minutes) plus a revocable refresh token.

**Do not put anything in a JWT you would mind the holder reading** - it is signed, not encrypted.

## Cookies

For browser sessions: `HttpOnly` (blocks JavaScript access), `Secure` (HTTPS only),
`SameSite=Lax` or `Strict` (CSRF defence), a sensible `Path`, and an explicit expiry. Rotate
the session ID on login to prevent session fixation.

## OAuth / OIDC

- **OAuth 2.0 is for authorization, OpenID Connect is for authentication.** Using a raw OAuth
  access token as proof of identity is a known mistake.
- Use **authorization code flow with PKCE**. Implicit flow is deprecated.
- **Validate the `state` parameter** - it is the CSRF defence for the callback.
- Validate the ID token's signature, issuer, audience and expiry. Every one of them.
- Never accept tokens from an issuer you did not configure.

## MFA and recovery

- TOTP or WebAuthn; SMS is weak (SIM swapping) but better than nothing.
- **Account recovery is usually the weakest link.** A recovery flow that bypasses MFA makes MFA
  decorative. Design it as carefully as login itself.

## Failure modes

- **Home-grown crypto or session handling.**
- **JWTs with no revocation path** and multi-day expiry.
- **Tokens in `localStorage`**, readable by any XSS.
- **User enumeration** - "no such user" versus "wrong password" tells an attacker which accounts
  exist. Return the same message and take the same time.
- **No rate limiting**, permitting credential stuffing.
- **Secrets in source control**, or a signing key that is never rotated.
- **Auth checked in the UI only**, with the API left open.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Authorization|Authorization]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Secrets & Configuration|Secrets & Configuration]]

## Sources

- OWASP Authentication and Session Management Cheat Sheets - <https://cheatsheetseries.owasp.org/> (CC BY-SA 4.0, verified 2026-09-03; synthesised, not copied); NIST SP 800-63B Digital Identity Guidelines - <https://pages.nist.gov/800-63-3/sp800-63b.html>; RFC 6749/9700 (OAuth 2.0 and best current practice).
