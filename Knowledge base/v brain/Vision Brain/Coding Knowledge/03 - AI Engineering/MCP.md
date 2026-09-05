---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# MCP

The Model Context Protocol: how tools and context are exposed to a model, and what the protocol does and does not guarantee.

## What it is

An open protocol standardising how applications supply context and tools to language models. It
uses **JSON-RPC 2.0** messages between three roles:

- **Host** - the LLM application that initiates connections
- **Client** - a connector inside the host, one per server
- **Server** - a service exposing capabilities

The point is composability: any compliant client can use any compliant server, so an integration
is written once rather than once per application.

## Primitives

**Servers offer:**

| Primitive | Is | Controlled by |
| --- | --- | --- |
| **Tools** | Functions the model can invoke | The model chooses; the host must consent |
| **Resources** | Context and data to read | The application or the user |
| **Prompts** | Templated messages and workflows | The user |

**Clients offer:**

- **Elicitation** - a server may request additional information from the user.

Beyond the core there are opt-in **extensions**, negotiated at initialisation, including
**Tasks** (asynchronous long-running operations with polling and durable handles), **Skills over
MCP**, and **MCP Apps** (inline interactive UI).

## Transports

Exactly two standard bindings:

1. **stdio** - newline-delimited JSON-RPC over the standard streams of a client-launched
   subprocess. The default for local servers.
2. **Streamable HTTP** - each message is an HTTP POST to a single MCP endpoint; the reply is
   either a JSON object or a request-scoped SSE stream.

Custom transports are permitted but must preserve the message format, patterns and per-request
metadata model.

> [!note] Version-dependent, and it matters
> The 2026-07-28 revision is **stateless with per-request capability negotiation**, and servers
> do **not** initiate JSON-RPC requests. Earlier revisions used a connection-scoped `initialize`
> handshake and allowed server-initiated requests; implementations detect and fall back.
>
> Practically: **check which revision each side implements before debugging an integration.**
> A client written against the older session model talking to a newer stateless server is a
> confusing failure that looks like a transport bug.

## Security

The specification is explicit that MCP enables arbitrary data access and code execution, and
that it cannot enforce safety at the protocol level. The stated principles:

- Users must consent to and understand all data access and operations.
- Hosts must obtain explicit consent before exposing user data to servers, and before invoking
  any tool.
- **Tool descriptions and annotations must be treated as untrusted** unless the server is
  trusted.

That last point is the one engineers most often miss: **a tool's description is text from
another party that lands in the model's context**, and it can carry instructions. Curate the
tool surface; do not import a large server's entire catalogue unexamined.

## Practical guidance

- **Curate, don't import.** A server exposing 188 operations should not become 188 tools in your
  agent. Select the ones the task needs and deny the rest - fewer tools also improves selection
  accuracy. *(In this stack, 6 of Obsidian's 16 tools are enabled and the 10 mutating ones,
  including `command_execute`, are denied.)*
- **Deny by default**, especially anything that executes commands, writes, deletes or moves.
- **Watch for privilege loops.** A tool that lets one model approve another model's permission
  prompts destroys the entire permission boundary. *(Found and excluded during this project's
  OpenCode integration.)*
- **Authenticate remote servers**, and keep TLS verification on. A self-signed local certificate
  should be trusted explicitly (`NODE_EXTRA_CA_CERTS`), never bypassed.
- **Bound tool results.** An unbounded resource read will consume the context window.
- **Check host support.** Not every host implements every transport or extension - Open WebUI
  v0.11.3, for example, supports Streamable HTTP only.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Tool & Function Calling|Tool & Function Calling]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]
- [[Coding Knowledge/11 - Vision & OpenCode/MCP Integration Patterns|MCP Integration Patterns]]

## Sources

- Model Context Protocol specification, revision **2026-07-28** - <https://modelcontextprotocol.io/specification/latest> and <https://modelcontextprotocol.io/specification/2026-07-28/basic/transports> (repository MIT; fetched and verified 2026-09-03). The curation and privilege-loop observations are from this project.
