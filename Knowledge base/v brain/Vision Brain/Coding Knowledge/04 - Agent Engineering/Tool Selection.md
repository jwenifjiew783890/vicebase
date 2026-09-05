---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Tool Selection

Making the right tool the obvious one. Most tool-choice failures are design failures, not model failures.

## The dominant factor is the size and clarity of the surface

Selection accuracy falls as the number of similar tools rises. Six clearly distinct tools
outperform twenty overlapping ones by a wide margin, regardless of model.

So the first move when tool selection is unreliable is **not** a better prompt or a better
model - it is to **remove or merge tools**.

## Designing for selection

- **Distinct purposes.** If two tools could plausibly answer the same request, either merge them
  or make their descriptions state the boundary explicitly: "use X for a single note, Y for a
  search across notes".
- **Descriptions carry the decision.** Say what it does, **when to use it**, **when not to**,
  what it needs, and what it returns. The "when not to" line is the most under-used and most
  effective part.
- **Name for intent**, not implementation: `search_notes` beats `obsidian_rest_query_v2`.
- **Constrain parameters.** Enums, required fields and clear types eliminate invented arguments.
- **Make errors instructive.** A tool that returns "No project path given. Pass an absolute path
  such as `D:\projects\x`" gets a correct retry; one returning "error" gets a loop.
- **Return bounded, structured results** including whether anything was found. An empty result
  must be explicit, not silent.

## Curation over import

Automatically importing an entire API surface produces dozens or hundreds of tools, most of them
irrelevant, several of them dangerous, all of them competing for the model's attention.

> [!note] Measured in this project
> Importing OpenCode's OpenAPI surface directly would have produced 188 operations - including
> `permission.reply`, which would have let Vision's model approve OpenCode's own permission
> prompts and dissolve the entire boundary. The surface was curated instead: two scoped agents,
> six of Obsidian's sixteen tools enabled, ten mutating ones denied.

**Rule: expose the tools the task needs, deny the rest, and re-examine the list whenever a
dependency updates.**

## Diagnosing selection failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Picks the wrong tool | Overlapping descriptions | Merge, or state the boundary |
| Never uses a tool | Description does not match the user's phrasing | Add the trigger phrasing |
| Calls repeatedly | The result did not answer the need | Better result content; cap iterations |
| Invents arguments | Loose schema | Enums, required fields, validation |
| Uses a tool for everything | One tool is too general | Split it |
| Ignores tools, answers from memory | No instruction to prefer tools | Say so explicitly |

## Ordering and defaults

- **Put the most commonly correct tool first** in the list; order has a small but real effect.
- **Provide a default path.** If there is an obvious first step - search before read - say so in
  the system prompt rather than hoping.
- **Do not expose a tool that is usually wrong.** Its presence costs accuracy on every request.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Tool & Function Calling|Tool & Function Calling]]
- [[Coding Knowledge/03 - AI Engineering/MCP|MCP]]
- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]

## Sources

- Provider tool-use documentation; MCP specification on untrusted tool descriptions - <https://modelcontextprotocol.io/specification/latest> (MIT). The 188-operation and curation findings were measured in this project.
