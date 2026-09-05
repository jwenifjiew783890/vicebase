# How I Think

## Systems-Oriented Thinking

I naturally tend to think about systems as interconnected parts
rather than isolated features.

When designing a large project, I prefer to understand:

- what belongs in the core
- what should be an extension
- what should be reusable infrastructure
- what should remain replaceable
- how components communicate
- how future changes will affect the architecture

## Modular Thinking

I strongly prefer modular architecture.

A feature should not automatically become part of the core simply
because it is useful.

Before adding something, consider:

- Does this belong in Core?
- Should it be a plugin?
- Should it be a service?
- Should it be an external provider?
- Can it be removed without breaking the system?

## Learn From Previous Mistakes

Previous projects are used as architectural lessons.

When an earlier approach caused excessive coupling or complexity,
the lesson should be recorded and considered in future projects.

## Build for the Future

I often think ahead about capabilities that may not exist yet.

Architecture should therefore provide clean extension points without
prematurely implementing every future idea.

## Practical Principle

Future-proof through boundaries and interfaces,
not by building every future feature immediately.

## Development Discipline

Prefer:

PLAN
→ REVIEW
→ APPROVE
→ IMPLEMENT
→ TEST
→ VERIFY

over rushing directly into implementation.