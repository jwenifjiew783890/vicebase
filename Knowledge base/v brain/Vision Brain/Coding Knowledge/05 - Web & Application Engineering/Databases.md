---
type: note
domain: Coding Knowledge
section: 05 - Web & Application Engineering
created: 2026-09-03
---

# Databases

Choosing one, modelling in it, changing it safely, and operating it.

## Choosing

**Default to a relational database.** PostgreSQL handles relational data, JSON documents,
full-text search, geospatial data and queues competently. Most systems that adopted something
else would have been better served by it, and the ones that genuinely needed otherwise knew
exactly why.

Reach for something else with a specific reason:

| Need | Consider |
| --- | --- |
| Key-value cache, ephemeral | Redis / Valkey |
| Document store with flexible schema at scale | MongoDB, or Postgres JSONB first |
| Time series at high write rate | TimescaleDB, ClickHouse |
| Full-text search at scale | Elasticsearch/OpenSearch, or Postgres FTS first |
| Vector similarity | pgvector first, dedicated store when it stops scaling |
| Embedded, single-process | SQLite - genuinely excellent, and underrated |

## Modelling

- **Normalise first.** Denormalise only in response to a measured problem, and document why.
- **Constraints in the database**: `NOT NULL`, foreign keys, `UNIQUE`, `CHECK`. Application-level
  validation is bypassed by every script, migration and manual fix. The database is the last
  line and the only one that always runs.
- **Right types**: `timestamptz` not string, `numeric` not float for money, native enums or a
  lookup table, UUID or bigint for keys deliberately.
- **Store timestamps in UTC**, always.
- **Soft delete only where genuinely needed** - it complicates every query and every unique
  constraint thereafter.

## Migrations

The rule that prevents most deployment disasters: **every schema change must be backwards
compatible with the currently running code for one release.**

The safe expand/contract sequence:
1. Add the new column, nullable, with a default
2. Deploy code that writes both old and new
3. Backfill in batches, throttled
4. Deploy code that reads the new
5. Stop writing the old
6. Drop the old column, in a later release

Also: **never lock a large table during a deploy.** Adding an index concurrently, adding a
`NOT NULL` constraint, and rewriting a table all behave differently by engine and version -
check before running, in a maintenance window if unsure.

## Operating

- **Connection pooling**, sized deliberately. More connections is not more throughput; past a
  point it is less. Use an external pooler (PgBouncer) for many application instances.
- **Statement timeouts**, so one runaway query cannot hold resources indefinitely.
- **Backups that have been restored.** An untested backup is a hypothesis. Test the restore on a
  schedule, and measure how long it takes - that number is your real recovery time.
- **Monitor**: slow queries, lock waits, connection count, replication lag, table and index
  bloat, disk headroom.
- **Read replicas** shift read load, at the cost of replication lag the application must handle
  explicitly - read-after-write from a replica is a real and confusing bug class.

## Failure modes

- **No index on a foreign key** used in joins.
- **N+1 queries** from an ORM's lazy loading.
- **`SELECT *`** pulling large columns nobody uses.
- **Long transactions** holding locks across network calls.
- **Migrations that cannot roll back**, deployed with the code that requires them.
- **OFFSET pagination** on large tables.
- **Backups never restored.**
- **Application-only constraints**, bypassed by the first manual fix.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/SQL|SQL]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Database Problems|Database Problems]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Backups|Backups]]

## Sources

- PostgreSQL documentation - <https://www.postgresql.org/docs/> (PostgreSQL licence); Martin Kleppmann, *Designing Data-Intensive Applications* (2017) - cited, not reproduced.
