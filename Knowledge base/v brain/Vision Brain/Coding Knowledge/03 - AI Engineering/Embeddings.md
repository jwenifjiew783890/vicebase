---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Embeddings

Vectors as a similarity mechanism: what they capture, what they miss, and the operational decisions that are hard to reverse.

## What an embedding is

A fixed-length vector positioning text in a space where geometric closeness approximates
semantic relatedness. Cosine similarity is the usual measure - and it measures **relatedness**,
not relevance, not entailment, and not truth. "The deploy succeeded" and "the deploy failed"
embed close together; they are about the same thing and mean the opposite.

That single fact explains most disappointing vector-search results.

## What they are bad at

- **Exact identifiers**: error codes, function names, UUIDs, version numbers, file paths. Rare
  tokens carry little signal. Use keyword search for these.
- **Negation**: "without authentication" sits near "with authentication".
- **Numeric and temporal comparison**: "after March 2025" is not a geometric property.
- **Long documents**: one vector for 10 pages averages everything into mush.
- **Cross-domain jargon collisions**: the same word meaning different things in two domains.

The correct response is not to abandon embeddings but to **combine them with lexical search** -
see [[Coding Knowledge/03 - AI Engineering/Retrieval|Retrieval]].

## Operational decisions

**Model choice.** Small models (e.g. MiniLM-class, ~384 dims) are fast, cheap and run locally;
larger models retrieve better on hard queries. Domain-specific and code-specific models
meaningfully beat general ones on their domain.

**Dimensionality.** Higher costs storage, memory and search time. Some models support truncation
(Matryoshka representation) so you can trade accuracy for size without re-embedding.

> [!warning] The irreversible decision
> **Query and document embeddings must come from the same model.** Changing the embedding model
> means re-embedding the entire corpus - there is no migration path. Choose deliberately, record
> the model and version alongside the index, and treat a change as a full rebuild.

**Asymmetry.** Some models have separate query and document encoders, or require a prefix
(`query: ` / `passage: `). Omitting the prefix degrades retrieval substantially and silently.

**Normalisation.** Normalise vectors if using dot product as cosine. Mixing normalised and
un-normalised vectors in one index produces nonsense rankings.

**Index type.** Exact search (flat) is correct and fast enough well into the hundreds of
thousands of vectors on modern hardware. Approximate indexes (HNSW, IVF) trade recall for speed
and add tuning parameters. Do not reach for ANN before measuring that you need it.

## Cost and resource reality

Embedding is a **model inference**, with the same resource profile as any other. Locally hosted
embedding models occupy RAM continuously and consume CPU or GPU during ingestion.

> [!note] Measured in this project
> Open WebUI's default `rag.embedding_engine=""` means **local** SentenceTransformers, not a
> remote API. The Hugging Face cache held `all-MiniLM-L6-v2` (931.7 MB) and
> `whisper-large-v3-turbo` (1,547.3 MB), plus torch at 536 MB. "Our models run remotely" was
> true of chat and false of embeddings - a bulk ingestion run held ~2.9 GB and ~184% of one CPU
> core for over an hour.

## Failure modes

- **Mixed models in one index** - silently wrong similarity, no error.
- **Missing the required prefix** - degraded recall with no signal.
- **Embedding whole documents** instead of chunks - everything is vaguely similar to everything.
- **Treating similarity scores as absolute.** A cosine of 0.82 means nothing on its own; scores
  are only comparable within one model and one corpus. Use rank, or a threshold you calibrated.
- **Assuming the vector store is the bottleneck** when the chunking is the problem.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/RAG|RAG]]
- [[Coding Knowledge/03 - AI Engineering/Retrieval|Retrieval]]
- [[Coding Knowledge/03 - AI Engineering/Local vs Remote Inference|Local vs Remote Inference]]

## Sources

- Sentence-Transformers documentation - <https://www.sbert.net/>; MTEB retrieval benchmark - <https://huggingface.co/spaces/mteb/leaderboard>; Kusupati et al., "Matryoshka Representation Learning" (2022) - <https://arxiv.org/abs/2205.13147>. The Open WebUI local-embedding measurements were taken in this project on 2026-09-03.
