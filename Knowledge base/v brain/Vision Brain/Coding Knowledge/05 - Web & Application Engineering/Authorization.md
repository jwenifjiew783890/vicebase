---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Authorization

Deciding what an authenticated party may do. Unlike authentication, this cannot be outsourced - it is your business rules.

## The rule that prevents most breaches

**Enforce on the server, at the data access boundary, on every request.** Not in the UI, not
once at the start of a session, not in a middleware that only covers some routes.

Hiding a button is a usability feature. The API behind it is the security boundary.

## Broken object-level authorization

The most common serious web vulnerability, and the simplest: an endpoint checks that you are
logged in, but not that the object belongs to you.

```
GET /api/invoices/1234     <- authenticated, returns someone else's invoice
```

The fix is structural, not per-endpoint vigilance: **scope every query by the actor**.

```sql
SELECT * FROM invoices WHERE id = ? AND account_id = ?
```

Do this in the repository layer so that it cannot be forgotten. Any codebase where the correct
behaviour depends on each developer remembering an `if` will eventually have one that is
missing.

## Models

| Model | Fits |
| --- | --- |
| **Role-based (RBAC)** | Small, stable sets of permissions. Simple and usually enough |
| **Attribute-based (ABAC)** | Decisions depending on data - owner, department, time, status |
| **Relationship-based (ReBAC)** | Sharing graphs: "can edit because a parent folder was shared" |
| **Ownership** | The simplest and most common: does this row belong to this actor |

Start with roles plus ownership. Add attributes when a real rule needs them. Do not adopt a
policy engine before the rules justify it.

## Design rules

- **Deny by default.** A new endpoint with no explicit rule must be inaccessible, not open.
- **Centralise the decision**, apply it everywhere. One `can(user, action, resource)` function
  that every path calls beats scattered checks.
- **Check at the point of data access**, not only at the route. Background jobs, exports, admin
  tools and GraphQL resolvers are all paths that bypass route middleware.
- **Least privilege**, including for service accounts and internal tools. An internal admin panel
  with unrestricted database access is a breach amplifier.
- **404 versus 403.** If the existence of a resource is itself sensitive, return 404.
- **Re-check on every request.** Permissions change; a long session must not carry stale
  authority.

## Multi-tenancy

Tenant isolation is the highest-consequence case. Every query must be scoped by tenant, enforced
somewhere it cannot be omitted - row-level security in the database, or a repository layer that
requires a tenant context to construct a query. A single missing `WHERE tenant_id = ?` is a
cross-customer data leak.

## Auditing

Log authorization **denials** as well as sensitive allowed actions: who, what, which resource,
when, allowed or denied. Denials are the signal that something is misconfigured or that someone
is probing.

## Failure modes

- **Object-level checks missing** - the ID in the URL is trusted.
- **Client-side-only enforcement.**
- **Mass assignment** - accepting a `role` or `account_id` field from the request body and
  writing it.
- **Permissions checked at login and cached** for the session.
- **Admin endpoints protected by obscurity.**
- **Background jobs bypassing checks** because they run "as the system".
- **A missing tenant filter** in one query out of hundreds.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Authentication|Authentication]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]
- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]

## Sources

- OWASP Top Ten, A01 Broken Access Control - <https://owasp.org/www-project-top-ten/>; OWASP Authorization Cheat Sheet - <https://cheatsheetseries.owasp.org/> (CC BY-SA 4.0, synthesised).
