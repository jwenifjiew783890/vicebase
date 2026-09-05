# Architecture Lessons

## Main Lesson

Do not put every new capability directly into the application's core.

## What to Avoid

A growing core containing:

- memory
- integrations
- external tools
- model-specific logic
- specialized workflows

This creates unnecessary coupling and makes future changes risky.

## Vision Rule

Optional capability → plugin or isolated service when practical.

## Failure Isolation

If an integration fails:

Disable/unplug the integration.

Vision Core should continue functioning.

## Development Lesson

Do not build deep backend infrastructure before proving the application
can actually launch and be tested.

## Vision Rule

Always build breadth-first:

working foundation
→ verified feature
→ next feature

Never leave the application in an un-runnable state.

## Long-Term Principle

Keep the body stable.

Allow models, agents, memory, integrations and tools to evolve independently.