---
type: note
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Engineering Principles

The rules that apply to every piece of code, in the order they should be applied. When two principles conflict, the one earlier in this list wins.

## 1. Correct before fast, clear before clever

Wrong code that is fast is worthless. Working code nobody can change is a liability with a
delay fuse. Optimise only against a measurement - see
[[Coding Knowledge/07 - Debugging & Problem Solving/Performance Profiling|Performance Profiling]].

## 2. Make the smallest change that does the job

A diff's cost is not its line count, it is the surface a reviewer must reason about and the
number of ways it can break something else. Unrequested refactors bundled into a fix hide the
fix. If a refactor is needed, do it as its own change.

## 3. Match the surrounding code

Consistency inside a file beats personal preference. Read the neighbouring functions before
writing: naming, error style, comment density, test layout. Two valid styles in one file is
worse than one style you dislike.

## 4. Make invalid states unrepresentable

Prefer the type system, the schema and the constructor to a runtime check. A field that can be
`null` will be `null` at the worst moment. Parse input into a validated shape once at the
boundary rather than re-checking it at every use - the "parse, don't validate" discipline.

## 5. Fail loudly, early, and at the boundary

Silence is the expensive failure mode. A swallowed exception costs hours later; a crash costs
minutes now. Validate at system boundaries - request handlers, file loads, subprocess results -
and let the interior assume validity.

> [!warning] The catch-all that eats the cause
> `except Exception: pass` and `catch {}` are the two most expensive lines in software. If you
> genuinely must continue, log the exception *with its traceback* and record that you continued.

## 6. Errors must carry enough to act on

An error message is a user interface for whoever is woken by it. It should say what was being
attempted, what was received, and what to do. `ValueError: invalid input` is a bug in itself.

## 7. One source of truth

Every fact should live in exactly one place. A value duplicated across a config file, a
constant and a comment will drift, and the drift will be discovered by an outage.

## 8. Idempotence where retries exist

Anything a caller can retry - a queue consumer, an HTTP handler, a deploy step - will be
retried, including after a partial success. Design it so running twice equals running once.

## 9. Explicit over implicit

Implicit ordering, implicit globals, implicit type coercion and implicit environment
dependencies are all forms of hidden state, and hidden state is what makes bugs
non-reproducible.

## 10. Design for deletion

The clearest sign of a good boundary is that the component behind it can be removed without
archaeology. Ask "what breaks if this is deleted?" - if the answer is unclear, the boundary
is not real.

## 11. Observability is a feature, not an afterthought

If a system cannot be asked what it is doing, every incident starts from zero. Log decisions
and inputs, not just errors. See
[[Coding Knowledge/01 - Software Engineering/Observability|Observability]].

## 12. Reversibility beats correctness of prediction

You will guess wrong about the future. Prefer decisions that are cheap to undo: a feature flag
over a rewrite, an adapter over a hard dependency, a migration that can roll back. Spend the
"hard to reverse" budget only where it buys something.

## 13. Do not claim what you did not verify

If the tests were not run, say the tests were not run. If a change is untested, say so in the
report. A confident false claim is more damaging than an admitted gap - it removes the
reviewer's reason to check.

## Applying these under uncertainty

When a decision is genuinely ambiguous, the tiebreak order is: **does it fail safely -> can it
be undone -> is it readable -> is it fast**. Optimising the fourth at the expense of the first
is the classic novice trade.

---

## See also

- [[Coding Knowledge/05 - Failure Patterns|Failure Patterns]]
- [[Coding Knowledge/01 - Software Engineering/Maintainability|Maintainability]]
- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]
- [[Coding Knowledge/10 - Engineering Experience/Practitioner Heuristics|Practitioner Heuristics]]

## Sources

- Synthesised from long-standing practice. Closest published statements: Google, *Engineering Practices* - <https://google.github.io/eng-practices/> (CC BY 3.0); Google, *Site Reliability Engineering* - <https://sre.google/books/> (readable online, (c) Google, not redistributable); Alexis King, "Parse, don't validate" - <https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/>.
