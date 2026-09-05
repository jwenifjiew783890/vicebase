---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Vision Architecture

The components, their addresses, and the path a request actually takes.

> [!danger] The identity rule
> **`OPEN WEBUI = VISION`.** There is no separate Vision application, backend or core. The
> earlier Electron/React build is abandoned and must not be revived or referred to as current.

## The chain

```
Vision (Open WebUI)
  |-- MCP Streamable HTTP --> n8n  /mcp/vision        curated tool surface, bearer auth
  |                             |
  |                             |-- VISION - AGENTS (orchestrator)
  |                             |     |-- Research / Business / Monitoring / Content  (n8n capabilities)
  |                             |     '-- Coding --HTTP--> OpenCode server
  |                             |                              |
  |                             |                              '-- MCP --> Obsidian Local REST API
  |                             '-- Knowledge Retriever --------------------------> (same API)
  '-- local models: SentenceTransformers (embedding), Whisper (speech)
```

## Verified running state

Measured 2026-09-03.

| Component | Address | Process | Health |
| --- | --- | --- | --- |
| Vision / Open WebUI | `http://127.0.0.1:8080` | `pythonw` | 200 |
| n8n | `http://127.0.0.1:5678` | `node`, **native npm install** | 200 |
| OpenCode server | `http://127.0.0.1:4096` | `opencode` | 401 (Basic auth on - correct) |
| Obsidian Local REST API | `https://127.0.0.1:27124` | Obsidian plugin | 200 |
| SearXNG | container | Docker | **down - Docker daemon not running** |

> [!note] Correction worth recording
> **n8n does not run in Docker here.** It is installed via npm and runs as a Node process
> (`%AppData%\npm\node_modules\n8n`). Docker is used for SearXNG, not for n8n - so Docker
> being stopped does not stop the agent layer. This contradicts an earlier assumption in this
> project, and the measurement is what settles it.

Versions in use: Open WebUI **0.11.3**, n8n **2.37.7**, OpenCode **1.18.26**, WSL **2.7.12**.

## Where inference happens

- **Chat reasoning: remote.** NVIDIA `integrate.api.nvidia.com`, model `openai/gpt-oss-120b`.
- **Embedding: local.** Open WebUI's `rag.embedding_engine=""` means SentenceTransformers in
  process (`all-MiniLM-L6-v2`, 931.7 MB cached).
- **Speech: local.** `whisper-large-v3-turbo`, 1,547.3 MB cached. Torch adds ~536 MB.

"The models run remotely" is true only of chat. This distinction has already caused one
misdiagnosis of memory use.

## Data

- **`webui.db`** holds Open WebUI's configuration, users, chats and the Obsidian MCP key.
  **Never reset or recreate it.**
- **`D:\v brain\Vision Brain`** is the Obsidian vault - the knowledge source of truth.
- **`D:\n8n\workflows`** holds the workflow JSON and `agent-registry.json`.
- **n8n credentials** live in n8n's own encrypted store, nowhere else.

## The rules this shape encodes

1. Obsidian is the single knowledge source. Nothing is copied into Open WebUI Knowledge.
2. Retrieval is on demand and domain-scoped. No full-vault embedding.
3. Coding goes through OpenCode. No coding engine inside Vision, and OpenCode is not replaced.
4. One Obsidian MCP server - the plugin itself. No bridge, no second server.
5. The n8n agent hierarchy is locked; extend it by registry entry.
6. Open WebUI is a fork; prefer configuration and additive files over divergence from upstream.

---

## See also

- [[Coding Knowledge/04 - Vision Engineering Constraints|Vision Engineering Constraints]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]
- [[Coding Knowledge/11 - Vision & OpenCode/n8n Integration Patterns|n8n Integration Patterns]]

## Sources

- Measured on this machine 2026-09-03: listening ports, process list, and HTTP health checks. Architecture recorded in `D:\opencode\README.md` and `D:\n8n\workflows\AGENT-REGISTRY.md`.
