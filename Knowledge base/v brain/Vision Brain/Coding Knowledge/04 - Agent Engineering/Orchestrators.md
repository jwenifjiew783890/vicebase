---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Orchestrators

The component that routes a request to the right capability and owns the contract with everything above it.

## What an orchestrator is responsible for

1. **Routing** - which agent, which capability.
2. **Validation** - is this request permitted, are the required arguments present.
3. **Invocation** - call the capability with a well-formed input.
4. **Result shaping** - one consistent output contract regardless of which capability ran.
5. **Error surfacing** - a failure below must arrive above as a usable message, not a fragment.

It should **not** contain business logic for any particular capability. The moment the
orchestrator knows how research differs from coding, it has become a monolith and every new
agent requires editing it.

## The registry pattern

Keep a **machine-readable registry** as the single source of truth: agents, their capabilities,
input and output schemas, permissions, knowledge domains, enabled state. The orchestrator reads
it; documentation and diagrams are generated from it.

This buys three things:

- **Adding an agent is a data change**, not a code change.
- **Documentation cannot drift**, because it is generated.
- **The allowlist is explicit** - a disabled entry cannot be called, which is a security property
  as well as an organisational one.

*Verified in this stack: registering a new agent left the hub workflow at exactly the same node
count, because the hub reads the registry rather than encoding the agents.*

## Routing

Prefer **deterministic routing** on a declared task type or an explicit capability name. Use a
model to route only when the request is natural language and the mapping is genuinely
ambiguous - and then validate its choice against the registry before acting on it, because a
model asked to pick from a list will occasionally invent an item.

## Contracts

- **One output shape** for every capability: `{ok, agent_id, tool_id, result, error}` or
  similar. Callers should not need to know which capability ran.
- **Every field the caller depends on is always present**, even when empty.
- **Errors are structured**, with a stable code and a human message.

## Error propagation is harder than it looks

An error thrown deep in a sub-workflow has to survive every layer above it. Layers routinely
truncate, re-wrap, or swallow.

> [!warning] Measured in this project
> A thrown sub-workflow error reaches the caller as **only the text after the last colon**. An
> error message containing `D:\path\...` therefore arrived as a meaningless fragment, with the
> explanation discarded. Thrown messages are now written colon-free.
>
> Separately: a successful sub-workflow returns `error: null`, so testing `error === undefined`
> scored **every success as a failure**. Explicit non-null checks are required.

Both are examples of the general rule: **verify how an error actually arrives at the top, by
causing one**, rather than assuming the framework preserves it.

## Failure modes

- **Orchestrator that knows every agent's internals.** Every addition edits it.
- **Silent skip.** A stage producing nothing causes downstream to be skipped while every step
  reports success. Emit a sentinel instead of nothing.
- **Inconsistent output shapes** forcing callers to special-case.
- **Errors flattened to "failed"**, discarding the cause.
- **No timeout at the orchestrator level.** One hung capability hangs the whole system.
- **Registry and implementation drifting** because the registry is documentation rather than the
  thing actually read.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Planners|Planners]]
- [[Coding Knowledge/04 - Agent Engineering/Failure Recovery|Failure Recovery]]
- [[Coding Knowledge/11 - Vision & OpenCode/n8n Integration Patterns|n8n Integration Patterns]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- Measured in this project. The registry design and its verification are recorded in `D:\n8n\workflows\AGENT-REGISTRY.md` and `agent-registry.json`.
