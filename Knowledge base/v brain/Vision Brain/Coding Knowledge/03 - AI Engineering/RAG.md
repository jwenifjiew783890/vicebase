---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# RAG

Retrieval-augmented generation as a pipeline. Every stage can fail independently, and the symptom is always the same: a bad answer.

## Why it exists

A model's parametric knowledge is lossy, undated and unverifiable. Retrieval replaces it with
text you control, that you can cite, and that you can update without retraining. The trade is
that you now own an information-retrieval system, with all of its failure modes.

## The pipeline

```
documents -> chunk -> embed -> index
query -> (rewrite) -> search -> filter -> rerank -> assemble -> generate -> cite
```

## Where it actually goes wrong

Diagnose in this order; the later stages are usually blamed for the earlier stages' failures.

**1. The document was never ingested.** Check the index, not the code. This is the most common
cause and the easiest to miss.

**2. Chunking destroyed the answer.** Split mid-table, mid-function, or separated a heading from
its content. If the answer spans a boundary, no retriever will find it whole.

**3. The query does not resemble the document.** Users ask questions; documents state facts.
"How do I rotate the key?" may not embed near "Key rotation is performed by...". Query
rewriting, HyDE, or hybrid keyword search address this.

**4. Retrieval returned the wrong chunks.** Semantic-only search misses exact identifiers -
error codes, function names, IDs - because embeddings are poor at rare tokens. **Hybrid search
(BM25 + vector) is the single highest-value fix** in most RAG systems.

**5. The right chunk was retrieved but ranked below the cut-off.** This is what reranking is
for.

**6. Too much context.** Twenty chunks of which two are relevant is worse than three good ones -
the model is distracted, and the middle of a long context is used unreliably.

**7. The model ignored the context** and answered from parametric knowledge. Instruct it
explicitly to answer only from the provided material and to say when the material is
insufficient.

**8. No citation, so nobody can tell.** Without per-claim attribution, a wrong answer and a
right answer look identical.

## Design decisions that matter most

- **Chunk on structure, not character count.** Headings, sections, functions, paragraphs.
  Include the parent heading in each chunk - it restores the context a naive split destroys.
- **Overlap** of 10-20% reduces boundary loss, at the cost of duplication.
- **Store metadata with every chunk**: source path, section, date, permissions. Metadata
  filtering is more valuable than most people expect, and it is what makes multi-domain
  retrieval safe.
- **Retrieve wide, rerank, then cut narrow.** Top-50 by vector, rerank, keep 3-5.
- **Always include the source path in the assembled context**, so the model can cite and a human
  can verify.
- **Bound the assembled context** by characters or tokens, not by chunk count.

## When *not* to build a RAG pipeline

If the corpus is small, structured, or navigable, **direct retrieval beats embedding**. Reading
three known files is more accurate, cheaper and more debuggable than a similarity search over
their fragments.

This is why the Vision Brain deliberately does not embed the vault: OpenCode searches and reads
notes on demand through Obsidian's own index, and the notes are written to be read whole. See
[[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]].

## Evaluating it

Measure the stages separately or you will tune blind:

- **Retrieval**: recall@k - is the correct chunk in the retrieved set at all? If not, no
  generation change can help.
- **Ranking**: MRR / nDCG - how high is it?
- **Generation**: faithfulness (is every claim supported by the retrieved text?) and
  answer relevance.

A fixed set of question/expected-source pairs, run on every change, is the minimum viable
evaluation and takes an hour to build.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Retrieval|Retrieval]]
- [[Coding Knowledge/03 - AI Engineering/Embeddings|Embeddings]]
- [[Coding Knowledge/03 - AI Engineering/Reranking|Reranking]]
- [[Coding Knowledge/03 - AI Engineering/Evaluation|Evaluation]]

## Sources

- Lewis et al., "Retrieval-Augmented Generation" (2020) - <https://arxiv.org/abs/2005.11401>; Gao et al., "Precise Zero-Shot Dense Retrieval" (HyDE, 2022) - <https://arxiv.org/abs/2212.10496>; Liu et al., "Lost in the Middle" (2023) - <https://arxiv.org/abs/2307.03172>. Pipeline failure ordering is practitioner judgement.
