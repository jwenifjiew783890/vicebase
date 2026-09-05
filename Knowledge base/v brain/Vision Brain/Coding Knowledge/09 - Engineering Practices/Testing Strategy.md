---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# Testing Strategy

Deciding what to test, at which level, given that the budget is finite.

## Spend where failure is expensive and detection is hard

Not uniformly. The allocation that works:

| Area | Investment | Why |
| --- | --- | --- |
| Money, data integrity, security, permissions | Heavy | Failure is unacceptable and often silent |
| Core business logic | Heavy | Everything depends on it |
| Complex algorithms and parsers | Heavy, property-based | Edge cases are unbounded |
| Integration points | Moderate | Wiring breaks; mocks hide it |
| CRUD and glue | Light | Failures are obvious and cheap |
| Presentation | Light | Changes often, breaks visibly |
| Third-party internals | None | Not your code |

## The levels, and what each is for

**Unit** - logic, branches, edge cases. Fast enough to run constantly. Should be the bulk by
count.

**Integration** - the wiring: real database, real HTTP, real serialisation, real migrations.
Catches what unit tests structurally cannot, because unit tests mock exactly the boundary where
integration bugs live.

**End-to-end** - a handful of critical journeys. Expensive, slow, flaky, and they do not localise
failures. Keep the set small and curated; a large E2E suite is a tax that eventually gets muted.

**Contract** - the agreement between a provider and its consumers. Prevents a provider breaking
someone downstream without a full integration environment.

**Property-based** - invariants over generated inputs. Exceptional value for parsers, encoders,
serialisers and anything with a round-trip property. Finds cases nobody would write.

## The rule that makes tests real

**A test must fail when the behaviour it covers breaks.** Verify this once, deliberately, by
reverting the change and watching the test fail. A test that passes in both directions is a
liability: it contributes to a green pipeline that means nothing.

## Test behaviour, not implementation

Assert on what a caller observes. Asserting on internal calls means the suite breaks on every
refactor while catching no real defect - which converts tests from a safety net into a change
tax, and that is how teams end up resenting them.

## Where to mock

At the **system boundary**: the network, the clock, the filesystem, third-party services.
Everywhere inside, use the real thing. Mocking internal classes couples the tests to structure
and lets integration bugs through.

Keep at least one test against the real dependency - a mock encodes an assumption, and when the
assumption is wrong every test passes and production fails.

## Speed as a strategy decision

A suite too slow to run will be bypassed, and then it protects nothing. Sub-second unit tests,
integration tests in a couple of minutes, E2E on a schedule or on merge. **If forced to choose
between more coverage and a faster suite, take the faster suite** - it is the one that actually
runs.

## Flakiness

Fix or delete. Never re-run as policy: that habit is precisely what lets a real failure through.
Common causes are real time, real network, shared state, test ordering, unseeded randomness, and
`sleep` instead of waiting for a condition.

## Coverage

A diagnostic, never a target. It measures which lines executed, not whether anything was
verified. As a target, it produces tests written to touch lines - which is worse than no tests,
because it looks like protection.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Regression Investigation|Regression Investigation]]
- [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]]

## Sources

- Martin Fowler on the test pyramid and test doubles - <https://martinfowler.com/bliki/TestPyramid.html>; Google Testing Blog on flaky tests - <https://testing.googleblog.com/>. Synthesised.
