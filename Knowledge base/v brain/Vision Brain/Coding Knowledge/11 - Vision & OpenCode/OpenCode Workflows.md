---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# OpenCode Workflows

How a coding request actually runs, and the boundary that keeps it safe.

## The path

```
Vision -> n8n MCP tool -> Coding Agent -> code_explain / code_edit
       -> Resolve Project (allowlist check)
       -> OpenCode HTTP  POST /session  then  POST /session/{id}/message
       -> OpenCode agent (vision-explain | vision-code)
       -> Obsidian MCP for standards
       -> Format Reply -> back up the chain
```

## The two agents

Defined in `%UserProfile%\.config\opencode\opencode.jsonc`. The interactive agents (`build`,
`plan`) are untouched - using OpenCode directly in its TUI keeps full capability.

| | `vision-explain` | `vision-code` |
| --- | --- | --- |
| Purpose | Read-only analysis | Scoped edits inside one project |
| `edit` | deny | allow |
| `bash` / `task` / `webfetch` / `websearch` | deny | deny |
| `external_directory` | deny | deny |
| Obsidian tools | 6 read-only enabled | 6 read-only enabled |
| Obsidian mutating tools | 10 denied, incl. `command_execute` | 10 denied |

Both prompts instruct the agent to **search the vault for documented standards first** and treat
the vault as authoritative - which is what makes
[[Coding Knowledge/00 - Coding Knowledge|this domain]] operative rather than decorative.

## Defence in depth on writes

Two independent enforcement points, deliberately:

1. **n8n `Resolve Project`** validates the absolute path against `ALLOWED_ROOTS`
   (`D:\vision-workspace`), rejects `..` outright rather than resolving it, and refuses
   anything outside. Vision's own model chooses the `project` argument, so this is the check
   that stops a crafted request aiming the agent elsewhere.
2. **OpenCode's own permission engine** enforces `external_directory: deny` independently. If
   the n8n wrapper is bypassed or misconfigured, OpenCode still refuses.

Neither alone is sufficient; that is the point.

## Server

`opencode serve --port 4096 --hostname 127.0.0.1`, started by `D:\opencode\opencode-launcher.ps1`
via a logon scheduled task with a 90-second delay. The launcher **refuses to start without
`OPENCODE_SERVER_PASSWORD`**, so the server is never exposed unauthenticated. HTTP Basic auth is
verified working: unauthenticated requests return 401.

`NODE_EXTRA_CA_CERTS` points at the exported Obsidian certificate so TLS verification stays on
for the local HTTPS API.

## API notes that cost time

- `POST /api/session/{id}/prompt` is **asynchronous** - it returns an admission receipt.
- `session.wait` returns **503** in 1.18.26.
- `POST /session/{id}/message` is **synchronous**, which removed the need for a polling loop.
  This is why the integration uses `message` rather than `prompt`.
- The OpenAPI schema is at `/doc` and contains **188 operations**. It is deliberately not
  imported - see [[Coding Knowledge/11 - Vision & OpenCode/MCP Integration Patterns|MCP Integration Patterns]].

## Reading the reply

`Format Reply` extracts `parts[].type == 'text'` and joins them. If no text is present, it
reports `finish` rather than returning a blank answer - anything other than `finish: "stop"`
usually means the run was cut off or errored, and surfacing that beats returning silence.

---

## See also

- [[Coding Knowledge/11 - Vision & OpenCode/MCP Integration Patterns|MCP Integration Patterns]]
- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]
- [[Coding Knowledge/04 - Agent Engineering/Sandboxing|Sandboxing]]

## Sources

- Configuration read from `%UserProfile%\.config\opencode\opencode.jsonc`, `D:\opencode\opencode-launcher.ps1` and `D:\n8n\workflows\vision-code-explain.json` on 2026-09-03. API behaviours recorded in `D:\opencode\README.md` from live testing against OpenCode 1.18.26.
