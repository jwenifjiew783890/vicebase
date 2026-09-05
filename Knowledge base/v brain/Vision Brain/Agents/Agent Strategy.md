# Vision Agent Strategy

## Core Principle

An agent is a worker operating through controlled capabilities.

An agent is not Vision Core.

## Model vs Agent

Model:
Provides reasoning/intelligence.

Agent:
Provides:

- role
- instructions
- tools
- permissions
- context
- task state
- workflow

## Initial Agent

A lightweight Hermes-based agent may be used first to validate the
architecture.

## Future Agents

Potential roles:

- Coding
- Planning
- Research
- Debugging
- Testing
- Project analysis
- Task execution
- Automation

## Coding

Future coding models may include:

- DeepSeek
- Qwen
- other strong coding models

## Infrastructure

Prefer mature agent infrastructure/protocols such as ACP rather than
building an entire agent runtime from zero.

## Security

Agents must use controlled filesystem, terminal and plugin capabilities.

Agent-generated actions should have appropriate approval/permission
controls.

## UI Principle

Agents should appear naturally inside the work being performed.

Do not make Vision primarily an "agent dashboard."