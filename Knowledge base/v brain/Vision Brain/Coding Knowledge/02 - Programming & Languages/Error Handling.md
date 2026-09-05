---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Error Handling

Deciding what an error is, who handles it, and how to avoid the two failure modes: swallowing and drowning.

## The two failure modes

**Swallowing** - catching and continuing without recording anything. The failure becomes a wrong
answer somewhere else, hours later, with no trace back to the cause. This is the most expensive
mistake in this note.

**Drowning** - catching and logging at every level, so one failure produces forty log lines and
the actual cause is buried. Handle once, at the level that can actually do something.

## Errors versus bugs

- **Expected failures**: the network is down, the file is missing, the input is invalid, the
  user is not authorised. These are part of the design. Model them as values - a `Result`, an
  error return, a typed exception - and handle them.
- **Bugs**: null dereference, index out of range, an impossible state, a violated invariant.
  These should crash loudly, not be caught. A caught bug is a corrupted program still running.

A blanket `except Exception` catches both, which is why it is almost always wrong.

## Where to handle

Handle at the level that has enough context to **decide**. Everywhere else, add context and
propagate.

- A database helper does not know whether a failed read should retry, use a default, or abort.
- A request handler does.

So the helper enriches - "failed reading user 1234 from the primary" - and re-raises; the
handler decides. This is why exception chaining (`raise ... from e`, `.context(...)`,
`{cause: e}`) matters: it builds a narrative from the low-level cause up to the business
operation.

## Writing an error message

An error message is read by someone under pressure who does not have your context. Include:

1. **What was being attempted** - "publishing workflow visionAgtCoding"
2. **What actually happened** - "HTTP 409 from n8n"
3. **The identifying values** - which record, which file, which attempt
4. **What to do**, if it is knowable - "the workflow is active; deactivate it first"

`Error: operation failed` fails all four.

> [!warning] Never put an unbounded value in an error message
> Interpolating an entire request body or a 10 MB string into an exception makes logs unusable
> and can leak secrets.

## Rules

- **Never catch what you cannot handle.** Let it propagate.
- **Never catch broadly to convert to a default.** `except: return []` turns an outage into
  silently empty results, and it will be believed.
- **Preserve the cause.** Losing the original exception discards the only useful information.
- **Clean up with the language's guaranteed mechanism** - `finally`, `with`, `defer`, RAII,
  `try/finally`. An error path that skips cleanup leaks resources exactly when the system is
  already stressed.
- **Validate at the boundary, trust inside.** Re-checking everywhere is noise; checking nowhere
  is a vulnerability.
- **Distinguish retryable from permanent.** Retrying a 400 forever is a bug; not retrying a 503
  is a missed recovery.
- **Errors crossing a process boundary lose their type.** Design a serialisable error shape with
  a stable code - see [[Coding Knowledge/02 - Programming & Languages/API Design|API Design]].
- **Timeouts are errors too**, and they carry an extra property: the operation's outcome is
  *unknown*, not failed. Treat it as such.

## Language notes

- **Python**: `raise NewError(...) from e` preserves the chain. Never bare `except:` - it
  catches `KeyboardInterrupt` and `SystemExit`.
- **JavaScript**: an unhandled promise rejection terminates modern Node. `Error.cause` chains.
- **Go**: `if err != nil` every time; wrap with `fmt.Errorf("...: %w", err)` to keep
  `errors.Is`/`errors.As` working.
- **Rust**: `?` with `thiserror` for libraries, `anyhow` with `.context()` for applications.
- **C**: check every return value; the ones nobody checks are `close`, `write` and `printf`.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/02 - Programming & Languages/API Design|API Design]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reading Logs & Stack Traces|Reading Logs & Stack Traces]]

## Sources

- Practitioner synthesis. Language-specific behaviour from each language's official documentation: Python exceptions - <https://docs.python.org/3/tutorial/errors.html>; Go error handling - <https://go.dev/blog/go1.13-errors>; Rust error handling in *The Rust Programming Language* - <https://doc.rust-lang.org/book/ch09-00-error-handling.html>.
