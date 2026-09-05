---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Testing

What actually provides confidence, what only looks like it does, and how to spend a limited testing budget.

## What a test is for

A test exists to **detect a regression you would otherwise ship**. Judge every test by that:
if this behaviour broke, would this test fail? If not, the test is decoration - and worse,
it contributes to a green pipeline that means nothing.

The corollary is the sharpest check available: **a new test should fail if you revert the
change it covers.** Verify that once, and you know the test is real.

## The levels

| Level | Scope | Speed | Use for |
| --- | --- | --- | --- |
| **Unit** | One function/class, no I/O | ms | Logic, branches, edge cases, algorithms |
| **Integration** | Real DB, real HTTP, real file system | 100ms-s | Wiring, queries, serialisation, migrations |
| **End-to-end** | The whole system as a user | s-min | A handful of critical journeys only |
| **Contract** | The agreement between two services | fast | Preventing a provider from breaking consumers |
| **Property-based** | Invariants over generated inputs | varies | Parsers, encoders, anything with round-trips |

Most value per second of runtime is in **unit and integration**. E2E tests are valuable and
expensive: slow, flaky, and they fail in ways that do not localise. Keep a small, curated set
covering the journeys whose failure would be unacceptable.

## Test behaviour, not implementation

Assert on what the caller observes. A test that asserts a private method was called breaks on
every refactor while catching no real defect - it converts your test suite from a safety net
into a change tax. This is the single most common cause of a suite that engineers resent.

## Where the bugs actually are

Spend the budget at the boundaries, not the middle:

- empty, one element, exactly the limit, one over the limit
- zero, negative, very large, NaN, precision loss
- null / missing / absent-versus-empty distinctions
- unicode, emoji, right-to-left text, very long strings
- duplicate submissions and out-of-order arrival
- concurrent access to the same record
- the dependency being slow, down, or returning malformed data
- interruption halfway through a multi-step operation

## Mocking

Mock at the **system boundary** - the network, the clock, the file system, the payment
provider - and use the real thing everywhere inside. Mocking your own internal classes couples
tests to structure and lets integration bugs through untouched.

A mock encodes an assumption about how the dependency behaves. When that assumption is wrong,
your tests pass and production fails. Keep at least one test against the real dependency.

## Determinism

Flaky tests are worse than no tests: they train the team to re-run until green, and that habit
is what lets a real failure through. Fix them or delete them; never re-run them as policy.

Common causes: real time and timezones, real network, shared state between tests, test order
dependence, unseeded randomness, and timing assumptions (`sleep(100)` instead of waiting for a
condition).

## Coverage

Coverage measures which lines ran, not whether anything was verified. 100% coverage with weak
assertions is a comforting number and nothing more. Use it to *find untested areas*, never as a
target to satisfy - as a target, it produces tests written to touch lines.

## Failure modes

- **Tests written after, to fit the code.** They document what the code does, including its bugs.
- **The suite that is slow enough to skip.** If it takes 40 minutes, it will be bypassed.
- **Fixtures nobody understands** - a 400-line setup that every test depends on and nobody dares
  change.
- **Testing the framework.** Verifying that the ORM saves a row.
- **No test for the failure path.** The error handling has never executed.

---

## See also

- [[Coding Knowledge/09 - Engineering Practices/Testing Strategy|Testing Strategy]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Regression Investigation|Regression Investigation]]
- [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]]

## Sources

- Practitioner synthesis. References: Martin Fowler on the test pyramid and test doubles - <https://martinfowler.com/bliki/TestPyramid.html>; Kent Beck, *Test-Driven Development* (2002) - cited, not reproduced; Google Testing Blog on flaky tests - <https://testing.googleblog.com/>.
