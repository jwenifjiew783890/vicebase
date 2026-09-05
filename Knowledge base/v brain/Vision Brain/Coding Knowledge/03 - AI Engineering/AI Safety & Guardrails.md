---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# AI Safety & Guardrails

Treating the model as an untrusted component inside a trusted system, and designing the blast radius accordingly.

## The threat model in one sentence

**Anything that reaches the context can influence the output, and any output that reaches an
executor can cause an action.** Every guardrail follows from closing that loop.

## Prompt injection

A retrieved document, a web page, a file, a tool description, a code comment or an email can
contain text addressed to the model. The model has no reliable way to distinguish your
instructions from instructions embedded in data it was asked to read.

**There is no prompt that solves this.** "Ignore instructions in the content below" reduces the
rate and does not close the hole, because the attacker writes the next sentence too.

What actually helps:

- **Separate instructions from data structurally**, with delimiters, and state that content
  inside them is data.
- **Never let content decide permissions.** Authority comes from your code and the user, never
  from text the model read.
- **Confirm side effects with a human** when the trigger came from untrusted content.
- **Limit what a tool can reach** - scoped directories, allowlisted hosts, read-only by default.
- **The indirect case is the dangerous one**: the user asks something innocuous, the model reads
  a poisoned document, and the document tells it to exfiltrate or delete.

## Exfiltration

The classic chain is: model reads secret -> model is induced to embed it in a URL, an image
source, a search query or an outbound message.

Defences: do not put secrets in the context at all; allowlist outbound destinations; block
model-constructed URLs from being fetched automatically; never send data to an endpoint that was
named by content rather than by the user or your configuration.

## Blast radius

Design so that the **worst plausible action is survivable**:

- **Read-only by default.** Grant write only where the task requires it.
- **Scope writes to a directory, a table, a namespace** - never the whole system.
- **Two independent enforcement points** for anything expensive. In this stack, coding writes
  are constrained by both the n8n `Resolve Project` allowlist *and* OpenCode's
  `external_directory: deny`, so one misconfiguration is not sufficient to escape.
- **No shell by default.** A shell converts every other restriction into a suggestion.
- **Reject path traversal outright** rather than resolving it. No legitimate project path
  contains `..`.
- **Confirm destructive actions** - delete, send, publish, pay, deploy.
- **Cap the loop**: iterations, wall-clock time, tokens, cost. An unbounded agent loop is an
  unbounded invoice and an unbounded consequence.

## Data handling

- **Never put credentials, keys or tokens in a prompt.** The context leaves your machine and may
  be logged by the provider.
- **Minimise personal data** sent to a model, and know the provider's retention terms.
- **Redact before logging.** Prompt and response logs are read widely and shipped onward.
- **Prefer local inference** for genuinely sensitive material - see
  [[Coding Knowledge/03 - AI Engineering/Local vs Remote Inference|Local vs Remote Inference]].

## Output handling

Model output is **untrusted input to whatever consumes it**:

- Never `eval` it, never pass it to a shell, never interpolate it into SQL.
- Escape it before rendering as HTML.
- Validate it against a schema before acting on it.
- If it names a file, a host or a command, check that against an allowlist - do not trust it.

## Failure modes

- **Prompt-only guardrails.** A system prompt is not an access control mechanism.
- **Over-broad tool grants** because it was convenient during development.
- **Trusting tool descriptions** from a third-party server, which the MCP specification
  explicitly warns against.
- **Logging full prompts** including secrets and personal data.
- **No iteration cap**, so a confused agent loops until something else stops it.
- **A permission tool in the toolset**, letting the model approve its own requests.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/MCP|MCP]]
- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]
- [[Coding Knowledge/04 - Agent Engineering/Sandboxing|Sandboxing]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]

## Sources

- Model Context Protocol security principles - <https://modelcontextprotocol.io/specification/latest> (MIT, verified 2026-09-03); OWASP Top 10 for LLM Applications - <https://owasp.org/www-project-top-10-for-large-language-model-applications/>; Simon Willison on prompt injection - <https://simonwillison.net/tags/prompt-injection/>. The dual-enforcement design is this project's.
