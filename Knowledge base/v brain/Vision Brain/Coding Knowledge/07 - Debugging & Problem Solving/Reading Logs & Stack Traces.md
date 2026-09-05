---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Reading Logs & Stack Traces

Extracting the answer from evidence you already have, which is usually faster than producing more.

## Read the whole trace, from the bottom

The top frame is where the error **surfaced**. The cause is usually deeper, and in a chained
exception it is in a different exception entirely.

- **Python**: read bottom-up. `During handling of the above exception, another occurred` and
  `The above exception was the direct cause` both mean **the first exception is the real one**
  and the visible one is a consequence.
- **Java/.NET**: `Caused by:` sections - read the last one.
- **JavaScript**: async stacks may be truncated; `Error.cause` chains where used.
- **Rust/Go**: the context chain (`anyhow` context, wrapped errors) reads as a narrative from
  the operation down to the cause.

**Find your own code in the trace.** Twenty framework frames and two of yours - the boundary
between them is where to look. The last frame in your code before entering the library is
usually where the wrong value was passed.

## What the message actually says

Read it literally. "No such file or directory: `config/settings.yaml`" contains a **relative
path**, which means the working directory is part of the problem. "Connection refused" means
something answered; "timeout" means nothing did. "Permission denied" names a specific
operation on a specific resource.

Precision matters: `None` is not `""`, `KeyError` is not `AttributeError`, and 401 is not 403.
Each distinction narrows the search substantially.

## Searching logs effectively

```
grep -i error app.log | sort | uniq -c | sort -rn | head -20
```

That idiom - **count and rank distinct messages** - is the fastest way to see what is actually
happening in a large log. A message appearing 4,000 times and one appearing twice are different
kinds of evidence, and the rare one is often the interesting one.

Then:

- **Grep by correlation ID** to get one request's whole path.
- **Use context flags** (`-A`, `-B`, `-C`) - the lines around an error usually carry the state.
- **Bound by time** first (`journalctl --since`, or a timestamp range) so you are reading the
  right window.
- **Look just before the first error**, not at the error itself. The last successful operation
  tells you how far it got.
- **Look for what is missing.** A gap in a regular heartbeat, an absent "completed" line, a
  request with no response. Absence is evidence and greps do not find it.

## Correlating across sources

Line up application logs, the reverse proxy, the database and system logs on one timeline. The
sequence usually tells the story: a slow query, then a connection pool exhaustion, then request
timeouts, then a health check failure, then a restart - four of which are symptoms of the first.

**Check clock skew** before trusting cross-host ordering. Two hosts a few seconds apart will
produce a confidently wrong causal story.

## When the logs say nothing

That is itself information:

- **The error was swallowed.** Search for bare `except`/`catch` on that path.
- **The log level filters it.** DEBUG statements exist and are not emitted.
- **It never got there.** The failure is earlier than the first log line - startup,
  configuration, DNS, or the process not being the one you think.
- **The output goes elsewhere** - a different file, stdout captured by a service manager, a
  container whose logs are not being collected.
- **The process died without a chance to log** - OOM kill (`dmesg`, exit code 137), SIGKILL, or
  a segfault.

## Failure modes

- **Reading only the first line** of a trace.
- **Skipping the chained exception**, which is the actual cause.
- **Trusting timestamps** across hosts without checking skew.
- **Grepping for `error`** and missing failures logged at WARN or INFO.
- **Not checking whether the log is fresh** - reading yesterday's file, or a rotated one.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Logging|Logging]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Systematic Debugging|Systematic Debugging]]
- [[Coding Knowledge/02 - Programming & Languages/Error Handling|Error Handling]]

## Sources

- Language runtime documentation for traceback formats (Python, Java, .NET, Rust). Practitioner synthesis for the search techniques.
