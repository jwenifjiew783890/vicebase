# Vision Architecture

## Product Definition

Vision is a local-first AI platform designed to provide a unified,
premium desktop experience for AI conversation, coding, local models,
agents, tools, projects, terminal workflows and external integrations.

Vision is the product.

Underlying models, runtimes, agents and plugins are replaceable
components.

---

## Primary Experiences

### Chat

A premium Claude-like conversational experience.

Planned capabilities:

- Conversations
- Model selection
- Streaming
- Markdown
- Code
- Reasoning
- Files
- Attachments
- Images
- Image generation
- Future tools
- Future agents

### Code

A Claude Code-style AI coding workspace.

It is NOT intended to be a traditional IDE or a VS Code clone.

The goal is for an AI coding agent to work directly on a user's real
local project.

Future workflow:

Select project
→ select coding model/agent
→ describe task
→ inspect project
→ plan
→ modify files
→ execute commands
→ test
→ inspect errors
→ fix
→ iterate
→ explain changes

---

## Core Architecture

Vision Core should remain stable.

Core responsibilities include:

- Application shell
- UI
- Secure IPC
- Settings
- Project/session infrastructure
- Model/provider abstractions
- Terminal infrastructure
- Filesystem infrastructure
- Agent integration boundary
- Plugin boundary
- Orb integration boundary
- Security and permissions

Optional functionality should be isolated behind clear interfaces.

---

## Body vs Engine

### Body

- UI
- Chat
- Code workspace
- Projects
- Models
- Terminal
- Settings
- Plugin interface
- Orb

### Engine

- Model inference
- Providers
- Runtimes
- Agents
- Tools
- Memory
- Web
- Image generation
- External integrations

The body should be usable and testable independently of specific AI
engines.

---

## Model Architecture

The system must separate:

- Model
- Provider
- Runtime
- Endpoint
- Credential
- Capabilities

Vision must not be locked to one model or runtime.

Potential runtimes/providers include:

- Ollama
- llama.cpp
- vLLM
- LM Studio
- OpenAI-compatible APIs
- NVIDIA-hosted APIs
- custom endpoints
- future runtimes

Models are dynamically discoverable/configurable.

---

## Hardware Neutrality

Hardware is an advisory runtime input.

It may affect:

- recommendations
- performance estimates
- warnings
- runtime suggestions

It must NOT:

- remove models from the catalog
- permanently mark models unsupported
- prevent users from attempting models
- become part of the model definition

The same Vision architecture should work across different hardware,
including local, remote and cloud environments.

---

## Terminal

Vision will contain a real Windows terminal.

It should support:

- PowerShell
- CMD
- real command execution
- streaming output
- interactive processes
- command history
- multiple sessions

The terminal will eventually be used for:

- development
- runtime management
- model installation
- AI infrastructure management
- coding-agent execution

The terminal is general-purpose infrastructure, not merely a model
installer.

---

## Agents

Agents are workers operating through controlled capabilities.

Model:
Provides intelligence.

Agent:
Provides role, instructions, tools, permissions, context and workflow.

Potential roles:

- Coding
- Planning
- Research
- Debugging
- Testing
- Project analysis
- Task execution
- Automation

Agents should not become the primary application navigation.

---

## Plugins

Optional capabilities should be implemented as plugins where practical.

Potential integrations:

- Obsidian
- Blender
- Memory systems
- Ponytail
- Future tools
- External applications

Plugin failure must not break Vision Core.

Plugins must have controlled permissions and capability boundaries.

---

## Obsidian

Obsidian is an external knowledge/memory system.

It is not part of Vision Core.

Future architecture:

Vision
→ Obsidian Plugin/Adapter
→ Obsidian
→ Knowledge / Memory

The Obsidian vault remains independently usable.

---

## Orb

The Vision Orb is part of the product identity.

It should eventually be:

- 3D
- floating
- animated
- state-driven
- isolated from model/provider logic

Target states:

- Idle
- Listening
- Thinking
- Responding
- Generating
- Error

Reference implementation:

https://github.com/SAGAR-TAMANG/ultron-by-sagar-builds.git

Only relevant orb techniques should be adapted.

---

## Security

Vision must maintain strict boundaries between:

- Renderer
- Main process
- Filesystem
- Terminal
- Models
- Agents
- Plugins
- Credentials

API keys and secrets must remain protected.

AI-generated commands/actions require appropriate permission controls.

---

## Development Principle

PLAN → APPROVE → IMPLEMENT → TEST → STOP

Vision must remain runnable after every major implementation step.

Never implement large amounts of backend infrastructure without
proving the application runs.