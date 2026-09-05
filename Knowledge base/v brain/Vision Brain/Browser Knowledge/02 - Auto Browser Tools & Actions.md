---
type: note
domain: Browser Knowledge
created: 2026-09-04
---

# Auto Browser Tools & Actions

The tool surface Auto Browser exposes over MCP, and how to pick the right call. The design point:
a **compact, curated** set so an agent selects tools well.

Part of [[Browser Knowledge/00 - Browser Knowledge|Browser Knowledge]].

## Tool profiles — curated vs full

Auto Browser exposes two profiles, selected by the `MCP_TOOL_PROFILE` config key:

- **`curated`** *(default)* — a deliberately small surface, "to keep the browser surface compact
  for better tool selection". This is what an agent should use.
- **`full`** — adds background agent-run and convergence/harness tooling. Only for operator
  workflows that need it.

Prefer `curated`. A smaller tool surface measurably improves tool-choice accuracy; do not switch to
`full` unless a task genuinely needs the harness tools.

## Curated surface — the tools you act with

Exact names as the docs give them (`browser.*`), grouped by what they are for:

| Group | Tools / actions | Purpose |
| --- | --- | --- |
| **Session** | `browser.create_session`, `browser.save_auth_profile` | Start a session; persist auth state ([[Browser Knowledge/03 - Browser Sessions & Lifecycle\|note 03]]) |
| **Navigate & act** | session actions for **navigation, clicking, typing, scrolling** | Drive the page — go to a URL, click/type on an element, scroll |
| **Observe** | `browser.observe`, `browser.screenshot`, `browser.dom` | Read current state — combined observation, a screenshot, or the DOM structure ([[Browser Knowledge/04 - Observation & Element Grounding\|note 04]]) |
| **Find** | `browser.find_elements` | Locate elements by a `query` — plain text or regex, case-insensitive |
| **Diagnostics** | `browser.console`, `browser.network` | Read console output and inspect network activity |

## Full-profile additions (operator only)

- `browser.queue_agent_run`, `browser.resume_agent_job` — queue / resume background agent runs.
- `harness.start_convergence`, and read-only introspection: `harness.get_status`,
  `harness.get_trace`, `harness.list_runs`, `harness.list_candidates`, `harness.get_candidate`,
  `harness.graduate`.

These belong to Auto Browser's own agent/eval harness. Vision's orchestration is n8n
(`VISION — AGENTS`); **do not** wire Vision's control flow through the harness tools — treat them
as out of scope for normal browser tasks.

## The act loop with these tools

The intended perception→action→verification loop, in Auto Browser's own terms:

1. **Capture** — `browser.observe` (or `screenshot`/`dom`) tags interactables with **stable element
   ids**.
2. **Choose** — pick an `element_id`; if you don't have one, `browser.find_elements` with a text or
   regex `query`.
3. **Execute** — the navigation/click/type/scroll action against that element.
4. **Verify** — confirm via changed URL, title, focus, text, or DOM. Auto Browser itself derives
   action verification from before/after page signals; read that result rather than assuming
   ([[Browser Knowledge/05 - Navigation Downloads & Security|note 05]]).

The whole point of stable element ids is to stop the model *guessing* coordinates — ground on the
id, not the pixel.

> [!warning] Tool names are upstream, not yet Vision-verified
> The exact `browser.*` names below are read from Auto Browser's docs (`docs/mcp-clients.md`),
> which note the manifest is not fully exhaustive there. Confirm the live tool list from the
> running server (MCP `tools/list`) before hard-coding any name — the curated set is what the
> server advertises, and it is the authority.

> [!info] Provenance
> Tool profiles (`MCP_TOOL_PROFILE`: curated/full), the `browser.*` and `harness.*` tool names, and
> the act loop are **upstream capability** from the **Auto Browser** `docs/mcp-clients.md` and
> `docs/architecture.md` (MIT, © LvcidPsyche; ~v1.5.0), retrieved 2026-09-04. **Derived, not
> copied.** Not yet *Vision-verified*. Record:
> [[Browser Knowledge/99 - Sources & Provenance|Sources & Provenance]].
