---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Database Problems

Slow queries, locking, connection exhaustion and wrong data - diagnosed in that order of frequency.

## Slow queries

1. **Find them.** Slow query log, `pg_stat_statements`, the APM. Sort by **total time**, not by
   worst single execution - a 20 ms query run 50,000 times costs more than one 4-second query
   and is much easier to miss.
2. **`EXPLAIN ANALYZE`** the offender. Read for: sequential scans on large tables, estimated
   rows far from actual, nested loops over large inputs, sorts spilling to disk.
3. **Estimate versus actual is the key signal.** A large divergence means statistics are stale
   and the planner is choosing badly because it is misinformed. `ANALYZE` first, before
   redesigning anything.
4. **Check the index.** Missing, or present but unusable: a function wrapping the column, a
   leading wildcard `LIKE '%x'`, an implicit type cast, or the wrong leading column in a
   composite index.
5. **Check the row count returned.** A fast query returning 200,000 rows to a client that needs
   20 is not a database problem.

## N+1

The most common performance defect in ORM-based applications: one query for the list, then one
per item. Invisible with 10 rows, fatal with 10,000.

Detect by counting queries per request - not by reading code. Fix with eager loading (`join`,
`select_related`, `include`), or a single query with an `IN` clause.

## Locking and blocking

- **Find the blocker**, not the blocked. `pg_locks` joined to `pg_stat_activity`, `SHOW ENGINE
  INNODB STATUS`, or the equivalent. The query that is waiting is a symptom.
- **Long transactions are the usual cause**, especially one held across an external network call.
  Keep transactions short and never wrap an HTTP request in one.
- **Deadlocks are normal** in concurrent systems. Acquire locks in a consistent order and retry
  on deadlock; trying to eliminate them entirely is usually the wrong goal.
- **DDL takes strong locks.** An `ALTER TABLE` during peak traffic can block everything; know
  which operations require a rewrite in your engine and version.

## Connection exhaustion

Symptom: "too many connections", or requests queuing while the database looks idle.

- Pool size is not "more is better". Past a point, more connections reduce throughput.
- **Leaked connections** - a code path that does not release on error. Look for the missing
  `finally`/context manager.
- Many application instances x a large pool each = far more connections than intended. Use an
  external pooler.
- Set a **statement timeout**, so one runaway query cannot hold a connection indefinitely.

## Wrong data

- **`NULL` semantics.** `NOT IN` with a `NULL` in the set returns nothing, silently. `= NULL` is
  never true. Aggregates skip `NULL`.
- **Isolation level.** Read-committed permits non-repeatable and phantom reads; anomalies that
  "only happen under load" are usually this.
- **Lost updates** from read-modify-write in application code.
- **Replication lag** - reading your own write from a replica returns stale data.
- **Timezone handling** - a naive timestamp stored from two different server timezones.
- **Implicit type coercion** in comparisons producing surprising matches.

## Before touching production data

- Run the `WHERE` clause as a `SELECT` first, and check the row count.
- Wrap in a transaction so it can be rolled back.
- Take a backup or a snapshot for anything destructive.
- Batch large updates and throttle them; a single statement touching millions of rows will lock
  and will generate enormous replication lag.

## Investigation order

Slow queries -> missing indexes -> N+1 -> long transactions and locks -> connection pool ->
isolation semantics -> hardware. Working in that order finds the cause quickly the large majority
of the time; starting at hardware almost never does.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/SQL|SQL]]
- [[Coding Knowledge/05 - Web & Application Engineering/Databases|Databases]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]]

## Sources

- PostgreSQL documentation on `EXPLAIN`, `pg_stat_statements` and locking - <https://www.postgresql.org/docs/>; Markus Winand, *Use The Index, Luke!* - <https://use-the-index-luke.com/>.
