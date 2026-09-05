---
type: note
domain: Browser Knowledge
created: 2026-09-04
---

# Auto Browser Architecture

What Vision's browser executor actually is, and how a client reaches it. Understanding the shape
prevents a lot of wrong assumptions about what you can and cannot do.

Part of [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]].

## What it is

**Auto Browser is an MCP-native browser control plane** — not a bare browser driver. Its own
description: a "shared Playwright browser with human takeover, reusable auth profiles, approvals,
audit trails, and local-first deployment" for MCP clients, LLM agents and operators. Two
components:

- **Controller service** (FastAPI, Python) — the *only* interface an LLM touches. It manages
  sessions, executes Playwright actions, enforces policy, captures screenshots, extracts
  interactable elements with **stable element ids**, saves/restores auth state, and exposes the
  unified API.
- **Browser node** — a container running Chromium plus `Xvfb`, `Fluxbox`, `x11vnc`, `noVNC`, and a
  Playwright server (port `9223`). Chromium is chosen for automation reproducibility.

The controller drives the browser via Playwright's `launchServer`/`connect`, **not** a raw
Chrome-DevTools-Protocol attach — a deliberate choice after Chrome tightened remote-debugging in
early 2025. So think "Playwright semantics", not "CDP".

## How a client reaches it

| Transport | Address / command | Use |
| --- | --- | --- |
| **MCP over HTTP** | `http://127.0.0.1:8000/mcp` | The primary path — session-aware JSON-RPC, curated tool profile |
| **Stdio bridge** | `uvx auto-browser-mcp` | Local MCP clients that speak stdio |
| **REST** | controller API | Optional built-in agent runner (OpenAI / Claude / Gemini) |
| **Reverse-SSH** | per-session tunnels | Isolated human-takeover URLs |

## Local-first / loopback binding

**All published ports bind to `127.0.0.1` by default.** Nothing is exposed off-host unless an
operator explicitly opts into an `unsafe-public` mode. This is the security spine of the whole
system: the browser control plane is a loopback service on the user's machine, not a network
service. Treat any suggestion to bind it publicly as a decision for the user, never a default.

## How Vision would connect

Auto Browser fits Vision's existing pattern exactly: it is a **Streamable-HTTP MCP server on
loopback** (`http://127.0.0.1:8000/mcp`) — the same transport class Open WebUI already uses for the
Obsidian and n8n MCP servers ([[Integrations/00 - Integrations|Integrations]]). So the integration
mechanism is "register another MCP tool server", not "build a bridge". Heavy executors follow the
OFF → TASK → OFF rule
([[Agents/Self-Improving Agent Layer — Requirements|Requirements]]).

> [!warning] Not yet integration-tested by Vision
> The above is **upstream capability** from the Auto Browser repo/docs. Vision has **not** yet
> registered or driven Auto Browser end-to-end, so none of the connection details are
> *Vision-verified*. Confirm the port, transport (Streamable HTTP vs. SSE), and TLS behaviour on
> this machine before relying on them — the same care that the Obsidian MCP integration needed.

## How to reason about it

- It is a **control plane with a lock**, not a raw browser: expect one active session per node in
  the base setup, sequential actions, and policy checks between you and the page.
- It speaks **Playwright**, so element/selector behaviour and navigation semantics follow
  Playwright, not CDP.
- It is **loopback and local-first** — capabilities like human takeover (noVNC) and audit are
  built in, not bolted on.

> [!info] Provenance
> Architecture, components, ports, transports and loopback binding are **upstream capability** from
> the **Auto Browser** repository and `docs/architecture.md` (MIT, © LvcidPsyche; ~v1.5.0),
> retrieved 2026-09-04. **Derived, not copied.** The "fits Vision's MCP pattern" note is our
> reasoning, not an upstream claim, and is explicitly *not yet Vision-verified*. Record:
> [[Browser Knowledge/99 - Sources & Provenance|Sources & Provenance]].
