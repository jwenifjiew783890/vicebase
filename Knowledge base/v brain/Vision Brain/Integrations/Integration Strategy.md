# Vision Integration Strategy

## Principle

External applications and services should remain outside Vision Core
whenever practical.

Use plugins/adapters.

## Obsidian

Purpose:
External knowledge and memory.

Future capabilities may include:

- search notes
- read notes
- create notes
- update notes
- retrieve project context
- store decisions
- store long-term knowledge

## Blender

Potential future capabilities:

- project interaction
- asset workflows
- automation
- controlled agent interaction

## Memory Systems

Future memory systems should preferably be plugins rather than
hardcoded into Vision Core.

## Ponytail

Treat as a future optional integration.

## Failure Isolation

An integration failure must not make Vision Core unusable.

## Security

Plugins should have explicit capabilities and permissions.

Do not grant blanket filesystem/network access by default.