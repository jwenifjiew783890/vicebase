---
type: stable
category: ai-models
last_verified: 2026-09-03
confidence: high
---

# 11 — AI & Model Preferences

## Strategy: hybrid local + cloud

```
Local model        →  quick, private, basic tasks
Strong API model   →  complex reasoning, tool use, coding, multi-step automation
```

`[user 2026-09-03]`

**No model is permanently canonical.** Vision must stay able to switch
providers, runtimes and models. `[user 2026-09-03]` `[vault]` (ADR-004, ADR-005)

## Providers used

| Provider | Status |
| --- | --- |
| TokenRouter (OpenAI-compatible) | active, ~86 models `[verified 2026-09-03]` |
| NVIDIA-hosted APIs | available through the above `[user]` `[verified]` |
| Ollama (local) | installed, not running `[verified 2026-09-03]` |

## Observed model behaviour `[verified 2026-09-03]`

Measured while building the Obsidian integration — useful, and likely to age:

- **`deepseek/deepseek-v4-pro`** — fast (~1s first token), reliable multi-step
  MCP tool calling. Drove the whole Phase 2.1 test suite correctly.
- **`openai/gpt-oss-120b`** — responsive (~1s).
- **`z-ai/glm-5.3-free`** — slow (~32s).
- **`moonshotai/kimi-k3`** — did not return within 45s; unusable at that time.

`WORKING CONTEXT` — provider-side performance, not a property of the models.

## Earlier stated role preferences `[vault]`

From [AI Preferences](Preferences/AI%20Preferences.md.md) — recorded during the abandoned Electron build, so
treat as **direction, not current configuration**:

- General chat → Qwen or similar
- Coding → DeepSeek or similar strong coding model
- Planning → Hermes or similar

The DeepSeek-for-coding preference is corroborated by the 2026-09-03 results
above. `[inferred — CONFIDENCE: MEDIUM]`

## Behavioural expectations of AI systems `[vault]` `[user]`

- Be useful, clear, honest, practical.
- **Never claim success without evidence.**
- Communicate uncertainty rather than papering over it.
- Use tools when they materially help; don't perform unnecessary actions.
- **Never silently execute destructive operations.**
- Don't present outdated model knowledge as current fact.
- Use stored preferences and project context; never invent personal facts.
- Memory should be curated, not automatic — see
  [[Memory/99 - Memory Rules|99 — Memory Rules]].

## Agents

Agent ≠ model. A model supplies intelligence; an agent supplies role,
instructions, tools, permissions, context and workflow. Agents are replaceable
workers and should not become the product's primary navigation. `[vault]`
(ADR-007, [[Agent Strategy]])
