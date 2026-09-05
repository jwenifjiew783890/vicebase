---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Evaluation

Knowing whether a change made the system better. Without this, every prompt change is a guess with a confident narrator.

## The core problem

LLM systems are non-deterministic, and their failures are subtle rather than loud. A change that
fixes one case commonly breaks three others, and nobody notices because nobody re-ran them.
**Vibes-based iteration converges on whatever was tested last.**

The minimum viable answer is small and cheap: **a fixed set of 20-50 real inputs with expected
outcomes, run on every change**. That alone catches most regressions and takes an hour to build.
Everything below is refinement.

## Building the set

- **Use real inputs.** Synthetic cases test what you imagined, not what happens.
- **Include the failures you have already fixed.** Every bug becomes a permanent case - this is
  the regression suite, and it is the highest-value part.
- **Include the boundaries**: empty input, huge input, ambiguous requests, adversarial phrasing,
  wrong-language input, and cases where the correct answer is "I don't know".
- **Keep a holdout.** If every case is used for tuning, you have fitted the prompt to the set
  and your numbers mean nothing.
- **Version it with the code.**

## Scoring, in order of preference

1. **Deterministic checks** - exact match, schema validity, does it compile, does the test pass,
   is the cited source real, is the number correct. Cheap, reliable, unambiguous. Use these
   wherever the task permits.
2. **Programmatic properties** - length bounds, required sections present, no forbidden content,
   citations resolve to existing documents.
3. **LLM-as-judge** - a model scoring against a rubric. Necessary for open-ended quality, but:
   it is biased toward longer and more confident answers, it is inconsistent across runs, and it
   must itself be validated against human judgement on a sample before you trust it.
4. **Human review** - the ground truth, too slow to run continuously. Use it to calibrate the
   judge and to spot-check.

## What to measure for each system type

| System | Metrics |
| --- | --- |
| **Retrieval** | recall@k, MRR, nDCG - measured *separately* from generation |
| **RAG** | faithfulness (every claim supported), answer relevance, citation accuracy |
| **Extraction** | field-level precision and recall, plus "correctly said unknown" |
| **Agents** | task completion, steps taken, tool-selection accuracy, cost, failure recovery |
| **Classification** | per-class precision/recall; overall accuracy hides the rare class |

**Measure stages separately.** An end-to-end score tells you something regressed, not where.
In a RAG system, if retrieval recall is 60%, no generation work will fix the other 40%.

## Operational discipline

- **Run on every prompt, model, retrieval or tool change.** Prompts are code; they need the same
  gate.
- **Record cost and latency alongside quality** - a 2% quality gain for 5x cost is a decision,
  and it should be made knowingly.
- **Pin model versions during evaluation.** Otherwise a provider update looks like your change.
- **Repeat non-deterministic runs.** A single sample of a stochastic system is noise; use
  several runs and compare distributions.
- **Track in production too**: user corrections, retries, abandonment, thumbs-down, escalation
  rate. These catch what an offline set never will.

## Failure modes

- **No evaluation at all.** By far the most common, and every claim of improvement is then
  unfalsifiable.
- **Evaluating on the tuning set.** Guaranteed to look good and mean nothing.
- **Averaging away the failures.** 90% average with a catastrophic 10% may be unusable. Look at
  the worst cases, not the mean.
- **An unvalidated LLM judge**, whose biases you have now baked into the target.
- **Testing only the happy path**, so every real-world edge case is a surprise.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/RAG|RAG]]
- [[Coding Knowledge/03 - AI Engineering/Hallucination Reduction|Hallucination Reduction]]
- [[Coding Knowledge/04 - Agent Engineering/Evaluation Loops|Evaluation Loops]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]

## Sources

- Practitioner synthesis. Corroborating work: Zheng et al., "Judging LLM-as-a-Judge" (2023) - <https://arxiv.org/abs/2306.05685>; RAGAS faithfulness/relevance metrics - <https://github.com/explodinggradients/ragas>. Concepts restated.
