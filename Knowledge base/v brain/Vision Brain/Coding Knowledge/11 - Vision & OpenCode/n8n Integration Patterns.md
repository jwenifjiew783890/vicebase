---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# n8n Integration Patterns

The orchestration layer: how it is structured, and the sharp edges that have already drawn blood.

## Structure

The hierarchy is **locked**. Extend it by adding a registry entry, never by restructuring.

```
VISION
  -> VISION HUB              MCP surface, /mcp/vision
  -> VISION - AGENTS         orchestrator + generated architecture map
  -> agent type              Research | Coding | Business | Monitoring | Content
  -> capability              or an external executor (OpenCode)
  -> result
```

**`agent-registry.json` is the single source of truth.** It holds agents, capabilities, input
and output schemas, permissions, knowledge domains, `enabled` state and the MCP surface. The hub
reads it; the architecture sticky notes on the canvas are **generated** from it, so the picture
cannot drift from the system.

Verified property: registering a new agent left the hub workflow at **exactly the same node
count**, because the hub reads the registry rather than encoding the agents.

`enabled: false` keeps a FUTURE slot out of the router and out of the dispatcher allowlist, so it
cannot be called. That is a security property as well as an organisational one.

## Sharp edges - all measured here

> [!warning] Error text is truncated at the last colon
> A thrown sub-workflow error reaches the caller as **only the text after the last colon**. A
> message containing `D:\path\...` therefore arrives as a meaningless fragment. **Keep thrown
> messages colon-free.**

> [!warning] `error: null` is success
> A successful sub-workflow returns `error: null`, so testing `error === undefined` scores
> **every success as a failure**. Use an explicit non-null check.

> [!warning] A node emitting zero items skips everything downstream
> Every step still reports **success**, and the agent halts silently. A slow Obsidian once made
> the folder listing time out and the research agent stopped dead with no error anywhere.
> **Return a sentinel item rather than nothing** whenever downstream must continue.

> [!warning] `$json` at a prompt node is the previous node's output
> Not the workflow input. In a multi-hop capability, reading `$json.knowledge` renders empty with
> no error and the retrieved standards silently vanish. **Read from the named trigger** -
> `$('When Executed by Another Workflow').first().json.knowledge` - which is correct in both
> single-hop and multi-hop shapes.

> [!warning] `SplitInBatches` v3 outputs are `['done', 'loop']` - done is index 0
> Its done output carries **one item per iteration**, each holding the accumulator as it stood
> then. `.first()` reports only stage 1 of a multi-stage run; take the fullest snapshot.

Also:

- **Sub-workflows must be published**, not merely imported; re-importing deactivates them.
- `publish:workflow` via PowerShell's `&` returns 255 and silently does nothing - run it from
  bash. `Stop-N8n.ps1` from bash needs `-ExecutionPolicy Bypass`.
- **An import against a running n8n does not take effect.**
- The Code node sandbox has **no `fetch`** - use `this.helpers.httpRequest`.
- There is **no `delete:workflow` CLI command**; deleting needs the REST API, or a database
  delete with `PRAGMA foreign_keys=ON` (most children cascade, `workflow_statistics` does not).

## Model nodes

`responsesApiEnabled: false` on **every** model node - NVIDIA does not implement the Responses
API and the failure mode is a silent zero-token reply rather than an error.

Every `lmChatOpenAi` node carries `timeout: 60000` and `maxRetries: 1`. Unbounded, one degraded
provider hung a call for **302 seconds**, and a retry was still hanging past ten minutes. Bounded,
the worst case is a clean failure the hub reports honestly.

## Knowledge injection

Capabilities take an optional `knowledge` input, filled by the Knowledge Retriever. The prefix
wording is load-bearing: a soft "please follow the standards" preamble was **ignored**, because
each capability's own prompt says "write markdown with exactly these sections". Only explicit
precedence - *these OUTRANK everything that follows, including any list of required sections* -
made it effective.

**A knowledge layer that the executor's own boilerplate can override is not a knowledge layer.**

## Operational

`EXECUTIONS_DATA_PRUNE=true`, `EXECUTIONS_DATA_MAX_AGE=168` (hours),
`EXECUTIONS_DATA_PRUNE_MAX_COUNT=500`, `N8N_LOG_LEVEL=warn` - set in `D:\n8n\n8n-env.ps1` to
bound execution-history growth.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Orchestrators|Orchestrators]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]]
- [[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]]

## Sources

- All items measured in this project and recorded in `D:\n8n\workflows\AGENT-REGISTRY.md`, `_generate.py`, `_generate_hub.py` and the workflow JSON. n8n 2.37.7, verified 2026-09-03.
