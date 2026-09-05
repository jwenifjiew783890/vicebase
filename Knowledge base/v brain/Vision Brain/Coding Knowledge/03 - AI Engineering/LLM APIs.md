---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# LLM APIs

The provider surface as an engineering dependency: shapes, limits, costs and the ways it fails.

## Treat the provider as an unreliable remote dependency

It is a third-party network service with rate limits, variable latency, occasional outages,
silent model updates and a metered bill. Every reliability technique in
[[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]] applies, and the ones
that matter most are timeouts, bounded retries and a fallback.

## The request surface

Most providers converge on a chat-completions shape: a list of messages with roles (`system`,
`user`, `assistant`, `tool`), sampling parameters, tool/function definitions, and a response
format specifier. "OpenAI-compatible" endpoints are common but **compatibility is partial** -
that is the single most important operational fact in this note.

Frequently incomplete in "compatible" endpoints: newer response APIs, structured-output modes,
tool-calling shapes, streaming event details, token usage fields, and system-message handling.

> [!warning] Measured in this project
> NVIDIA's OpenAI-compatible endpoint does **not** implement the newer Responses API. The n8n
> `lmChatOpenAi` node defaults to it, and the result was not an error - it was a silent
> zero-token reply. `responsesApiEnabled: false` is required on every model node.
>
> The same endpoint also rejects LangChain's tool-result message shape with
> `content.0 Input should be a valid dictionary or instance of Content`, which forced a
> plan-then-execute design instead of an agent tool loop.
>
> **Lesson**: verify each capability against the actual endpoint. "OpenAI-compatible" is a
> claim about the request format, not about the feature set.

## Limits

- **Context limit** covers input **plus** output. Reserve room for the answer, or generation is
  truncated mid-sentence.
- **Rate limits** apply per requests-per-minute *and* per tokens-per-minute; you can be limited
  while well under the request count. Respect `Retry-After`.
- **Max output tokens** is usually far below the context limit.
- Some providers cap concurrent requests separately from rate.

## Cost

Priced per input and output token, usually with output several times more expensive.
Consequently:

- Long outputs dominate the bill. Ask for the shortest sufficient answer.
- **Prompt caching** is the largest single saving for repeated system prompts and stable
  retrieved context - and it requires the stable part to come first.
- Retries multiply cost silently. So do agent loops: an unbounded loop is an unbounded invoice.
- Log token usage per call from day one. Without it, cost regressions are invisible until the
  bill arrives.

## Streaming

Server-sent events, delivering deltas. Handle: partial JSON across chunks, the terminating
sentinel, mid-stream errors (which arrive *inside* a 200 response), and client disconnects.
A stream that ends early looks like a short answer, not like a failure - check the finish reason
explicitly.

## Reliability checklist

- Explicit **timeout** on every call, sized to the expected generation length.
- **Bounded retries** with exponential backoff and jitter; retry 429 and 5xx, never 400.
- A **fallback model or provider**, and a defined degraded behaviour when all are unavailable.
- **Circuit breaker** so a provider outage fails fast instead of consuming every worker.
- **Validate the response** before using it. A truncated or malformed reply must be detected,
  not parsed optimistically.
- **Pin the model version** where the provider allows. Silent model updates change behaviour and
  will move your evaluation numbers with no code change.
- **Record `finish_reason`.** `length` means truncated; treating it as a complete answer is a
  silent data-quality bug.
- **Never send secrets or unnecessary personal data** in a prompt. It leaves your machine.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Inference|Inference]]
- [[Coding Knowledge/03 - AI Engineering/Model Routing|Model Routing]]
- [[Coding Knowledge/01 - Software Engineering/Reliability|Reliability]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]]

## Sources

- Provider API documentation (OpenAI, Anthropic, NVIDIA NIM). The NVIDIA Responses-API and tool-result-shape behaviours were measured in this project on 2026-09-03 and are recorded in `D:\n8n\workflows\AGENT-REGISTRY.md`.
