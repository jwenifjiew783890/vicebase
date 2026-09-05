---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Observability

Being able to ask a running system what it is doing, including questions nobody thought of in advance.

## Monitoring vs observability

**Monitoring** answers questions you knew to ask ("is CPU high?"). **Observability** is whether
you can answer new questions from the data already being emitted, without shipping code. The
difference shows up during an incident nobody predicted, which is every interesting incident.

## The three signals, and what each is for

| Signal | Answers | Cost |
| --- | --- | --- |
| **Metrics** | "How much, how often, how slow?" - aggregate, cheap, always on | Low; cardinality is the trap |
| **Logs** | "What exactly happened in this case?" - detailed, per-event | High volume; expensive at scale |
| **Traces** | "Where did the time go across services?" - causal path | Sampling needed |

Use metrics to notice, traces to localise, logs to explain. Reaching for logs first is the most
common time sink.

## Logging that is worth reading

- **Structured, not prose.** Key-value or JSON, so it can be filtered and aggregated. A
  grep-only log is a log you cannot ask questions of.
- **Log decisions and inputs, not just errors.** "Chose provider X because Y was rate-limited"
  is what makes an incident explicable. Errors alone tell you it broke, not why it chose that
  path.
- **One correlation ID through the whole request**, propagated across every service, job and
  retry. Without it, distributed logs are unjoinable.
- **Levels with meaning.** ERROR = someone must act. WARN = suspicious, no action yet. INFO =
  a significant state change. DEBUG = for development. If ERROR is noisy, it will be ignored,
  and then it is not a signal.
- **Never log secrets, tokens, full request bodies with personal data, or whole payloads by
  default.** Logs get shipped, indexed and read widely.
- **Include the context needed to act**: the identifiers, the actual values, the attempt number.
  `"failed to fetch"` costs an hour; `"failed to fetch user=1234 attempt=3/3 status=503 after=61s"`
  costs a minute.

## Metrics that matter

Start with the **four golden signals**: latency, traffic, errors, saturation. For resources, the
**USE method**: utilisation, saturation, errors. For request-driven services, the **RED method**:
rate, errors, duration.

- Record **percentiles** (p50/p90/p99), never only averages. An average hides the tail entirely.
- Beware **cardinality**: a label with user IDs in it will bankrupt the metrics backend.
- Measure what users experience, not only what the server does. Queue time before your handler
  is still latency to them.

## Alerting

Alert on **symptoms**, not causes: "checkout error rate above 2%" rather than "CPU above 80%".
High CPU may be fine; failing checkouts never are. Every alert must be actionable and have a
documented response - an alert nobody acts on trains everyone to ignore the channel.

## Failure modes

- **Logging everything.** Volume so high nothing is findable, and the cost forces retention
  down to uselessness.
- **No correlation ID.** Impossible to reconstruct one request's path.
- **Instrumenting after the incident.** The data you needed was not being collected. Instrument
  the risky path *when writing it*.
- **Alert fatigue.** Noisy alerts get muted, and the muted channel is where the real one lands.
- **Dashboards nobody reads** built instead of alerts that fire.
- **Observability that dies with the process.** If logs are only on a dead container's local
  disk, they do not exist. Ship them.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Logging|Logging]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring|Monitoring]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reading Logs & Stack Traces|Reading Logs & Stack Traces]]

## Sources

- Google, *Site Reliability Engineering*, four golden signals - <https://sre.google/books/> (cited only). Brendan Gregg, the USE method - <https://www.brendangregg.com/usemethod.html>. Tom Wilkie, the RED method. OpenTelemetry documentation - <https://opentelemetry.io/docs/>.
