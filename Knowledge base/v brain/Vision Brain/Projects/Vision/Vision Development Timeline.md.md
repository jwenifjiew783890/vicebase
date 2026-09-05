# Vision Development Timeline

## Vision 1.0 — Rebuild from Lessons Learned

Vision is a clean rebuild intended to avoid the architectural
mistakes made in earlier AI projects.

The project should be developed as a stable platform rather than
a monolithic AI application.

---

## Initial Vision Concept

Original goal:

Create a premium desktop AI application with a Claude-like user
experience while allowing the underlying intelligence to come from
different local or remote models.

Vision should eventually provide:

- Chat
- Code
- Projects
- Models
- Terminal
- Plugins
- Settings
- Agents
- Tools
- External integrations

---

## Body First

Decision:

Build the Vision body before building its AI engine.

Body includes:

- application shell
- Chat UI
- Code workspace
- Terminal
- Projects
- Models UI
- Settings
- Plugin UI
- Orb

Engine/capabilities are added afterward.

Reason:

Prevent the project from becoming difficult to test or debug before
the application itself is stable.

---

## Mature Infrastructure

Decision:

Do not reinvent mature infrastructure.

Potential infrastructure includes:

- Electron
- React
- TypeScript
- xterm.js
- node-pty / ConPTY
- Three.js / React Three Fiber
- mature agent protocols
- existing model runtimes
- mature UI libraries

Vision should build the product layer and integrate existing
infrastructure.

---

## Model Independence

Decision:

Vision must not be an Ollama-only application.

Possible future sources:

- Ollama
- llama.cpp
- vLLM
- LM Studio
- OpenAI-compatible servers
- NVIDIA APIs
- custom API endpoints
- other future runtimes

Models must be dynamically discoverable/configurable.

---

## API-First Development

Initial development does not require local models.

API-accessible models can be used for testing while Vision's local
runtime support is developed independently.

This prevents local hardware from blocking application development.

---

## Local Model Workflow

Future intended workflow:

Vision Terminal
→ install/configure runtime
→ install model
→ Vision discovers model
→ model appears in Models
→ select model
→ use in Chat or Code

The user should not need to modify Vision's source code when adding
a model.

---

## Chat

Chat is a primary Vision experience.

Goal:

Provide a premium Claude-like conversational environment.

Future capabilities include:

- conversations
- model selection
- files
- attachments
- images
- image generation
- markdown
- code
- streaming
- tools
- agents

---

## Code

Code is a Claude Code-style AI coding workspace.

It is not intended to become a traditional IDE or VS Code clone.

Future coding workflow:

Select project
→ select coding model
→ describe task
→ agent understands project
→ agent plans
→ agent modifies files
→ agent runs terminal commands
→ agent tests
→ agent fixes
→ agent reports changes

---

## Vision Terminal

Vision will eventually contain a real Windows terminal.

Purpose:

- development
- PowerShell/CMD
- runtime management
- local model installation
- AI infrastructure management
- future coding-agent execution

The terminal should remain a general-purpose terminal rather than
a special fake model installer.

---

## Agents

Agents are future workers.

Possible roles:

- Coding
- Planning
- Research
- Debugging
- Testing
- Project analysis
- Automation

A model and an agent are different concepts.

Model = intelligence.

Agent = role + instructions + tools + permissions + context +
workflow.

---

## Agent Infrastructure

Decision:

Prefer mature agent protocols/infrastructure rather than building
an entire agent system from scratch.

ACP and compatible agent systems were investigated.

OpenCode is a possible initial backend.

---

## Plugins

Decision:

Optional integrations should live outside Vision Core whenever
practical.

Potential integrations:

- Obsidian
- Blender
- memory systems
- Ponytail
- future tools/services

Plugin failure should not break Vision Core.

---

## Obsidian

Decision:

Obsidian is an external knowledge/memory system.

The vault remains independent from Vision.

Future architecture:

Vision
→ Obsidian Plugin/Adapter
→ Obsidian
→ Knowledge / Memory

Removing the integration must not break Vision.

---

## Vision Orb

The Orb is part of Vision's identity.

It should eventually be:

- 3D
- floating
- animated
- state-driven
- isolated from model/provider logic

Reference implementation identified:

https://github.com/SAGAR-TAMANG/ultron-by-sagar-builds.git

The relevant Three.js techniques should be studied/adapted rather
than blindly importing the entire application.

---

## Hardware Neutrality

Hardware limitations must not become architectural limitations.

Hardware may influence:

- recommendations
- performance warnings
- runtime suggestions

Hardware must not permanently remove models from Vision.

The same Vision architecture should work across different hardware
and remote endpoints.

---

## Development Method

The project follows:

PLAN
→ APPROVE
→ IMPLEMENT
→ TEST
→ STOP

Every major implementation stage should leave Vision runnable.

---

## Current Development State

Completed:

- Step 1 — Foundation
- Step 2 — Design system
- Step 3 — IPC/security boundary
- Step 4 — Settings
- Step 5 — Application shell
- Step 6 — Chat UI

Current direction:

Continue building Vision incrementally while keeping the core
modular and stable.