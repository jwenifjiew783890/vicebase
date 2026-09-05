---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Permissions

Deciding what an agent may do, and enforcing it somewhere the model cannot reach.

## The first principle

**A permission enforced in a prompt is not a permission.** The model can be argued with,
confused, or instructed by content it reads. Enforcement belongs in code, in a layer the model
cannot influence.

The prompt should still state the boundary - it improves behaviour and produces better refusals -
but it is documentation of the constraint, never the constraint itself.

## Classify every capability

| Class | Examples | Default |
| --- | --- | --- |
| **Read** | List, search, fetch | Allow within scope |
| **Write** | Create, edit, upload | Allow within a narrow scope, only where required |
| **Destructive** | Delete, overwrite, move | Deny; require explicit confirmation |
| **Execute** | Shell, eval, arbitrary code | Deny by default |
| **External** | Send, publish, pay, deploy | Deny; require confirmation |
| **Meta** | Change permissions, approve prompts | Never grant |

That last row is absolute. A tool allowing a model to approve permission requests dissolves the
entire model. *(Found and excluded in this project: OpenCode's `permission.reply` operation
would have let Vision's model approve OpenCode's own prompts.)*

## Scoping

- **Directory scope** for file access - one project root, with traversal rejected outright
  rather than resolved. No legitimate path contains `..`.
- **Host allowlist** for network access.
- **Record and column scope** for data access, not just table.
- **Time and budget scope**: a maximum number of actions, tokens or minutes.

## Defence in depth

Enforce independently at more than one layer, so a single misconfiguration is not sufficient.

*In this stack: the n8n `Resolve Project` node validates the path against an allowlist, and
OpenCode independently enforces `external_directory: deny`, `bash: deny`, `task: deny`,
`webfetch: deny` in its own permission engine. Bypassing the n8n wrapper does not widen what
OpenCode will do.*

The comment in that node records the reasoning: Vision's own model chooses the project argument,
so that check is what stops a crafted request from aiming the coding agent at an arbitrary
directory.

## Confirmation

Require a human decision for: destructive operations, anything outbound (send, publish, pay,
deploy), anything outside the normal scope, and anything triggered by content the agent read
rather than by the user's own request.

Confirmation must present **what will actually happen** - the specific file, the specific
recipient, the specific amount - not a category. "Approve file operations?" is not consent.

## Auditing

Log every permission decision: what was requested, by which agent, allowed or denied, and why.
Denials are the more interesting half - a rise in denials is either a misconfigured agent or an
injection attempt, and both are worth knowing about.

## Failure modes

- **Prompt-only enforcement.**
- **Over-broad grants** made for convenience during development and never narrowed.
- **A single enforcement point**, so one bug is a full escape.
- **Path traversal resolved rather than rejected.**
- **Permission-granting tools** in the toolset.
- **Confirmation fatigue** - so many prompts that everything is approved reflexively. Ask rarely
  and meaningfully.
- **Denials not logged**, so an attack leaves no trace.

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Sandboxing|Sandboxing]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]
- [[Coding Knowledge/04 - Agent Engineering/Tool Selection|Tool Selection]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]

## Sources

- MCP specification on consent and tool safety - <https://modelcontextprotocol.io/specification/latest> (MIT). The dual-enforcement design and the `permission.reply` exclusion are from this project.
