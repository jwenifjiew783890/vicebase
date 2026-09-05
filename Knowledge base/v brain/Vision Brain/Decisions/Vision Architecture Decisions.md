# Vision Architecture Decisions

## ADR-001 — Vision is the Platform

Vision is the primary application/platform.

Ollama, local runtimes, API providers, models, agents, memory systems,
and integrations are components used by Vision.

Vision should not become tightly coupled to any one provider or model.

---

## ADR-002 — Body vs Engine

Vision's BODY contains:

- UI
- Chat
- Code workspace
- Terminal
- Projects
- Models UI
- Settings
- Plugin UI
- Orb

The ENGINE contains:

- model inference
- providers
- agents
- tools
- memory
- external integrations
- advanced orchestration

Build the body first and connect engines later.

---

## ADR-003 — Mature Infrastructure First

Do not rebuild mature infrastructure unnecessarily.

Use established technologies for:

- local inference
- terminal/PTY
- 3D rendering
- agent protocols
- UI primitives
- editors/viewers where useful

Vision's unique value is the integration and product experience.

---

## ADR-004 — Provider/Runtime Abstraction

Vision must not be locked to Ollama.

Separate:

MODEL
PROVIDER
RUNTIME
ENDPOINT
CREDENTIAL
CAPABILITIES

Possible sources include:

- Ollama
- llama.cpp
- vLLM
- LM Studio
- NVIDIA APIs
- other OpenAI-compatible APIs
- future runtimes/providers

---

## ADR-005 — Dynamic Models

Models must not be hardcoded into Vision.

Vision should discover/configure models dynamically.

The same UI should work whether a model is:

- local
- LAN-hosted
- remote
- API-based
- cloud
- served through another runtime

---

## ADR-006 — Per-Session Model Selection

Settings contain default model preferences.

The active model belongs to the session/conversation/task.

Changing a global default must not silently change an existing conversation.

---

## ADR-007 — Agents Are Workers

Agents are not the same thing as models.

Model = intelligence.

Agent = role + instructions + tools + permissions + workflow.

Agents should work inside experiences such as Chat and Code rather than
turning Vision into an agent-management dashboard.

---

## ADR-008 — Plugins Stay Outside Core

Optional integrations belong in plugins whenever practical.

Examples:

- Obsidian
- Blender
- memory systems
- Ponytail
- future services

Removing a plugin must not require rewriting Vision Core.

---

## ADR-009 — Obsidian is External Knowledge

Obsidian is an external knowledge/memory system.

It is not part of Vision Core.

Vision may eventually access it through a controlled plugin/adapter.

---

## ADR-010 — Hardware Neutrality

Hardware may influence:

- recommendations
- estimated performance
- warnings
- runtime suggestions

Hardware must not permanently remove models or capabilities from Vision.

The same Vision application should work across different hardware.

---

## ADR-011 — Security Boundaries

Renderer code must not receive unrestricted system access.

Terminal, filesystem, credentials, plugins, and future agent actions
must cross controlled security boundaries.

---

## ADR-012 — Incremental Development

Development principle:

PLAN → APPROVE → IMPLEMENT → TEST → STOP

Every major stage must leave Vision runnable.

---

## ADR-013 — Self-Improvement Is a Layer Underneath, Not a Second Architecture

Vision may gain a self-improving agent layer. It sits UNDERNEATH `VISION — AGENTS`,
which remains the top-level orchestrator.

The layer learns from successful tasks, failures, corrections and user feedback, and
creates, improves, persists and reuses skills.

Constraints that are not negotiable:

- Obsidian stays the source of truth; no full-vault duplication into Open WebUI Knowledge
- the agent does not freely modify Vision itself
- learning changes are reviewable, reversible and isolated
- heavy executors stay on-demand: OFF → TASK → OFF
- no second large independent agent architecture if a mature system already covers it

NousResearch Hermes is the preferred candidate. Preferred is not selected: a clearly
better mature open-source alternative wins, and any alternative is REPORTED before it
is installed.

Status: requirement recorded. Audit, comparison and selection have not been done, and
nothing has been implemented.

Full requirements: [[Agents/Self-Improving Agent Layer — Requirements]]
