---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Design Patterns

Named solutions to recurring problems. Useful as vocabulary; harmful when applied for their own sake.

## How to use patterns

A pattern is a **compressed description of a trade-off**, not a goal. The correct sequence is:
notice a recurring problem, recognise the pattern that addresses it, apply the minimum of it.
Starting from the pattern and looking for somewhere to put it produces the classic
over-engineered codebase.

## The ones that earn their keep

**Strategy** - swap an algorithm behind one interface. Use when the variation is real and
runtime-selected. In most languages a function parameter is the whole pattern; a class
hierarchy is usually excess.

**Adapter** - make an external interface fit yours. This is the standard defence against a
third-party API: your code talks to your interface, one adapter absorbs the vendor's shape, and
replacing the vendor touches one file.

**Facade** - one simple entry point over a complicated subsystem. Good for narrowing a large
surface to the part actually used.

**Repository** - data access behind an interface expressed in domain terms. Buys testability
and a single place for query changes. Costs a layer; skip it for a script.

**Observer / pub-sub** - decouple producer from consumers. Watch for the debugging cost: control
flow becomes invisible, and "who handled this event?" is a hard question at 3 a.m.

**Command** - an action as an object, so it can be queued, logged, retried, undone. Natural fit
for job systems and agent tool calls.

**State machine** - explicit states and permitted transitions. Any workflow with more than about
three statuses should be one; the alternative is a spread of booleans that permit impossible
combinations.

**Circuit breaker** - stop calling a failing dependency, fail fast, probe occasionally. Essential
wherever a remote call sits on a hot path.

**Bulkhead** - separate resource pools so one saturated dependency cannot consume every thread
or connection.

**Retry with backoff and jitter** - the correct form of retry. Without jitter, retries
synchronise into a thundering herd.

**Idempotency key** - caller supplies a unique key; server does the work once and returns the
same result on repeats. The standard answer to "did that request actually go through?".

**Outbox** - write the event to the same database transaction as the state change, publish
asynchronously. Removes the dual-write problem where the DB commits and the message does not.

**Saga** - a long-running process as a sequence of local transactions with compensating actions.
Use when a distributed transaction is impossible, and accept that compensation is business
logic, not a rollback.

**Feature flag / strangler fig** - ship the new path alongside the old, migrate traffic
incrementally, delete the old. The mechanism behind almost every successful large migration.

## Anti-patterns worth naming

- **Singleton** as a global variable with a nicer name. Hides dependencies and ruins tests.
- **God object** - one class that knows everything.
- **Anaemic domain model** - data classes with no behaviour and a "service" layer holding all
  the logic; the object model is then decorative.
- **Abstract factory factory** - indirection with no variation behind it.
- **Inheritance for reuse** - subclassing to borrow code rather than to model a real "is-a".
  Composition is almost always the better tool.
- **Premature genericity** - a plugin system with one plugin.

## The test before applying a pattern

Ask: *what does this let me change cheaply that I could not before, and is that change actually
likely?* If there is no honest answer, do not apply it.

---

## See also

- [[Coding Knowledge/12 - Reliability Engineering/Stability Antipatterns|Stability Antipatterns]]
- [[Coding Knowledge/01 - Software Engineering/Modularity & Abstraction|Modularity & Abstraction]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/10 - Engineering Experience/Approaches That Commonly Fail|Approaches That Commonly Fail]]

## Sources

- Gamma, Helm, Johnson & Vlissides, *Design Patterns* (1994) - cited, not reproduced; Michael Nygard, *Release It!* (2nd ed., 2018) for circuit breaker, bulkhead and timeout patterns - cited, not reproduced; Chris Richardson, microservices patterns including saga and outbox - <https://microservices.io/patterns/>; Martin Fowler on the strangler fig - <https://martinfowler.com/bliki/StranglerFigApplication.html>.
