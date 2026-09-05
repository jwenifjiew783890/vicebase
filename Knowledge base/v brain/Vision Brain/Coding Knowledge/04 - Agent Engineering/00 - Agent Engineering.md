---
type: MOC
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Agent Engineering

Building systems where a model decides what to do next. The engineering is almost entirely in the constraints, not in the model.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

> [!important] The governing principle
> **Determinism where you can, model where you must.** Every step a model chooses is a step that
> can fail non-deterministically, cost money, and resist debugging. A working agent is mostly
> ordinary software with a model at the points that genuinely need judgement.

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/04 - Agent Engineering/Planners\|Planners]] | Turning a request into steps |
| [[Coding Knowledge/04 - Agent Engineering/Orchestrators\|Orchestrators]] | Routing, sequencing, and holding the contract |
| [[Coding Knowledge/04 - Agent Engineering/Tool Selection\|Tool Selection]] | Making the right tool the obvious one |
| [[Coding Knowledge/04 - Agent Engineering/Multi-Agent Systems\|Multi-Agent Systems]] | When more agents help, and when they multiply failure |
| [[Coding Knowledge/04 - Agent Engineering/State Management\|State Management]] | What is carried between steps |
| [[Coding Knowledge/04 - Agent Engineering/Feedback Loops\|Feedback Loops]] | Acting on the result of acting |
| [[Coding Knowledge/04 - Agent Engineering/Self-Improvement\|Self-Improvement]] | Systems that change their own behaviour, safely |
| [[Coding Knowledge/04 - Agent Engineering/Skill Systems\|Skill Systems]] | Reusable procedures as data |
| [[Coding Knowledge/04 - Agent Engineering/Evaluation Loops\|Evaluation Loops]] | Knowing whether the agent got better |
| [[Coding Knowledge/04 - Agent Engineering/Failure Recovery\|Failure Recovery]] | Behaving well when a step fails |
| [[Coding Knowledge/04 - Agent Engineering/Permissions\|Permissions]] | What it may do, enforced in code |
| [[Coding Knowledge/04 - Agent Engineering/Sandboxing\|Sandboxing]] | Containing what it can reach |

## The architecture that works

```
request -> router (deterministic) -> capability (specific, bounded)
                                       -> knowledge retrieval (scoped)
                                       -> executor (tools, permissioned)
                                       -> validated result
```

The model appears at: choosing the capability, planning within it, and interpreting results.
Everything else - routing tables, permission checks, retries, validation, assembly - is code.

## The counting rule

Before adding a component, ask **what fails if this is absent**. Agent systems accumulate
layers that each add latency, cost and a failure mode, and remove nothing.
