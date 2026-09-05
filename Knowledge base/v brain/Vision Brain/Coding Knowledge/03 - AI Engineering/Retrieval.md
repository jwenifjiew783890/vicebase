---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Retrieval

Getting the right material in front of the model. The search strategy matters more than the model choice.

## Hybrid search is the default

Lexical (BM25) and vector search fail on opposite things:

| | Good at | Bad at |
| --- | --- | --- |
| **BM25 / keyword** | Exact terms, identifiers, rare words, error codes | Synonyms, paraphrase, conceptual queries |
| **Vector** | Paraphrase, concept, cross-vocabulary | Exact identifiers, negation, numbers |

Running both and fusing the results - Reciprocal Rank Fusion is simple and works well - is
close to a free improvement in almost every corpus. If a system only does vector search, adding
BM25 is usually the highest-return change available.

## Chunking is where most quality is decided

- **Split on structure**: headings, sections, functions, list items. Character-count splitting
  cuts sentences, tables and code blocks in half.
- **Keep chunks self-contained.** Prepend the document title and heading path to each chunk so
  it is meaningful in isolation. A chunk reading "It must be rotated every 90 days" is useless
  without knowing what "it" is.
- **Size to the answer.** If answers are typically a paragraph, chunk at a paragraph or two.
  Too small loses context; too large dilutes the embedding.
- **Overlap 10-20%** to survive boundary splits.
- **Never split code mid-function** or tables mid-row.

## Filtering before ranking

Metadata filters - domain, date, permission, document type - are cheap, exact and often more
valuable than better ranking. They are also the mechanism that keeps multi-domain retrieval
**safe**: scoping the search to one domain prevents cross-contamination between unrelated
knowledge areas, which is a correctness property, not just a relevance one.

This stack does exactly that: each agent declares its knowledge domains, and retrieval is
scoped to those folders. Nothing in the shared retrieval components names a domain, which is
what lets a new domain be added without touching them.

## Query handling

- **Rewrite conversational queries into standalone ones.** "What about the other one?" retrieves
  nothing; resolve the reference first.
- **Expand with synonyms and likely phrasings** when recall is poor.
- **HyDE**: generate a hypothetical answer and embed *that* - it often sits closer to the real
  documents than the question does.
- **Decompose multi-part questions** and retrieve for each part; a single query for a
  three-part question retrieves the average of three things.

## Assembling the context

- **Retrieve wide, rerank, cut narrow.** Top-30 or 50, rerank, keep 3-5.
- **Order deliberately.** Most relevant first *and* last, given mid-context degradation.
- **Always include the source path** with each chunk so the model can cite it.
- **Deduplicate.** Near-identical chunks waste the budget.
- **Bound by tokens**, and state what was truncated rather than silently dropping it.

## When search is the wrong tool

A structured, well-organised corpus with an index can often be **navigated** rather than
searched: read the index, follow the link, read the note. That is more accurate and far more
debuggable than similarity search, and it is why a well-maintained MOC hierarchy is a retrieval
mechanism in its own right.

Use search to *find the entry point*, then follow structure.

## Failure modes

- **Vector-only search** on a corpus full of identifiers.
- **Fixed `k`** regardless of query. Some questions need one chunk, some need ten.
- **No relevance floor** - returning the top 5 of a corpus that contains nothing relevant, and
  the model then answers from noise.
- **Unscoped retrieval across domains**, letting unrelated material contaminate an answer.
- **Ignoring recency** where the corpus contains superseded documents.
- **Silent empty result** - returning nothing where the caller treats nothing as success.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/RAG|RAG]]
- [[Coding Knowledge/03 - AI Engineering/Reranking|Reranking]]
- [[Coding Knowledge/11 - Vision & OpenCode/Obsidian Retrieval Patterns|Obsidian Retrieval Patterns]]

## Sources

- Robertson & Zaragoza, BM25 (2009). Cormack et al., "Reciprocal Rank Fusion" (2009). Gao et al., HyDE (2022) - <https://arxiv.org/abs/2212.10496>. The domain-scoping design is this project's, verified by execution.
