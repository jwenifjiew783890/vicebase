---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Backups

The only property that matters is whether the restore works. Everything else is filing.

## The rule

**An untested backup is a hypothesis.** Until a restore has been performed, from the actual
backup, into a usable system, you do not have a backup - you have files you hope are useful.

Test the restore on a schedule, and **measure how long it takes**. That duration is your real
recovery time, and it is almost always longer than anyone assumed.

## The 3-2-1 baseline

Three copies, on two different media, one off-site. The off-site copy is what survives fire,
theft, ransomware and a mistaken `rm -rf` propagated by sync.

Extend it for ransomware: at least one copy **immutable or offline**. A backup that the
compromised machine can delete or encrypt is not a backup against the most common modern
disaster.

## What must be backed up

Not just the database:

- Database, with a **consistent** snapshot (a file copy of a running database is often corrupt -
  use the engine's dump or snapshot mechanism)
- Uploaded files and generated artefacts
- Configuration and secrets (encrypted, and stored separately)
- Infrastructure definitions
- Anything hand-configured that is not in version control - and finding these is itself the
  exercise

## Define the targets explicitly

- **RPO** (recovery point objective) - how much data may be lost. Determines backup frequency.
- **RTO** (recovery time objective) - how long recovery may take. Determines the mechanism -
  a nightly dump cannot meet a 15-minute RTO.

Writing these down converts an unbounded worry into a design constraint, and usually reveals
that the current setup does not meet what everyone assumed.

## Practical requirements

- **Automated.** A manual backup will be skipped.
- **Monitored.** A silently failing backup job is the standard disaster story. Alert on the
  *absence* of a recent successful backup, not only on failure.
- **Encrypted at rest**, with the key stored somewhere the backup is not.
- **Retention that covers slow discovery.** Corruption found three weeks later needs a copy from
  four weeks ago. Daily-for-a-week is not enough on its own.
- **Verified integrity** - checksums, and a periodic test restore.
- **Documented restore procedure**, written to be followed by someone tired and stressed.

## Point-in-time recovery

For databases, continuous archiving (WAL shipping, binlogs) enables recovery to a specific
moment, which is what you need after a bad migration or an accidental `DELETE`. A nightly dump
alone means losing a day.

## Before any destructive operation

Take a snapshot first. This applies to migrations, bulk updates, cleanup scripts and
"just tidying up". The cost is minutes; the alternative is unbounded.

For anything that deletes: **look at what will be deleted before deleting it.** Run the query as
a `SELECT`, run the script with `--dry-run`, list the files before removing them.

## Failure modes

- **Never restored.** The dominant failure.
- **Backing up a corrupt state** for weeks, and only finding out during recovery.
- **Backups on the same host or the same account** as the data.
- **Secrets not backed up**, so the data is recoverable and unusable.
- **No monitoring**, so a job that stopped months ago is discovered during an incident.
- **Retention too short** for slow-discovery corruption.
- **Restore procedure that only one person knows.**

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Secrets & Configuration|Secrets & Configuration]]
- [[Coding Knowledge/05 - Web & Application Engineering/Databases|Databases]]
- [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons|Production Incident Lessons]]

## Sources

- Practitioner synthesis. PostgreSQL continuous archiving documentation - <https://www.postgresql.org/docs/current/continuous-archiving.html>. The 3-2-1 rule is long-standing industry practice.
