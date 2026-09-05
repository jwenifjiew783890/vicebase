---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Structured Outputs

Getting a machine-parseable result reliably, in order of how much the mechanism actually guarantees.

## The methods, ranked by guarantee

**1. Constrained decoding / JSON schema mode.** The provider restricts token sampling to
grammatically valid continuations. This makes malformed output *impossible*, not unlikely. Use
it wherever available - it is categorically better than every alternative below.

**2. Tool calling as a schema.** Define one tool whose parameters are the desired shape. Widely
supported and usually well-tuned, since providers optimise tool-argument generation heavily.

**3. JSON mode.** Guarantees syntactic validity but **not** schema conformance. You still get
missing fields, extra fields and wrong types. Validate.

**4. Prompt and hope.** No guarantee. Requires extraction, repair and retry.

Regardless of method: **validate the parsed object against the schema before using it.**
Constrained decoding guarantees the shape, not that the values are sensible.

## Designing the schema

- **Flat beats nested.** Deep nesting produces more errors and is harder to repair.
- **Enums over free strings** for anything categorical. It removes a whole error class.
- **Required over optional.** An optional field will sometimes be absent for no reason.
- **Describe every field** in the schema description - the model reads them and it materially
  improves output.
- **Give it somewhere to put uncertainty.** A `confidence` field, or an explicit
  `"unknown"` enum value, prevents invention. Without an escape hatch, a model asked for a value
  it does not have will produce one.
- **Avoid unbounded arrays** without a stated limit.
- **Reasoning before the answer, in that order.** If you want a rationale, put the field *first*
  in the schema - the model generates left to right, so a rationale generated after the
  conclusion is a rationalisation, not a reason.

## Parsing defensively

Even with good methods:

- Strip markdown code fences; models wrap JSON in them habitually.
- Handle text before and after the JSON block.
- Watch for trailing commas, single quotes, `NaN`, `Infinity`, and Python-style `True`/`None`.
- **Check `finish_reason`.** `length` means the JSON is truncated - the parse error is the
  symptom, the token limit is the cause.
- On a parse failure, **return the error to the model and ask for a correction** - one repair
  attempt, not an unbounded loop.

## Failure modes

| Failure | Cause | Fix |
| --- | --- | --- |
| Truncated JSON | Hit max output tokens | Raise the limit, or ask for less |
| Extra prose around JSON | No constrained mode | Extract the block; prefer schema mode |
| Wrong types (`"5"` vs `5`) | JSON mode without schema validation | Validate and coerce explicitly |
| Hallucinated field values | No "unknown" option | Add one, and instruct its use |
| Schema drift between calls | Schema built inline in several places | One schema definition, imported |
| Fields silently dropped | Consumer ignores unknown keys | Validate strictly, log rejections |

## A rule for the whole topic

**Never `json.loads` a model response without a try/except and a schema check.** The one time it
fails will be in production, and an unvalidated parse turns a recoverable formatting error into
a crash or, worse, a wrong value flowing downstream.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/Tool & Function Calling|Tool & Function Calling]]
- [[Coding Knowledge/03 - AI Engineering/Hallucination Reduction|Hallucination Reduction]]
- [[Coding Knowledge/02 - Programming & Languages/Error Handling|Error Handling]]

## Sources

- Provider documentation on structured outputs and JSON mode (OpenAI, Anthropic). Willard & Louf, "Efficient Guided Generation for LLMs" (2023) - <https://arxiv.org/abs/2307.09702> for constrained decoding. Concepts restated, no text reproduced.
