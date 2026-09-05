---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Tool & Function Calling

Giving a model the ability to act. The hard part is not the mechanism; it is the tool surface and the failure handling.

## The mechanism

You supply tool definitions - name, description, JSON Schema for parameters. The model may emit
a structured call instead of text. **Your code executes it** and returns the result as a tool
message; the model continues with that result in context.

Two facts follow immediately, and most bugs come from forgetting them:

1. **The model never executes anything.** It emits an intention. Every permission, validation
   and safety decision is yours, in your code.
2. **A tool call is untrusted input to your system**, because it may be influenced by anything
   in the context - including retrieved documents and web pages. Validate every argument as you
   would a request from the internet.

## Designing the tool surface

**Fewer, better tools.** Accuracy of selection degrades as the number of similar tools rises.
Twenty tools with overlapping descriptions produce worse behaviour than six clearly distinct
ones. This is the highest-leverage design decision available.

- **Descriptions are the interface.** The model chooses from the description, not the
  implementation. Say what it does, when to use it, when *not* to, and what it returns.
- **Name for the task, not the implementation**: `search_notes`, not `obsidian_api_v2_query`.
- **Flat, typed, constrained parameters.** Enums over free strings; required over optional;
  avoid deeply nested objects.
- **One tool, one job.** A tool with a `mode` parameter that changes its behaviour is several
  tools wearing a coat.
- **Return structured, bounded results.** A tool that can return 500 KB will destroy the context
  window. Truncate, paginate, and say that you did.
- **Make errors instructive.** `"No project path given. Pass an absolute path such as
  D:\projects\x"` lets the model recover; `"error"` produces a retry loop.

## Failure modes

| Failure | Cause | Mitigation |
| --- | --- | --- |
| Wrong tool chosen | Overlapping descriptions | Fewer tools, sharper boundaries |
| Invented arguments | Under-specified schema | Required fields, enums, strict validation |
| Loop calling the same tool | The result did not answer the need | Cap iterations; return a clear terminal error |
| Never calls the tool | Description does not match how the need is phrased | Mention the trigger phrasing in the description |
| Calls with stale data | Result cached or from an earlier turn | Include a timestamp in the result |
| Context blown by results | Unbounded tool output | Truncate and summarise at the boundary |
| Silent stall | Tool returned nothing at all | Always return something, even "no results" |
| Destructive call from injected text | Retrieved content told it to | Permission the tool, confirm side effects |

> [!warning] Never return an empty result to a caller that treats empty as "skip"
> Measured in this project: an n8n node emitting zero items causes every downstream node to be
> skipped, so the agent halted silently with the execution still marked *success*. The fix was a
> sentinel item. The general rule - **never return nothing where nothing means "stop"** - applies
> to any pipeline, not just n8n.

## Permissions

Classify every tool as **read**, **write** or **destructive**, and enforce that classification
in code, not in the prompt. A prompt instruction is a suggestion; an allowlist is a boundary.

Enforce **twice** where the cost of failure is high: once in the orchestrator, once in the
executor. In this stack, coding writes are constrained by the n8n `Resolve Project` allowlist
*and* independently by OpenCode's `external_directory: deny`.

## Agent loop versus plan-then-execute

- **Agent loop** - the model calls tools repeatedly until done. Flexible; can loop, drift and
  cost unboundedly. Requires a hard iteration cap and a budget.
- **Plan-then-execute** - the model produces a plan, code executes the steps deterministically,
  the model interprets the results. More predictable, cheaper, far easier to debug and audit.

This stack uses plan-then-execute for the n8n agents, originally because the provider rejected
LangChain's tool-result shape, but retained because the determinism proved more valuable than
the flexibility.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/MCP|MCP]]
- [[Coding Knowledge/03 - AI Engineering/Structured Outputs|Structured Outputs]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]
- [[Coding Knowledge/04 - Agent Engineering/Tool Selection|Tool Selection]]

## Sources

- Provider tool-calling documentation (OpenAI function calling, Anthropic tool use). Model Context Protocol specification - <https://modelcontextprotocol.io/> (MIT). The empty-result and tool-result-shape behaviours were measured in this project.
