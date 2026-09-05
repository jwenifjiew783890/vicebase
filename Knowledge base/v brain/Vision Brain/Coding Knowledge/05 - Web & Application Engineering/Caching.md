---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Caching

The cheapest performance win and the source of the subtlest bugs. Add it deliberately, never by reflex.

## Before adding a cache

Ask whether the work can simply not be done: a missing index, an N+1 query, an unnecessary
call, a response returning fields nobody uses. **A cache in front of a bad query hides the
problem and doubles the failure modes.** Fix the underlying work first.

Then be explicit about: what is cached, what invalidates it, how stale it may be, and what
happens when the cache is cold or unavailable.

## Layers

| Layer | Scope | Invalidation |
| --- | --- | --- |
| **Browser** | One user | `Cache-Control`, ETag, content-hashed filenames |
| **CDN** | All users, static and cacheable dynamic | TTL, purge API |
| **Reverse proxy** | All users | TTL, purge |
| **Application memory** | One process | Time or event; **not shared across instances** |
| **Shared cache (Redis)** | All instances | Explicit, and the usual right choice |
| **Database** | Query and buffer caches | Automatic |

**In-process caches are per-instance.** With three instances you have three views of the truth
and three different invalidation moments - a real source of "it's fixed for some users".

## Invalidation strategies

- **TTL** - simplest, and correct far more often than people expect. Accept bounded staleness
  and move on.
- **Write-through** - update the cache when writing. Consistent, more coupling.
- **Write-invalidate** - delete the key on write, repopulate on next read. Usually the best
  default.
- **Event-driven** - subscribe to changes. Powerful, and the events become a dependency.
- **Versioned keys** - include a version or content hash in the key, so old entries become
  unreachable rather than needing deletion. Very robust.

## The classic failures

**Stampede / dogpile.** A popular key expires; every request misses simultaneously and hits the
origin at once. Fix with jittered TTLs, single-flight (one request repopulates, others wait), or
proactive refresh before expiry.

**Cold start.** After a restart or a flush, the origin receives full traffic with no cache. Know
whether the origin can survive that - if not, the cache is not an optimisation, it is a load
bearing dependency that must be treated as such.

**Cache poisoning.** An unkeyed input (a header, a query parameter) affects the response but not
the cache key, so one user's response is served to another. **Always include every input that
varies the response in the key** - especially the user or tenant identity.

**Caching per-user data in a shared cache without the user in the key.** The most damaging
version of the above, and it looks like a working cache until it does not.

**Negative results not cached**, so a missing item hammers the origin on every request. Cache
the miss, with a short TTL.

**Unbounded cache.** No eviction policy, growing until the process runs out of memory.

## Rules

- Cache keys include **every** input that varies the output.
- Set an explicit TTL on everything. No entry lives forever by accident.
- Bound the size, with an eviction policy.
- The system must **work correctly, if slower, with the cache empty or down**.
- Measure hit rate. A cache with a 5% hit rate is complexity for nothing.
- Never cache authorization decisions longer than the shortest revocation requirement.

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Web Performance|Web Performance]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]
- [[Coding Knowledge/05 - Web & Application Engineering/REST|REST]]

## Sources

- RFC 9111 HTTP Caching - <https://www.rfc-editor.org/rfc/rfc9111>; AWS Builders' Library on caching challenges - <https://aws.amazon.com/builders-library/caching-challenges-and-strategies/>.
