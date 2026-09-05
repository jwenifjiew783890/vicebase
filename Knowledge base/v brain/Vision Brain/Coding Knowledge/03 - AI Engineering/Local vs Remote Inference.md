---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Local vs Remote Inference

Which model runs where, what each choice actually costs, and the assumption that catches people out.

## The assumption that catches people out

**"Our models run remotely" is almost never true of the whole system.** Chat inference is the
visible model; embedding, reranking, speech-to-text, OCR and image models frequently run locally
by default, and they are resident in RAM whether or not anyone is chatting.

> [!note] Measured in this project
> Open WebUI's default `rag.embedding_engine=""` means **local** SentenceTransformers. The
> Hugging Face cache held `all-MiniLM-L6-v2` (931.7 MB) and `whisper-large-v3-turbo`
> (1,547.3 MB), with torch at 536 MB - while all chat inference was remote on NVIDIA. A bulk
> ingestion run then held ~2.9 GB and ~184% of one CPU core for over an hour.
>
> When investigating resource use, **check the configuration, not the mental model.**

## The comparison

| | Local | Remote API |
| --- | --- | --- |
| **Data** | Never leaves the machine | Leaves; subject to provider terms and retention |
| **Cost** | Hardware + electricity, fixed | Per token, variable, scales with use |
| **Latency** | No network; poor on weak hardware | Network round trip; strong hardware |
| **Capability** | Bounded by VRAM/RAM | Frontier models |
| **Availability** | Yours; offline-capable | Their outages, rate limits, deprecations |
| **Idle cost** | RAM/VRAM held continuously | Zero |
| **Ops burden** | Yours: updates, drivers, serving | Theirs |
| **Determinism** | Pinned weights you control | Silent model updates |

## Choosing

**Local is right for**: small always-on models (embedding, reranking, classification, speech),
genuinely sensitive data, offline requirements, high steady volume where the per-token cost
exceeds hardware, and pinning behaviour against provider changes.

**Remote is right for**: frontier capability, bursty or low volume, avoiding operational
burden, and anything needing a very large context window.

**The common sensible split** - and the one this stack uses - is **remote for chat reasoning,
local for the small support models**. It gets frontier quality where quality matters and avoids
per-token cost on high-frequency, low-difficulty work.

## Local resource reality

- **Weights**: parameters x bytes-per-parameter. 7B at 4-bit ~ 4 GB before context.
- **KV cache** grows with context length and concurrency, and is what usually causes OOM.
- **Models stay resident** once loaded. An idle service holding two models holds their RAM all
  day - which is why "why is the machine using so much memory at idle?" so often ends here.
- **CPU-only inference is memory-bandwidth-bound** and dramatically slower than GPU.
- **Unload or lazily load** models that are used rarely, if the framework supports it.

## Operational advice

- **Know which components are local.** Enumerate every model your stack loads, and where.
- **Measure with private commit**, not working set, when attributing memory to a process.
- **Bound concurrency** on a local server, or throughput collapses instead of degrading.
- **Keep a remote fallback** for local failures, and vice versa.
- **Evaluate on your task before substituting** a local model for a remote one; quantised local
  models degrade unevenly, and code and reasoning suffer most.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Inference|Inference]]
- [[Coding Knowledge/03 - AI Engineering/Embeddings|Embeddings]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Processes & Resources|Processes & Resources]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]

## Sources

- Measurements taken in this project on 2026-09-03 from the running Open WebUI instance and the Hugging Face cache. Serving characteristics from vLLM and llama.cpp documentation.
