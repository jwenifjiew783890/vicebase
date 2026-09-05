---
type: MOC
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# AI Engineering

Building systems on top of language models: how they behave, how to retrieve for them, how to constrain them, and how to know whether any of it works.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

> [!important] The discipline in one line
> A model is a **non-deterministic component with a hard context limit and no ground truth of
> its own**. Every technique here exists to compensate for one of those three properties.

## The model itself

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/03 - AI Engineering/LLM Architecture\|LLM Architecture]] | What a transformer does, and what follows from it |
| [[Coding Knowledge/03 - AI Engineering/Inference\|Inference]] | Prefill vs decode, KV cache, batching, quantisation |
| [[Coding Knowledge/03 - AI Engineering/LLM APIs\|LLM APIs]] | Provider surfaces, streaming, limits, cost, failure |
| [[Coding Knowledge/03 - AI Engineering/Local vs Remote Inference\|Local vs Remote Inference]] | When each makes sense, and what each actually costs |

## Getting the model to do useful work

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/03 - AI Engineering/Prompt Engineering\|Prompt Engineering]] | What reliably changes behaviour |
| [[Coding Knowledge/03 - AI Engineering/Tool & Function Calling\|Tool & Function Calling]] | Exposing capability, and its failure modes |
| [[Coding Knowledge/03 - AI Engineering/Structured Outputs\|Structured Outputs]] | Getting parseable results reliably |
| [[Coding Knowledge/03 - AI Engineering/Context Management\|Context Management]] | Spending a finite window well |
| [[Coding Knowledge/03 - AI Engineering/Model Routing\|Model Routing]] | Sending each request to the right model |

## Grounding it in real information

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/03 - AI Engineering/RAG\|RAG]] | The full pipeline and where it goes wrong |
| [[Coding Knowledge/03 - AI Engineering/Embeddings\|Embeddings]] | Vectors, models, dimensions, similarity |
| [[Coding Knowledge/03 - AI Engineering/Retrieval\|Retrieval]] | Chunking, hybrid search, filtering |
| [[Coding Knowledge/03 - AI Engineering/Reranking\|Reranking]] | Fixing precision after recall |
| [[Coding Knowledge/03 - AI Engineering/Agent Memory\|Agent Memory]] | What persists between sessions, and what should not |

## Making it trustworthy

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/03 - AI Engineering/Evaluation\|Evaluation]] | Knowing whether a change helped |
| [[Coding Knowledge/03 - AI Engineering/Hallucination Reduction\|Hallucination Reduction]] | Reducing confident invention |
| [[Coding Knowledge/03 - AI Engineering/AI Safety & Guardrails\|AI Safety & Guardrails]] | Injection, exfiltration, blast radius |
| [[Coding Knowledge/03 - AI Engineering/MCP\|MCP]] | The tool/context protocol this stack uses |

## Agent architecture

Planners, orchestrators, multi-agent composition and permissions have their own section:
[[Coding Knowledge/04 - Agent Engineering/00 - Agent Engineering|04 - Agent Engineering]].
