---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Multi-Agent Systems

When splitting work across agents helps, and the much more common case where it multiplies cost and failure.

## Start from scepticism

Every additional agent adds a model call, latency, cost, a context boundary where information is
lost, and a new failure mode. The default answer to "should this be two agents?" is **no**.

Ask what the second agent can do that a second *step* cannot. If the answer is "nothing, but it
feels tidier", it is one agent with two steps.

## When it genuinely helps

- **Different permissions.** A read-only analyst and a write-capable editor is a *security*
  boundary, and that is a real reason.
- **Different context needs.** One agent needs the codebase, another needs the vault. Splitting
  keeps each context small and relevant.
- **Different models.** A cheap classifier and an expensive reasoner.
- **Genuine parallelism.** Independent subtasks that can run simultaneously.
- **Independent review.** A checker that has not seen the generator's reasoning catches things
  the generator will not - this is the one case where duplication is the point.

## Topologies

| Shape | Description | Notes |
| --- | --- | --- |
| **Hub and spoke** | One orchestrator calls specialists | The default. Predictable, debuggable |
| **Pipeline** | Fixed sequence, each stage transforms | Simplest; use whenever the order is fixed |
| **Hierarchy** | Orchestrators owning sub-orchestrators | Only when the domain is genuinely deep |
| **Peer-to-peer** | Agents calling each other freely | Avoid. Untraceable, prone to loops |
| **Blackboard** | Shared state, agents read and write | Needs strict ownership rules or it corrupts |

**Hub and spoke with a registry** is the shape that stays maintainable. Peer-to-peer looks
elegant and produces systems nobody can debug.

## Information loss at boundaries

Every handoff serialises context to text and loses everything not written down. Agent B does not
know what A tried, what it rejected, or why. So:

- **Pass structured state, not prose summaries**, where possible.
- **Include what was already attempted and failed**, or B repeats it.
- **Keep the original request** in every handoff. Losing the goal is the classic multi-agent
  failure - each agent optimises its local step while the overall task drifts.

## Cost and latency

Costs multiply, not add: three agents each making two model calls is six calls, each with full
context. A multi-agent system is routinely 5-10x the cost of a well-written single agent doing
the same work.

Latency is worse, because the calls are usually sequential. Parallelise where the subtasks are
genuinely independent, and measure whether the split paid for itself.

## Failure modes

- **Agents for organisational neatness** rather than capability.
- **Loops** - A delegates to B, B delegates back. Enforce a call-depth limit.
- **Diffused responsibility.** Each agent does its part correctly and the whole answers the wrong
  question.
- **Lost goal** across handoffs.
- **Untraceable execution.** Without a correlation ID through every agent, debugging is guesswork.
- **Cascading failure.** One specialist fails, the orchestrator misreports it as success. See
  [[Coding Knowledge/04 - Agent Engineering/Failure Recovery|Failure Recovery]].

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Orchestrators|Orchestrators]]
- [[Coding Knowledge/04 - Agent Engineering/State Management|State Management]]
- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]

## Sources

- Practitioner synthesis; hub-and-spoke registry design verified in this project. General multi-agent framing informed by published agent-framework documentation (LangGraph, AutoGen) - concepts restated, no text reproduced.
