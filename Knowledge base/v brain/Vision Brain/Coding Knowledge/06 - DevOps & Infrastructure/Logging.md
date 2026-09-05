---
type: note
domain: Coding Knowledge
section: 06 - DevOps & Infrastructure
created: 2026-09-03
---

# Logging

Producing logs that answer questions during an incident, rather than volume that hides them.

## The test

**Could you reconstruct what happened from the logs alone, without adding instrumentation?**
If the answer is no, the logging is inadequate no matter how much of it there is.

## Structure

Log structured events - JSON or key-value - not sentences. A prose log can only be grepped; a
structured log can be filtered, counted, grouped and joined. That difference is what makes it
possible to ask a question nobody anticipated.

Every event should carry: timestamp (UTC, ISO 8601), level, a **correlation ID**, the service
and version, and the fields relevant to the event.

## Levels that mean something

| Level | Means | Response |
| --- | --- | --- |
| **ERROR** | Something failed and someone must act | Alert |
| **WARN** | Suspicious, degraded, no action yet | Review |
| **INFO** | A significant state change or decision | Normal operation |
| **DEBUG** | Detail for development | Off in production, on when needed |

If ERROR is noisy, it stops being a signal and everything after that is theatre. Handled,
expected failures are not ERROR.

## What to log

**Log decisions and their inputs**, not only failures. "Selected provider B because A returned
429; attempt 2 of 3" is what makes an incident explicable. Error-only logging tells you it broke,
never why it took that path.

Also log: request boundaries with duration and outcome, external calls with target and status,
state transitions, permission denials, configuration at startup (values, not secrets), and
version and build identifiers.

## What never to log

- Passwords, tokens, keys, session identifiers, full authorization headers
- Full request or response bodies containing personal data
- Card numbers, national identifiers, health information
- Anything you would not want in a third-party log platform - because that is where it goes

**Redact at the logging boundary**, structurally, not by remembering at each call site. A
denylist of field names applied by the logger is the only approach that survives contact with a
growing codebase.

## Correlation

One ID generated at the entry point and propagated through every service, job, retry and log
line. Without it, distributed logs cannot be joined and every investigation starts by trying to
reconstruct which lines belong together. **This is the single highest-value logging feature.**

## Operational

- **Rotate and retain deliberately.** Unrotated logs fill disks; that is a common self-inflicted
  outage.
- **Ship them off the host.** Logs only on a dead container's local disk do not exist.
- **Sample high-volume events** rather than dropping the level. Keep all errors.
- **Cost scales with volume.** Logging every request body at INFO is expensive and rarely useful.
- **Log to stdout/stderr** in containers and let the platform handle collection.
- **Make the level runtime-configurable**, so DEBUG can be enabled during an incident without a
  deploy.

## Failure modes

- **Prose logs** that cannot be queried.
- **No correlation ID.**
- **Errors logged at every level** of the stack, so one failure produces forty lines.
- **Secrets in logs**, discovered during an audit.
- **`print`/`console.log` in production code**, unleveled and unfilterable.
- **Logging that lies** - a caught exception logged as INFO, or a partial failure logged as
  success.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Observability|Observability]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring|Monitoring]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reading Logs & Stack Traces|Reading Logs & Stack Traces]]

## Sources

- Practitioner synthesis. OpenTelemetry logging conventions - <https://opentelemetry.io/docs/>; Google, *Site Reliability Engineering* - cited only.
