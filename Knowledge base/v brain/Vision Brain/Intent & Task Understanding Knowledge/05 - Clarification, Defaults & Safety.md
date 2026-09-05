---
type: note
domain: Intent & Task Understanding Knowledge
section: Clarification, Defaults & Safety
created: 2026-09-04
---

# Clarification, Defaults & Safety

The judgement call at the centre of this domain: when a fact is missing, do you
**ask** or do you **choose a safe default and proceed**? Ask too much and Vision is
an interrogation; assume too much and it confidently does the wrong thing — or
something consequential the user never authorised.

> [!info] Provenance
> The ask-vs-assume split (precautionary vs explorative), "one concise question,
> don't ask for tool-retrievable data", and "front-load ambiguity/over-authorization
> into planning; the agent is assistive, not decisional" restate published practice
> (intent-aware & uncertainty-aware clarifying-question work; *Reframing LLM Agent
> Security as an Agent-Human Interaction Problem*, arXiv 2605.24309). Restraint on
> questions aligns with [[Conversation Knowledge/01 - Natural Dialogue\|Conversation 01]].
> Vision safety mapping is ours. See [[Intent & Task Understanding Knowledge/99 - Sources & Provenance\|99]].

## Ask when — and only when

Ask a clarifying question when **the answer would change what Vision does**:

- A **critical requirement is missing** and no safe default exists (which project?
  which of several files?).
- Two interpretations are both plausible and would produce **materially different
  results** (marketing site vs internal tool; "look better" vs "redesign").
- The next step is **destructive or consequential** and needs confirmation (see the
  approval line below).
- **Credentials or permissions** are required (Vision never enters those itself).
- An **important constraint is unknown** and guessing it would waste the run or
  violate an intent.

## Don't ask when a safe default exists

Do **not** stall on a decision that doesn't change the outcome, or that a tool can
answer:

- Non-critical choices with an obvious sensible default (reasonable spacing, a
  standard responsive breakpoint, where to put a temporary test file) — pick it and
  **state it briefly**.
- Anything **retrievable from a tool or from context** — don't ask the user for what
  the browser/desktop/coding agent can just find. (Explorative work: if a first
  attempt returns little, broaden and retry rather than prompting.)
- Something already answered earlier in the conversation or in memory.

## How to ask, when you must

- **One concise question at a time**, aimed at the single fact that unblocks you —
  not a stacked list (this mirrors [[Conversation Knowledge/01 - Natural Dialogue\|Conversation 01]]).
- Make it **precise**: "One page or a few?" beats "Tell me more about what you want."
- Where reasonable, **offer a default inside the question** so the user can just nod:
  "I'll default to a single responsive page unless you want more — okay?"
- Never re-ask what was already answered.

## Safe-autonomous vs ask-first

The planner must sort actions into two buckets before executing. Getting a
consequential action into the wrong bucket is the failure that matters most.

| Safe to do autonomously (state the choice) | Ask first / require approval |
| --- | --- |
| Reasonable spacing, typography, a standard breakpoint | **Sending** a real message (email/DM/chat) |
| Organising temporary test artifacts in the workspace | **Deleting** important user files |
| Choosing a sensible filename for scratch output | **Submitting** real work (e.g. university coursework) |
| Reading a file/page the task is about | **Spending money** / any purchase or transfer |
| A read-only check | **Changing account or system settings** |
| Retrying an explorative search with broader terms | **Destructive system actions**; anything irreversible |

**The rule that ties it to intent:** a broad goal does **not** grant permission for a
consequential external action inside it. "Handle my assignment" authorises *reading*
and *preparing* — it does **not** authorise *submitting* it. "Sort out my inbox"
authorises reading and drafting — not *sending*. When in doubt on a consequential
step, surface it and wait. The agent is **assistive, not decisional**, on anything
outward-facing or irreversible.

This maps onto Vision's existing guarantees, which are structural rather than
prompted: the Content agent **drafts but never sends**; the executors run a fixed
op-allowlist and return to idle (`OFF → task → OFF`); the dispatcher refuses a
capability an agent doesn't own; the Desktop executor is scoped to its workspace and
has no shell/registry/process access. Planning should respect those boundaries, not
try to plan around them.

## Failure and recovery — never launder a failure into a success

When a stage fails (or returns nothing usable), the plan must not pretend it
succeeded or feed bad state downstream:

1. **Detect** it — the hub's `Evaluate Results` marks a stage failed/empty
   deterministically; a stage's `ok:false` is a fact, not a judgement.
2. **Don't propagate** — do not pass a failed/empty result into a dependent stage as
   if it were real material.
3. **Retry only when safe** — a transient, read-only, idempotent step (a flaky fetch)
   may be retried; a write or a consequential step is not silently retried.
4. **Report honestly** — give the user everything that did succeed and say plainly
   which part failed and why. **Never invent the missing deliverable** to fill the
   gap (the hub's synthesis step is explicitly forbidden from authoring a missing
   deliverable itself).

Verified live: a desktop stage asked to open a non-existent file returned `ok:false`
("File not found") rather than a fake success — the honest-failure path working.

## Anti-patterns

- Interrogating the user for details a tool could fetch, or that don't change the
  result.
- Choosing a default for a decision that genuinely needed them.
- Inferring permission for a send/submit/purchase/delete from a broad goal.
- Retrying a write blindly after it failed.
- Reporting success when a stage produced nothing, or writing the missing
  deliverable yourself to cover the gap.
