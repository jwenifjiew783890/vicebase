---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Context Management

The context window is a fixed budget with non-uniform value. Managing it well is one of the highest-leverage things in an LLM system.

## The budget

Input **plus** output must fit. Reserve room for the answer, or generation truncates mid-way -
which presents as a malformed result, not as an error.

A typical allocation for an agent turn:

| Slot | Notes |
| --- | --- |
| System prompt + tool definitions | Stable - put it first so prompt caching can reuse it |
| Retrieved knowledge | The variable, expensive part; bound it explicitly |
| Conversation history | Grows without limit unless managed |
| Current request | Small |
| Reserved for output | Must be explicit, not "whatever is left" |

## Position matters

Material at the **start and end** of a long context is used far more reliably than material in
the middle. So:

- Instructions at the top; the immediate request at the bottom.
- The most important retrieved chunk first *or* last, not buried at position 12 of 20.
- **More context is not better context.** Twenty chunks of which three are relevant produce
  worse answers than the three alone.

## Managing a growing conversation

| Strategy | Keeps | Loses |
| --- | --- | --- |
| **Truncate oldest** | Recency | The original task, often the most important thing |
| **Summarise older turns** | Gist and decisions | Detail and exact wording |
| **Keep first + last N** | The task and the recent state | The middle |
| **Structured state object** | Exactly what you chose to keep | Anything not modelled |
| **Externalise to notes/files** | Everything, retrievable | Requires a retrieval step |

The best results come from **not keeping raw history at all**: maintain an explicit state object
(goal, decisions made, facts established, current step, open questions) and rebuild the context
from it each turn. History is a transcript; state is what matters.

**Never silently drop the original task.** The most damaging truncation failure is losing the
goal while retaining recent chatter, after which the agent works confidently on the wrong thing.

## Tool results

Tool output is the fastest way to destroy a context window - one unbounded file read or database
query can consume everything. Bound at the tool boundary, not afterwards: truncate, paginate,
summarise, and **say explicitly that you truncated**, so the model knows the view is partial
rather than complete.

## Prompt caching

Providers cache the prefill of a stable prefix, substantially cutting cost and latency. This
makes prompt *ordering* an engineering decision: stable content first (system prompt, tools,
fixed corpus), variable content last. Reordering for aesthetic reasons can silently destroy the
cache hit rate and multiply cost.

## Practical rules

- **Count tokens before sending.** Do not discover a limit at request time.
- **Bound every variable input** - retrieved knowledge, tool output, history - with an explicit
  character or token cap. *(This stack caps assembled knowledge at 6,000 characters and 6 notes
  per domain, deliberately.)*
- **Log context size** per request; growth is a cost regression you will otherwise not see.
- **Prefer retrieval over stuffing.** Retrieving 3 relevant chunks beats including 100 pages,
  in accuracy as well as cost.
- **Structure the context with clear delimiters and headings.** A wall of concatenated text is
  harder to use than labelled sections.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/LLM Architecture|LLM Architecture]]
- [[Coding Knowledge/03 - AI Engineering/Agent Memory|Agent Memory]]
- [[Coding Knowledge/03 - AI Engineering/Retrieval|Retrieval]]
- [[Coding Knowledge/04 - Agent Engineering/State Management|State Management]]

## Sources

- Liu et al., "Lost in the Middle" (2023) - <https://arxiv.org/abs/2307.03172>; provider documentation on prompt caching and context limits. The 6,000-character cap is this project's Knowledge Retriever design.
