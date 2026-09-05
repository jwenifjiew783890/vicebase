# Things Vision Should Remember

This is a curated memory layer for information that is useful to
Vision across future conversations and projects.

Only information intentionally recorded here should be treated as
long-term memory.

---

## Vision

Vision is the user's primary long-term AI platform project.

The user wants Vision to eventually become a primary alternative to
Claude for everyday AI work.

Vision should provide:

- Chat
- Code
- Projects
- Models
- Terminal
- Agents
- Plugins
- External integrations

---

## Product Philosophy

Vision should feel like one coherent premium AI product.

It should not feel like:

- an Ollama frontend
- a collection of tools
- an admin dashboard
- a VS Code clone

---

## Architecture Philosophy

Vision Core should remain stable.

Optional functionality should be isolated whenever practical.

Models, runtimes, agents and external integrations should remain
replaceable.

Plugins should be preferred for optional integrations.

---

## Model Philosophy

Vision should support multiple model sources.

Examples:

- Local models
- Ollama
- Other local runtimes
- API providers
- Remote endpoints
- Cloud models

The user should be able to choose models for different purposes.

---

## Agent Philosophy

Agents are specialized workers.

Potential roles include:

- Coding
- Planning
- Research
- Debugging
- Testing
- Automation

Agents should operate through controlled tools and permissions.

---

## Plugin Philosophy

External systems should preferably be integrated through plugins.

Examples:

- Obsidian
- Blender
- Memory systems
- Ponytail
- Future services

A plugin should be removable without requiring Vision Core to be
rewritten.

---

## Obsidian

Obsidian is intended to serve as an external knowledge/memory layer
for Vision.

The vault remains independent from Vision.

Future connection:

Vision
→ Obsidian plugin/adapter
→ Obsidian knowledge

Obsidian is not Vision Core.

---

## Development Philosophy

The preferred workflow is:

PLAN
→ APPROVE
→ IMPLEMENT
→ TEST
→ VERIFY
→ STOP

Avoid rushing multiple architectural layers together.

---

## Engineering Preference

When a mature solution already exists, prefer integrating or adapting
it rather than rebuilding it unnecessarily.

Examples:

- model runtimes
- terminal infrastructure
- agent protocols
- UI primitives
- graphics infrastructure

---

## Hardware Philosophy

Hardware limitations should influence recommendations and performance
expectations.

They should not permanently constrain Vision's architecture or model
catalog.

---

## Current Vision Development

Vision is currently being built incrementally from the body outward.

Completed foundation:

- Electron foundation
- Design system
- Secure IPC
- Settings
- Application shell
- Chat
- 3D Orb

Future development includes:

- Real terminal
- Model providers
- Local/API model integration
- Projects
- Code workspace
- Coding agents
- Plugins
- Obsidian integration