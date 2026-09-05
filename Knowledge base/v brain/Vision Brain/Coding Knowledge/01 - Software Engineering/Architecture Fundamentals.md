---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Architecture Fundamentals

Architecture is the set of decisions that are expensive to reverse. Everything else is design.

## What actually counts as architecture

A decision is architectural if changing it later means changing many components at once, or
migrating data, or coordinating a release. In practice that is:

- the boundaries between components and who owns which data
- the communication style across those boundaries (sync call, async message, shared store)
- the data model and its storage engine
- the consistency and failure model
- the security and trust boundaries
- the deployment and runtime topology

Framework choice, folder layout and library selection usually are **not** architectural, though
they are often argued about as if they were.

## The forces to balance

Every architecture trades between: **performance, scalability, reliability, security,
changeability, operability, and cost**. You cannot maximise all of them. Naming which two you
are optimising, and which you are deliberately sacrificing, is most of the work - see
[[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]].

## Styles, and what each actually buys

| Style | Buys | Costs |
| --- | --- | --- |
| **Modular monolith** | Simple deploy, transactions, easy refactor across boundaries | One failure domain, one scaling unit, one language |
| **Microservices** | Independent deploy and scale, team autonomy, failure isolation | Network in every call path, distributed data, operational load |
| **Event-driven** | Decoupled producers/consumers, natural buffering, replay | Eventual consistency, ordering and duplicate handling, hard debugging |
| **Layered** | Clear dependency direction, testable core | Ceremony; layers that just forward calls |
| **Hexagonal / ports & adapters** | Domain logic independent of I/O, genuinely testable | More indirection than small systems need |
| **Pipeline** | Composable stages, easy to reason about one step | Whole-pipeline failure semantics need designing |

**The default should be a modular monolith** with real internal boundaries. It keeps the option
of splitting later; splitting early forecloses the option of merging.

## Conway's law is a design constraint

Systems take the shape of the communication structure of the organisation that builds them. If
one person maintains everything, a fine-grained service mesh will not stay coherent. Design the
architecture for the team that exists.

## Coupling and cohesion, concretely

- **Cohesion**: things that change together live together. If a feature change touches six
  directories, cohesion is wrong.
- **Coupling**: what one component must know about another. Rank from best to worst - data
  passed as arguments, a published interface, a shared schema, a shared database table, a
  shared mutable global.
- **Dependency direction**: point dependencies toward stability. Business rules should not
  depend on the HTTP framework; the framework adapter depends on the rules.

## Failure modes

- **Architecture by accretion.** Nobody decided; the shape emerged from a hundred local choices.
  Symptom: no one can draw the system.
- **Resume-driven design.** A technology chosen for interest rather than fit.
- **Ignoring the data.** Component boundaries drawn without deciding data ownership; the shared
  database quietly re-couples everything.
- **Uniform treatment.** Applying the highest-reliability pattern to every path, including the
  ones nobody would notice failing.
- **Big rewrite.** Almost always underestimates the accumulated knowledge encoded in the old
  system's edge cases.

## When to revisit

Revisit architecture when a *class* of change keeps being expensive - not when one change was
annoying. Three painful changes of the same shape is evidence; one is noise.

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Modularity & Abstraction|Modularity & Abstraction]]
- [[Coding Knowledge/01 - Software Engineering/Scalability|Scalability]]
- [[Coding Knowledge/09 - Engineering Practices/System Design|System Design]]
- [[Coding Knowledge/10 - Engineering Experience/Architecture Failure Modes|Architecture Failure Modes]]

## Sources

- Practitioner synthesis. Core references: Martin Fowler, *Software Architecture Guide* - <https://martinfowler.com/architecture/>; Martin Kleppmann, *Designing Data-Intensive Applications* (2017) - cited, not reproduced; Melvin Conway (1968), "How do committees invent?".
