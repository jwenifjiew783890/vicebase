---
type: note
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Vision Engineering Constraints

The hard rules for any change inside the Vision stack. These are decisions already made; they are not open for re-litigation during a task.

> [!danger] The identity rule
> **`OPEN WEBUI = VISION`.** There is no separate Vision application, backend or core. Vision
> *is* a customised Open WebUI installation. The earlier Electron/React build is abandoned and
> must not be revived, referenced as current, or partially resurrected.

## Architectural constraints

| Constraint | Consequence for a task |
| --- | --- |
| Obsidian is the single source of knowledge truth | Never copy vault content into Open WebUI Knowledge, or into a second store "for retrieval" |
| Retrieval is on-demand and domain-scoped | No full-vault embedding or sync system |
| Coding runs through OpenCode | Do not build a coding engine inside Vision, and do not replace OpenCode |
| One Obsidian MCP server | The Obsidian plugin *is* the MCP server; no bridge, no second server |
| The n8n agent hierarchy is locked | Extend by registry entry, never by restructuring `VISION - AGENTS` |
| Open WebUI is a fork, not a rewrite | Prefer configuration and additive files; minimise diff against upstream |

## Operational constraints

- **Chat inference is remote** (NVIDIA `integrate.api.nvidia.com`). **Embedding and speech are
  local** (SentenceTransformers, Whisper) - "the models are remote" is only true of chat.
- **PersistentConfig**: for many settings Open WebUI stores the value in `webui.db` on first
  run, after which the environment variable is ignored. Changing env alone will appear to do
  nothing. Change it in the UI/DB, or clear the stored value.
- **Certificate verification stays on.** Obsidian's Local REST API is HTTPS with a self-signed
  certificate; trust it via `NODE_EXTRA_CA_CERTS`. Disabling verification is not an option.
- **Secrets live in their own store** - n8n's encrypted credentials, environment variables,
  the OpenCode password file. Never in prompts, workflow names, registry metadata, source
  files, or commits.
- **Never reset or recreate `webui.db`.** It holds the configuration, users, chats and the
  Obsidian MCP key.
- **Coding writes are confined** to the allow-listed project roots, enforced twice: in the n8n
  `Resolve Project` node and independently by OpenCode's `external_directory: deny`.

## Verification constraints

- **Static configuration is not proof.** A workflow that looks right has not run. Claim success
  only from a real execution with real output.
- **Report gaps.** If a step was skipped or a test not run, say so explicitly.

## Where the detail lives

This note is the summary an agent should carry by default. The reasoning, the exact versions
and the incident history are in
[[Coding Knowledge/11 - Vision & OpenCode/00 - Vision & OpenCode|section 11]] - in particular
[[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]] and
[[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]].

---

## See also

- [[Coding Knowledge/11 - Vision & OpenCode/Vision Architecture|Vision Architecture]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]
- [[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]]

## Sources

- This project. Decisions recorded in [[Memory/14 - Decisions & Principles/Decision Log|the Decision Log]] and `D:\n8n\workflows\AGENT-REGISTRY.md`; behaviours confirmed by running the system.
