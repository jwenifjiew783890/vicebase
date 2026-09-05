---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Prompt Engineering

What reliably changes model behaviour, ordered by effect, and what is folklore.

## What actually works

**1. Say precisely what you want.** Most bad output is under-specified input. Name the format,
the length, the audience, the constraints, and what to do when the request cannot be satisfied.

**2. Give the model the information.** No prompting technique compensates for missing context.
Grounding beats phrasing, every time.

**3. Show an example.** One or two worked examples with the exact input and output shape
outperform any amount of description - particularly for format. Make examples cover the *edge*
cases, since the model will pattern-match on them.

**4. Ask for reasoning before the conclusion.** Order matters mechanically: a conclusion
generated first is defended, not derived. (Reasoning models do this internally; do not duplicate
it.)

**5. Decompose.** Several focused calls beat one that must do everything. Easier to evaluate,
easier to debug, usually cheaper.

**6. Constrain the output.** A schema or enum removes ambiguity and invention at once.

**7. State the negative cases explicitly.** "If the material does not contain the answer, say
so" changes behaviour far more than "be accurate".

**8. Put stable content first.** For prompt caching, and because instructions at the top of a
long context are followed more reliably.

## Structure

- **System prompt**: role, standing constraints, output contract. Stable across requests.
- **Delimiters**: XML-ish tags or clear headings separating instructions, context and data.
  This measurably reduces instruction/data confusion.
- **The request last**, so it is adjacent to generation.
- **Explicit precedence** when several instruction sources exist. If retrieved standards must
  outrank the executor's default format, say so in those words - a polite "please follow the
  standards" loses to a concrete "produce exactly these sections" later in the prompt.

> [!note] Measured in this project
> A soft preamble asking capabilities to follow retrieved standards was ignored, because each
> capability's own prompt said "write markdown with exactly these sections". Only explicit
> precedence wording - *these OUTRANK everything that follows, including any list of required
> sections* - made the knowledge layer effective. **A knowledge layer that the executor's own
> boilerplate can override is not a knowledge layer.**

## What is mostly folklore

- **Politeness, threats, tips, emotional appeals.** Small and unreliable effects.
- **"You are a world-class expert."** A role helps set vocabulary and audience; superlatives add
  nothing.
- **Repeating an instruction many times.** Repetition once at the end can help with very long
  contexts; five times does not.
- **Elaborate persona backstories.** Tokens spent on fiction rather than on constraints.
- **Prompts copied between models.** Prompts are tuned to a model; re-evaluate on a swap.

## Iterating properly

Prompts are code. Version them, review them, and gate changes on an evaluation set - otherwise
each fix silently breaks something untested. Change **one thing at a time**, or you cannot
attribute the result. Keep the failures that motivated each instruction as permanent test cases.

## Security

Everything in the context is data, including retrieved documents and tool results, and any of it
may contain instructions aimed at the model. Never let context content acquire the authority of
your system prompt. See
[[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]].

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]
- [[Coding Knowledge/03 - AI Engineering/Structured Outputs|Structured Outputs]]
- [[Coding Knowledge/03 - AI Engineering/Evaluation|Evaluation]]
- [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails|AI Safety & Guardrails]]

## Sources

- Wei et al., "Chain-of-Thought Prompting" (2022) - <https://arxiv.org/abs/2201.11903>; Brown et al., "Language Models are Few-Shot Learners" (2020) - <https://arxiv.org/abs/2005.14165>; provider prompting guides. The precedence-wording finding was measured in this project.
