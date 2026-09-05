---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Known Constraints

Hard limits of the components in use. Working against one of these wastes a task; knowing it saves the attempt.

## Open WebUI 0.11.3

- **PersistentConfig**: many settings are stored in `webui.db` on first run, after which the
  environment variable is **ignored**. Changing env alone appears to do nothing. Change it in
  the UI or the database, or clear the stored value.
- **MCP: Streamable HTTP only.** No stdio transport.
- **Embedding is local by default.** `rag.embedding_engine=""` means SentenceTransformers in
  process, not a remote API.
- **`rag.embedding_batch_size=1`** by default - correct for memory, slow for bulk ingestion.
- It is a **fork**. Prefer configuration and additive files; every divergence from upstream is a
  merge cost later.

## NVIDIA GPT-OSS endpoint

- **Does not implement the Responses API.** `responsesApiEnabled: false` is required; the
  failure mode is a silent zero-token reply, not an error.
- **Rejects LangChain's tool-result message shape** with
  `content.0 Input should be a valid dictionary or instance of Content`. This is why the agents
  are plan-then-execute rather than a tool loop.
- **Free tier**: subject to rate limits and outages. It has returned 504s. Every model node must
  be bounded (`timeout: 60000`, `maxRetries: 1`).
- **Single point of failure.** Every n8n agent routes here. Documented, not mitigated.

## n8n 2.37.7

- Errors thrown from a sub-workflow are truncated to **the text after the last colon**.
- A successful sub-workflow returns **`error: null`**, not `undefined`.
- A node emitting **zero items causes every downstream node to be skipped**, with the execution
  still marked success.
- `$json` at a node is the **previous node's output**, which is not the workflow input in a
  multi-hop flow.
- `SplitInBatches` v3: outputs are `['done', 'loop']`, **done is index 0**, and done carries one
  item per iteration.
- The Code sandbox has **no `fetch`** - use `this.helpers.httpRequest`.
- **No `delete:workflow` CLI command.**
- Sub-workflows must be **published**; re-importing deactivates them, and an import against a
  running n8n does not take effect.
- `publish:workflow` via PowerShell's `&` returns 255 silently - run it from bash.

## OpenCode 1.18.26

- `POST /api/session/{id}/prompt` is **asynchronous**; `session.wait` returns **503**.
  `POST /session/{id}/message` is **synchronous** - use that.
- The OpenAPI schema at `/doc` has **188 operations**, several of them dangerous
  (`permission.reply`, `credential.remove`, `config.update`). It is not imported.
- The server has **no authentication unless a password is set** - the launcher refuses to start
  without `OPENCODE_SERVER_PASSWORD` for exactly this reason.

## Obsidian Local REST API

- **HTTPS with a self-signed certificate.** Trust the CA (`NODE_EXTRA_CA_CERTS`); do not disable
  verification.
- Returns a note as **plain markdown**, so n8n wraps it as `{data: "..."}` - `content` appears
  only for JSON responses.
- Can be **slow enough to time out** on a folder listing; the retriever uses a 45-second timeout
  and a sentinel so a slow response cannot halt an agent.
- Exposes **16 MCP tools**, 10 of them mutating. Six read-only ones are enabled.

## Knowledge Retriever

- **Top-level listing only** - subfolders are skipped.
- **6 notes** maximum per domain, in listing order.
- **6,000 characters** maximum assembled.
- **No relevance ranking** - `query` is accepted but unused.

## Windows / WSL / Docker

- **PowerShell 5.1**: no `&&`/`||`, no ternary, no `??`, no `ConvertFrom-Json -AsHashtable`.
  `2>&1` on a native executable sets `$?` to false even on exit code 0.
- **CIM vs Get-Process type mismatch**: `Win32_Process.ProcessId` is `UInt32`,
  `Get-Process.Id` is `Int32`. Joining them without a cast silently drops processes.
- **`.wslconfig` requires `wsl --shutdown`** to take effect.
- **Docker is not required for n8n here** - n8n runs natively via npm. Docker hosts SearXNG.
- **Do not force-kill Docker Desktop**; it leaves a stale socket and a long recovery.

---

## See also

- [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]]
- [[Coding Knowledge/11 - Vision & OpenCode/n8n Integration Patterns|n8n Integration Patterns]]
- [[Coding Knowledge/04 - Vision Engineering Constraints|Vision Engineering Constraints]]

## Sources

- Every item measured in this project during 2026-09-03 work, and recorded in `D:\n8n\workflows\AGENT-REGISTRY.md`, `D:\opencode\README.md`, and the workflow source. Versions: Open WebUI 0.11.3, n8n 2.37.7, OpenCode 1.18.26, WSL 2.7.12.
