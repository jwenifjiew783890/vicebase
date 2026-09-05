---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# SQL

Thinking in sets, making the planner do the right thing, and the isolation semantics that produce "impossible" bugs.

## Set thinking

SQL is declarative: describe the result, let the planner choose how. The most common performance
mistake is procedural thinking - looping in the application and querying per item (the **N+1
pattern**) instead of expressing the whole thing as one join or one `IN`. A single query
returning 1,000 rows beats 1,000 queries returning one, by orders of magnitude.

## Indexes

- An index helps `WHERE`, `JOIN`, `ORDER BY` and `GROUP BY` on its **leading columns**. A
  composite index on `(a, b)` serves queries filtering on `a`, or on `a` and `b` - not on `b`
  alone.
- **Wrapping a column in a function defeats its index**: `WHERE lower(email) = ?` will not use
  an index on `email`. Use an expression index, or store the normalised value.
- **Leading wildcards defeat indexes**: `LIKE '%foo'` scans.
- **Implicit type casts defeat indexes**: comparing a `varchar` column to an integer.
- A **covering index** (including the selected columns) avoids touching the table at all.
- Indexes cost write throughput and disk. Every index is paid for on every insert and update.
- Low-selectivity columns (a boolean) rarely benefit from their own index.

## Reading a plan

`EXPLAIN ANALYZE` (Postgres), `EXPLAIN ANALYZE FORMAT=JSON` (MySQL), `EXPLAIN QUERY PLAN`
(SQLite). Look for, in order:

1. **Sequential scan on a large table** where a filter should have used an index.
2. **Estimated rows wildly different from actual** - statistics are stale; the planner is
   choosing badly because it is misinformed. Run `ANALYZE`.
3. **Nested loop over a large outer input** - usually a missing index on the inner side.
4. **Sort or hash spilling to disk** - work memory too small, or the query is fetching far more
   than it needs.

## Correctness traps

- **`NULL` is not equal to anything, including `NULL`.** Use `IS NULL`. `NOT IN` with a `NULL`
  in the list returns no rows at all - a silent, very expensive bug. Prefer `NOT EXISTS`.
- **Aggregates ignore `NULL`**: `COUNT(col)` differs from `COUNT(*)`.
- **`LIMIT` without `ORDER BY`** returns an arbitrary subset, which may be stable in testing and
  not in production.
- **Pagination by `OFFSET`** degrades linearly and can skip or repeat rows when data changes.
  Use keyset pagination (`WHERE id > last_seen ORDER BY id LIMIT n`).
- **Read-modify-write races.** `SELECT` then `UPDATE` from application code loses updates under
  concurrency. Use a single atomic `UPDATE ... WHERE`, `SELECT FOR UPDATE`, or optimistic
  concurrency with a version column.
- **Floating point for money.** Use `numeric`/`decimal`.

## Isolation

Default isolation is usually `READ COMMITTED`, which permits non-repeatable reads and phantom
reads. Bugs that "only happen under load" and involve counters, balances or uniqueness checks
are usually this.

- Understand what your engine's default actually is - it differs between Postgres and MySQL.
- `SERIALIZABLE` is correct but can abort transactions; the application must retry.
- **Keep transactions short.** A transaction held open across a network call holds locks for the
  duration of that call, and is a leading cause of lock pile-ups.
- **Deadlocks are normal** in concurrent systems; acquire locks in a consistent order and retry
  on deadlock rather than trying to eliminate them.

## Safety

- **Parameterised queries, always.** String interpolation into SQL is SQL injection; there is no
  safe escaping you should be writing yourself.
- **`UPDATE`/`DELETE` without `WHERE`.** Write the `WHERE` first, run it as a `SELECT`, then
  convert. Use a transaction so it can be rolled back.
- Migrations must be backwards compatible for one release - see
  [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]].

---

## See also

- [[Coding Knowledge/05 - Web & Application Engineering/Databases|Databases]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Database Problems|Database Problems]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]

## Sources

- PostgreSQL documentation - <https://www.postgresql.org/docs/> (PostgreSQL licence); MySQL and SQLite documentation; Markus Winand, *Use The Index, Luke!* - <https://use-the-index-luke.com/>. Facts restated, text not copied.
