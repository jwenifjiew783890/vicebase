---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Architecture Failure Modes

How designs go wrong - usually gradually, and usually for locally reasonable reasons.

## Erosion

The architecture on the diagram and the architecture in the code diverge. Each individual
shortcut was defensible under time pressure; the accumulation is a system nobody can describe.

**Signs**: nobody can draw it; the diagram is out of date and everyone knows; new engineers
consistently put things in the wrong place.

**Response**: make the boundaries enforceable rather than aspirational - module-level import
rules, package boundaries, lint rules that fail the build on a forbidden dependency. A boundary
that is only documented is a suggestion.

## The distributed monolith

Services split for organisational reasons, still deploying together, sharing a database, calling
each other synchronously in a chain. Every cost of distribution, none of the independence.

**Signs**: a release requires coordinating several services; one service being down stops
everything; a schema change requires several teams.

**Response**: fix the data ownership first. Splitting components without splitting data does not
decouple anything.

## The shared database

The most common way a boundary is quietly undone. Two components writing the same tables are one
component with two deployments, and neither can change the schema.

**Response**: one writer per table. Others read through an API, a replica, or an event stream.

## Big ball of mud

No discernible structure; everything reachable from everywhere.

**Signs**: no clear entry point; changing anything requires understanding everything; nobody can
say what a module is responsible for.

**Response**: incremental extraction from the edges inward, using seams. Never a rewrite.

## Over-engineering for imagined scale

Sharding, queues, caches, service meshes and abstraction layers for load that never arrives. The
operational cost is paid daily, forever, and the flexibility usually turns out to be for the
wrong axis.

**Signs**: more infrastructure than users; a plugin system with one plugin; abstractions with a
single implementation.

**Response**: delete the unused flexibility. This is usually easy and always resisted.

## The wrong abstraction, enforced

An abstraction built for one shape, now serving five, each needing a flag. Every new case makes
it worse, and everyone works around it.

**Signs**: parameters only one implementation uses; callers reaching past the interface;
`if type ==` inside the abstraction.

**Response**: inline it back and re-derive the boundary from what the code actually does. Going
back to duplication is a legitimate and frequently correct move.

## No back-pressure

A producer faster than its consumer, with an unbounded queue between them. Converts a throughput
problem into an out-of-memory crash, at the worst moment.

**Response**: bound every queue, and decide explicitly what happens when it is full - block, shed,
or reject.

## Single point of failure treated as reliable

One provider, one key, one host, one region, no fallback, no degraded mode. Often not identified
until it fails.

**Response**: name it explicitly in the design. *In this stack, every n8n agent routes to one
model provider; that is documented as a known single point of failure rather than left implicit.*
Naming it is the minimum; a fallback is better.

## Aspirational architecture

A design that describes what people intend rather than what exists. New engineers follow it and
produce code that does not fit reality; the gap widens.

**Response**: document what is, mark what is planned as **FUTURE** explicitly, and generate the
documentation from the system where possible so it cannot drift. *This stack generates its
architecture map from `agent-registry.json` for exactly that reason.*

---

## See also

- [[Coding Knowledge/01 - Software Engineering/Architecture Fundamentals|Architecture Fundamentals]]
- [[Coding Knowledge/08 - Code Quality & Review/Architecture Review|Architecture Review]]
- [[Coding Knowledge/10 - Engineering Experience/Approaches That Commonly Fail|Approaches That Commonly Fail]]

## Sources

- Practitioner judgement. Related published framing: Brian Foote & Joseph Yoder, "Big Ball of Mud" (1997) - <http://www.laputan.org/mud/>; Sandi Metz on the wrong abstraction - <https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction>. The stack-specific examples are from this project.
