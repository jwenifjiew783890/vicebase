---
type: MOC
role: domain index
domain: Intent & Task Understanding Knowledge
created: 2026-09-04
---

# Intent & Task Understanding

How Vision turns **a rough, informal, incomplete human request** into a clear,
executable plan for the right agents — *without* quietly replacing what the user
actually wanted. This is the layer that sits between a person typing
"make me a website for vision" and the [[Coding Knowledge/11 - Vision & OpenCode/Vision Architecture|VISION — AGENTS]]
orchestrator dispatching real work.

> This domain is *methodology*, not a runtime. It adds no agent, no model, no
> dispatcher. It shapes how Vision **reads a request and plans it**, then hands a
> structured task to the existing hub. It never overrides Vision's safety rules
> or the user-specific files below.

## Precedence — the user-specific layer wins

For **Muaz specifically**, the user model overrides every generic default here:

- [[Communication Style]] — blunt, casual, Roman-Urdu/Hindi and code-switching are
  normal input; *don't* mistake terseness for a lack of intent.
- [[Personality & Behavior]] — delegate-and-verify; wants remembered context;
  values honesty over pleasing language; challenges wrong answers.

When this domain and those files disagree, **those files are right.**

## The pipeline

```
RAW USER REQUEST
   ↓   read it as-is, in their own words and language
INTENDED OUTCOME        → 01 Intent Extraction
   ↓   expand to something operational, meaning preserved
ENRICHED REQUEST        → 02 Prompt Enhancement
   ↓   pin down what "done" means; separate fact from guess
REQUIREMENTS · CONSTRAINTS · ASSUMPTIONS   → 03
   ↓   what is missing and does it change the result?
CLARIFY  or  SAFE DEFAULT   → 05 Clarification, Defaults & Safety
   ↓   break into ordered stages, pick the right agents
TASK PLAN · AGENT TASKS     → 04 Task Decomposition & Agent Selection
   ↓
VISION — AGENTS (existing hub)  →  results  →  back to the user
```

**Match ceremony to risk.** `open example.com` stays one line and one agent. Only a
genuinely multi-part request ("download the file and open it in WordPad") earns the
full pipeline. Over-planning a trivial request is as wrong as under-planning a
complex one.

## The internal task contract *(Part L — Vision's synthesis)*

The pipeline fills in one structure. Its **whole point is to keep four things
separate** so an inference is never shipped as if the user had asked for it:

```jsonc
{
  "goal":               "the user's actual objective, in their terms",
  "explicit":           ["things the user actually said / asked for"],
  "inferred":           ["reasonable inferences — labelled as inferences"],
  "assumptions":        ["optional defaults chosen because they were safe + non-critical"],
  "constraints":        ["hard limits: named tool, file format, filename, style, language, budget, 'do not', 'must'"],
  "clarifications_needed": ["only the questions whose answers change the result"],
  "artifacts_required": ["files / outputs the user expects to receive"],
  "preferred_tools":    ["tools or agents the user named — to be honoured, not overridden"],
  "selected_agents":    ["the Vision agents chosen for this"],
  "steps":              [{"stage": 1, "agent": "...", "task": "...", "depends_on": [], "verify": "..."}],
  "verification":       ["how each stage and each deliverable is checked"]
}
```

| Field group | Filled in by | Never do |
| --- | --- | --- |
| `goal`, `explicit` | [[Intent & Task Understanding Knowledge/01 - Intent Extraction\|01]] | invent a goal the user did not have |
| `inferred`, `assumptions`, `constraints` | [[Intent & Task Understanding Knowledge/03 - Requirements, Constraints & Assumptions\|03]] | present an inference as an explicit request; drop a stated constraint |
| `clarifications_needed` | [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05]] | ask what a safe default or a tool could answer |
| `selected_agents`, `steps`, `verification` | [[Intent & Task Understanding Knowledge/04 - Task Decomposition & Agent Selection\|04]] | route everything through one agent; skip a verify step on a write |

This is *adapted to Vision*, not a rigid schema to serialise. Downstream it collapses
onto the hub's existing plan shape — `{"stages":[{"agent_id","task","context","why"}]}`
— which the `Manager` node already emits. The contract is the richer intent model
*behind* that plan; `steps[].task` becomes a stage `task`, and an upstream stage's
result is carried into a downstream stage's `context` by the hub's `Prepare Stage`
node (proven live: a browser stage's page title flowed into a desktop stage that
saved and verified it).

## Notes

| Note | Covers |
| --- | --- |
| [[Intent & Task Understanding Knowledge/01 - Intent Extraction\|01 · Intent Extraction]] | Desired outcome, object, environment, prohibitions; informal/typo/Roman-Urdu input; "that one" references |
| [[Intent & Task Understanding Knowledge/02 - Prompt Enhancement\|02 · Prompt Enhancement]] | Expand short requests into operational ones; preserve the goal and every constraint; inspect before redesigning |
| [[Intent & Task Understanding Knowledge/03 - Requirements, Constraints & Assumptions\|03 · Requirements, Constraints & Assumptions]] | Reframe vague → testable; hard-constraint taxonomy; explicit vs inferred vs optional-default |
| [[Intent & Task Understanding Knowledge/04 - Task Decomposition & Agent Selection\|04 · Task Decomposition & Agent Selection]] | Independent/dependent/parallel stages; picking the right Vision agent; passing material between them |
| [[Intent & Task Understanding Knowledge/05 - Clarification, Defaults & Safety\|05 · Clarification, Defaults & Safety]] | When to ask vs assume; safe-autonomous vs ask-first; never infer permission for consequential actions |
| [[Intent & Task Understanding Knowledge/99 - Sources & Provenance\|99 · Sources & Provenance]] | Every external source, licence, retrieval date, derive/summarise split |

## The one rule under all of it

**Enhancement makes the user's request executable. It does not change the request
into what the model would have preferred.** Preserve meaning, preserve constraints,
preserve named tools and style. When a missing decision would materially change the
result, ask. When it would not, choose a sensible default and say so.

## Related

- [[Conversation Knowledge/00 - Conversation Knowledge Index\|Conversation Knowledge]] —
  *how* Vision talks; this domain is *what* it decides to do. 01 there ("when not to
  ask") and 05 here share the same restraint.
- [[Coding Knowledge/09 - Engineering Practices/Requirements Analysis\|Requirements Analysis]]
  and [[Coding Knowledge/09 - Engineering Practices/Spec-Driven Development & Task Breakdown\|Spec-Driven Development & Task Breakdown]] —
  the engineering-grade version of the same discipline, for code work specifically.

> [!note] Not wired into n8n
> This is reference knowledge for Vision's reasoning/planning layer. It is **not**
> attached to any specialist agent's `knowledge_domains` and requires **no** registry
> or workflow change. If it is ever wired to an `inject`-mode agent, note the
> retriever's 6-note / 6000-char budget: keep it to the six always-on notes (00–05).
