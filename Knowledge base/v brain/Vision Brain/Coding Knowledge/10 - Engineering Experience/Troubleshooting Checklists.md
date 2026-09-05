---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Troubleshooting Checklists

What to check first, by symptom. Ordered by (probability x cheapness to check), not by probability alone.

## "It does not start"

1. Read the actual error - all of it, and the log the process writes rather than the console.
2. Is the port already in use? (`ss -tlnp`, `Get-NetTCPConnection`)
3. Is a required config value or environment variable missing?
4. Are file permissions right for the account it runs as?
5. Is a dependency (database, broker) reachable *from where it runs*?
6. Is the working directory what it expects?
7. Run the binary manually, as the same user, from the same directory - this reproduces the
   environment and usually reveals it immediately.

## "It worked yesterday"

1. `git log` since the last known-good; then `git bisect`.
2. Did a dependency update? Diff the lock file.
3. Did config or a secret change? Was a credential rotated?
4. **Did something expire?** Certificate, token, licence, trial. Very common and invisible in
   any diff.
5. Did the data change - new shape, new volume, a first-time edge case?
6. Did the environment change - base image, kernel, resource limits?
7. Is it actually a date boundary? Month-end, DST, leap day.

## "It works on my machine"

1. Versions: language runtime, dependencies, OS, database.
2. Environment variables present locally and absent there.
3. **Case sensitivity** - Linux is case-sensitive; Windows and macOS often are not.
4. Uncommitted or ignored files.
5. Local cached state - build cache, `node_modules`, `__pycache__`.
6. Data differences - your local database is not production.
7. Resource limits - less memory, fewer cores.
8. Network - can that host reach what yours can?

## "It is slow"

1. Slow for whom, doing what, compared with what? Get a number.
2. Profile before theorising.
3. **Count the queries per request.** N+1 is the most common answer.
4. Check `EXPLAIN` on the slowest query; check for a missing index.
5. Is it I/O-bound or CPU-bound? A CPU profile of an I/O-bound process shows nothing.
6. Is there a network call on the request path that should be queued?
7. Did the data volume grow past where the algorithm was acceptable?

## "It fails sometimes"

1. What is different between the successes and the failures? Input, time, host, user, order.
2. Concurrency - shared state, check-then-act, ordering assumptions.
3. Timeouts, and retries hiding partial failures.
4. One bad instance behind a load balancer - test each directly.
5. A cache serving stale or partial data.
6. Rate limiting engaging only at peak.
7. Clock skew between hosts.

## "It cannot connect"

1. Is anything listening, and on which interface? `127.0.0.1` vs `0.0.0.0`.
2. **Refused or timeout?** Refused = reached, nothing there. Timeout = dropped, likely firewall.
3. Does the name resolve, to the address you expect?
4. Firewall, security group, corporate proxy.
5. TLS: expiry, hostname match, chain completeness, protocol version.
6. Try `127.0.0.1` explicitly - `localhost` may resolve to IPv6 first.

## "Memory keeps growing"

1. Is it growing across *repeated identical cycles*, or is this one high reading?
2. Use **private bytes**, not RSS, to attribute it.
3. Is a job actually running? Check the CPU delta over a fixed interval.
4. Snapshot, N cycles, snapshot, **diff** - never read absolute heap contents.
5. Look at retainers, not at size.
6. Check the container/cgroup limit before blaming the process.

## "The data is wrong"

1. Is it wrong at the source, or wrong in the display?
2. Trace one record end to end and find the first point where it diverges.
3. Timezone and encoding, at every boundary.
4. `NULL` semantics - `NOT IN` with a NULL, aggregates skipping NULL.
5. Concurrency - a lost update from read-modify-write.
6. A cache serving something stale.
7. Replication lag - reading your own write from a replica.

---

## See also

- [[Coding Knowledge/02 - Debugging Method|Debugging Method]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/00 - Debugging & Problem Solving|Debugging & Problem Solving]]
- [[Coding Knowledge/10 - Engineering Experience/Practitioner Heuristics|Practitioner Heuristics]]

## Sources

- Practitioner judgement, assembled from the diagnostic sequences in section 07.
