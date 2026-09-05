---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# LLM Architecture

Enough of how a transformer works to predict its behaviour - which is the only reason an engineer needs it.

## The mechanism

A decoder-only transformer predicts the next token from all preceding tokens. Self-attention
lets every position attend to every earlier position; the stack of layers builds progressively
more abstract representations; the output is a probability distribution over the vocabulary,
sampled once per step and fed back in.

That is the entire loop. Everything below follows from it.

## What follows, practically

**It generates left to right and cannot revise.** A wrong token early is conditioned on for the
rest of the output. This is why "think before answering" prompting works: it puts the reasoning
into the context *before* the conclusion depends on it.

**Attention is quadratic in sequence length.** Doubling the context roughly quadruples the
prefill compute. Long contexts are expensive in latency and money, not just in tokens.

**Position matters.** Material at the very start and very end of a long context is used far more
reliably than material in the middle - the "lost in the middle" effect. Put the instruction and
the most important evidence at the edges.

**It has no working memory outside the context.** Nothing persists between requests unless you
put it back in. "Remembering" is an application feature - see
[[Coding Knowledge/03 - AI Engineering/Agent Memory|Agent Memory]].

**It is a next-token predictor, not a database.** Facts are lossy, compressed and undated.
Parametric knowledge is where hallucination originates; retrieved context is where it is cured.

**Tokens are not words.** Roughly 4 characters per token in English; code, JSON, rare words,
non-Latin scripts and long identifiers tokenise far worse. Character-level tasks (counting
letters, reversing strings) are genuinely hard for this reason - it is not a reasoning failure.

## Sampling

| Parameter | Effect | Use |
| --- | --- | --- |
| `temperature` | Flattens or sharpens the distribution | 0 for extraction/classification/code; 0.7+ for varied prose |
| `top_p` | Sample from the smallest set summing to p | Alternative to temperature; adjust one, not both |
| `top_k` | Sample from the k most likely | Blunter |
| `frequency`/`presence penalty` | Discourage repetition | Sparingly; distorts factual output |
| `stop` | End generation on a sequence | Structural control |
| `seed` | Reproducibility, where supported | Best-effort only |

**Temperature 0 is not deterministic in practice.** Batching, floating-point non-associativity
on GPUs, and mixture-of-experts routing all introduce variation. Design for near-deterministic,
never for identical.

## Model families worth distinguishing

- **Base** models continue text. **Instruction-tuned** models follow directions. **Reasoning**
  models spend extra tokens on internal deliberation before answering - better on hard
  multi-step problems, slower and more expensive, and often unsuitable when latency matters.
- **Mixture-of-experts** models activate a fraction of their parameters per token, giving large
  capacity at lower inference cost - relevant because their throughput and memory profiles
  differ from dense models of the same nominal size.

## Common misconceptions

- *"Bigger context is strictly better."* Cost, latency and mid-context degradation all rise.
  Retrieval usually beats stuffing.
- *"It knows what it does not know."* Calibration is weak; confidence and correctness are only
  loosely coupled.
- *"Fine-tuning adds knowledge."* Fine-tuning mostly teaches format, style and task shape.
  For facts, retrieve.
- *"Temperature 0 makes it correct."* It makes it consistent, including consistently wrong.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]
- [[Coding Knowledge/03 - AI Engineering/Inference|Inference]]
- [[Coding Knowledge/03 - AI Engineering/Hallucination Reduction|Hallucination Reduction]]

## Sources

- Vaswani et al., "Attention Is All You Need" (2017) - <https://arxiv.org/abs/1706.03762>; Liu et al., "Lost in the Middle" (2023) - <https://arxiv.org/abs/2307.03172>. Provider documentation for sampling parameters. Concepts restated, no text reproduced.
