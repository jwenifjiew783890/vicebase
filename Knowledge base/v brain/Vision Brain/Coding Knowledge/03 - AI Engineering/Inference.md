---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Inference

What actually happens when a request is served, and which knobs change latency, throughput and memory.

## Two phases with different characteristics

**Prefill** processes the whole prompt in parallel. It is compute-bound, and its cost scales
with prompt length. It determines **time to first token**.

**Decode** generates one token at a time, each step requiring a full pass over the model
weights. It is memory-bandwidth-bound, and its cost scales with output length. It determines
**tokens per second**.

Consequences: a long prompt with a short answer is prefill-dominated; a short prompt with a long
answer is decode-dominated. Optimising the wrong one wastes effort - and it is why "the prompt
is too long" and "the answer is too slow" are different problems.

## KV cache

Attention keys and values for processed tokens are cached so decode does not recompute them.
The cache is the dominant runtime memory cost and it grows linearly with context length and
batch size. Running out of KV cache - not model weights - is the usual cause of out-of-memory
under concurrency.

**Prompt caching** (provider-side) reuses the prefill of a shared prefix across requests. It
substantially cuts cost and latency, and it changes prompt design: put the stable material
(system prompt, tool definitions, retrieved corpus) at the **front**, and the varying material
at the end. Reordering a prompt can silently destroy the cache hit rate.

## Batching

Continuous batching (as in vLLM and similar servers) inserts new requests into a running batch
rather than waiting for a batch to finish. It raises throughput enormously at some cost to
individual latency. This is why a self-hosted server with one user is inefficient - most of the
hardware sits idle.

## Quantisation

Reducing weight precision (FP16 -> INT8 -> INT4) cuts memory and raises speed, at some quality
cost.

- 8-bit is usually near-lossless for most tasks.
- 4-bit is often acceptable, with measurable degradation on reasoning and code.
- Quality loss is task-dependent - **evaluate on your task**, not on a published benchmark.
- Memory rule of thumb for weights: parameters x bytes-per-parameter, plus KV cache, plus
  activation overhead. A 7B model at 4-bit needs roughly 4 GB for weights alone, before context.

## Latency budget

Total = network + queue + prefill + (output tokens x per-token time) + parsing.

- **Streaming** does not reduce total time; it reduces *perceived* time by delivering the first
  token early. Use it for anything user-facing.
- **Output length is the biggest lever** on latency. "Be concise" is a performance optimisation.
- Queue time is invisible in client-side timing but real; measure it separately.

## Failure modes

- **Unbounded timeouts.** A stalled provider hangs the caller for as long as it likes. Set an
  explicit timeout and a retry cap. *(Measured in this project: one unbounded call to a
  degraded provider hung for 302 s.)*
- **Retrying a long generation.** Three attempts at a 60-second generation is a three-minute
  stall. Cap total attempt time, not just attempt count.
- **Context overflow at request time**, discovered in production because input length was never
  bounded. Count tokens before sending.
- **Concurrency exhausting KV cache** on a self-hosted server - throughput collapses rather than
  degrading gracefully. Bound concurrent requests.
- **Assuming determinism.** Even at temperature 0, batching and GPU non-associativity vary
  output. Never assert exact equality in tests.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/LLM APIs|LLM APIs]]
- [[Coding Knowledge/03 - AI Engineering/Local vs Remote Inference|Local vs Remote Inference]]
- [[Coding Knowledge/03 - AI Engineering/Context Management|Context Management]]

## Sources

- vLLM documentation on continuous batching and paged attention - <https://docs.vllm.ai/>; Kwon et al., "Efficient Memory Management for LLM Serving with PagedAttention" (2023) - <https://arxiv.org/abs/2309.06180>; provider documentation on prompt caching. The 302-second stall was measured in this project.
