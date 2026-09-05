---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Model Routing

Sending each request to the model that is good enough for it, rather than to the best model for all of them.

## Why route

Models differ by an order of magnitude in cost and latency and by much less in quality on easy
tasks. Classification, extraction, formatting and short summarisation are usually served
perfectly by a small model; multi-step reasoning, architecture and difficult debugging are not.

Routing is also **availability engineering**: a router with a fallback survives a provider
outage, and a single-provider design does not.

## Routing signals, cheapest first

1. **Task type** - declared by the caller. The most reliable signal and the cheapest. If your
   system already knows it is doing extraction rather than design, route on that.
2. **Input length** - long context restricts the eligible set immediately.
3. **Required capability** - tool calling, structured output, vision, a specific context window.
   This is a hard filter, not a preference.
4. **Explicit difficulty hints** - a caller-supplied flag, or a user-selected mode.
5. **Cascade** - try the cheap model, validate the result, escalate on failure. Effective when
   validation is cheap and reliable; wasteful when it is not.
6. **Learned classifier** - a small model predicting which tier is needed. Only worth it at
   volume, and it needs its own evaluation.

Prefer 1-3. Cascades and classifiers add moving parts and a new failure mode each.

## Design rules

- **Fixed model per capability by default.** Predictability is worth more than marginal savings
  in a small system, and it makes evaluation meaningful.
- **Declare the model in configuration**, never inline at call sites. Otherwise you cannot
  answer "which model handled this?".
- **Always have a fallback**, and define what happens when every option fails: a clear error, a
  queued retry, or a degraded answer - decided in advance, not improvised.
- **Log the model, version, token counts and latency on every call.** Without this, both cost
  and quality regressions are invisible.
- **Re-evaluate when swapping models.** Prompts are tuned to a model; a "better" model can be
  worse on your specific prompts. Never swap without running the evaluation set.
- **Pin versions** where the provider allows, so behaviour does not shift under you.

## Failure modes

- **Single provider, no fallback.** One outage stops everything. *(This stack's n8n agents all
  route to one NVIDIA endpoint - a known single point of failure, documented rather than
  hidden.)*
- **Routing on a signal that does not predict difficulty**, such as prompt length as a proxy for
  complexity.
- **Cascade without validation** - escalating on a heuristic that does not detect the failure,
  so you pay twice and still return the bad answer.
- **Silent fallback.** Quality drops and nobody knows the cheap model answered. Record which
  model responded, and surface it when it matters.
- **Router latency exceeding the saving.** A model call to decide which model to call.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/LLM APIs|LLM APIs]]
- [[Coding Knowledge/03 - AI Engineering/Evaluation|Evaluation]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]

## Sources

- Practitioner synthesis. Provider pricing and capability documentation. The single-provider observation is from this project's n8n agent layer.
