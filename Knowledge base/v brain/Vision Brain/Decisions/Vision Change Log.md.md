# Vision Change Log

## Why this exists

This file records important architectural changes and why they
happened.

## Rule

When a major architecture decision changes, record:

- Date
- Decision
- Previous approach
- New approach
- Reason
- Consequences

## Current principle

Do not silently change foundational architecture.

Review → approve → implement.

---

## Early Evolution

### Code Workspace

Initial interpretation:
Traditional code editor/workspace.

Corrected interpretation:
Claude Code-style AI coding agent workspace.

Reason:
The primary goal is an AI agent operating on a real local project,
not building another IDE.

---

### Orb

Initial approach:
Create a procedural orb from scratch.

Updated approach:
Study/adapt the existing SAGAR-TAMANG Three.js orb implementation
while keeping Vision's own architecture and identity.

Reason:
Reuse mature work instead of unnecessarily rebuilding complex
visual infrastructure.

---

### Model Architecture

Initial:
Ollama-first thinking.

Final direction:
Provider/runtime abstraction supporting local runtimes, API
providers, remote endpoints and future inference strategies.

Reason:
Prevent Vision from becoming an Ollama-only application.