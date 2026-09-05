---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Reranking

A second, more expensive pass that fixes precision after a cheap first pass has provided recall.

## Why a second stage exists

First-stage retrieval must be fast over the whole corpus, so it compares pre-computed
representations - a query vector against document vectors that were embedded without ever
seeing the query. That is a real information loss.

A **cross-encoder** reranker instead reads the query and the document *together* and scores the
pair. Far more accurate, far too slow to run over a corpus - so it runs over the 20-50
candidates the first stage produced.

This two-stage shape (cheap recall, expensive precision) is the standard architecture of modern
search, and adding the second stage is often a larger quality gain than any amount of embedding
tuning.

## When it is worth it

**Worth it when**: the corpus is large or noisy, the first stage returns plausible-but-wrong
results, the query is conceptual, or the context budget is tight enough that only 3-5 chunks fit
and choosing the right 3 matters.

**Not worth it when**: the corpus is small (rerank latency exceeds the benefit), the first stage
already ranks correctly, latency is critical, or filtering by metadata already narrows the set
to a handful.

Do not add a reranker before measuring that ranking - rather than recall - is the problem. If
the right chunk is not in the top 50, reranking cannot help; fix retrieval instead.

## Options

| Approach | Quality | Latency | Notes |
| --- | --- | --- | --- |
| Cross-encoder model | High | 10s-100s ms for ~50 docs | The standard choice; small models run locally |
| LLM-as-reranker | High, flexible | Slow, expensive | Useful when the criterion is nuanced |
| Reciprocal Rank Fusion | Moderate | Negligible | Not a true reranker; fuses lists. Do this first |
| Heuristic boosts | Low but useful | Free | Recency, source authority, exact-title match |

Start with RRF and metadata boosts - they are free. Add a cross-encoder when measurement shows
ranking is still the limiting factor.

## Practical notes

- **Rerank 20-50 candidates**, not 500. Latency scales linearly and gains flatten quickly.
- **Cross-encoder scores are not probabilities** and are not comparable across models. Use them
  for ordering, and calibrate any threshold against your own data.
- **Apply a relevance floor.** If the best reranked score is poor, returning nothing and saying
  so is better than returning the least-bad chunk - which the model will treat as an answer.
- **Reranking runs a model**, with the memory and CPU cost that implies. On a local deployment
  that is another resident model.
- **Cache** rerank results for repeated queries.

## Failure modes

- **Reranking a bad candidate set.** Garbage in, well-ordered garbage out.
- **Adding a reranker to fix a chunking problem.** It cannot recover an answer that was split in
  half.
- **Reranking too many candidates** and paying latency for nothing.
- **Treating the score as absolute** and thresholding on an uncalibrated number.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Retrieval|Retrieval]]
- [[Coding Knowledge/03 - AI Engineering/RAG|RAG]]
- [[Coding Knowledge/03 - AI Engineering/Evaluation|Evaluation]]

## Sources

- Nogueira & Cho, "Passage Re-ranking with BERT" (2019) - <https://arxiv.org/abs/1901.04085>; Sentence-Transformers cross-encoder documentation - <https://www.sbert.net/examples/applications/cross-encoder/>. Staging advice is practitioner judgement.
