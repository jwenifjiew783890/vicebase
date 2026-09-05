---
type: note
domain: Coding Knowledge
section: 10 - Engineering Experience
created: 2026-09-03
---

# Engineering Trade-offs

The decisions that recur, the usual answer, and what changes it.

> [!note] These are defaults, not rules
> The value of a default is that departing from it becomes a conscious act requiring a reason.
> Every row below has legitimate exceptions.

## Design

| Trade | Usual answer | What flips it |
| --- | --- | --- |
| Simple vs flexible | **Simple** | Variation that is observed, not predicted |
| Duplication vs coupling | **Duplication**, early | Three real cases with a stable shared shape |
| Monolith vs services | **Modular monolith** | Independent deploy or scaling genuinely needed |
| Sync vs async | **Sync** | Slow work, retryable work, or decoupling needed |
| Generic vs specific | **Specific** | The third real case |
| Build vs buy | **Buy** undifferentiated | It is your core differentiator, or the vendor is a risk |
| Consistency vs availability | **Consistency** | Availability is the product, and staleness is acceptable |
| Local reasoning vs DRY | **Local reasoning** | The duplicated logic is genuinely one rule |

## Implementation

| Trade | Usual answer | What flips it |
| --- | --- | --- |
| Correct vs fast | **Correct** | Never - measure, then optimise the proven hot path |
| Readable vs clever | **Readable** | Almost never; if clever, comment the why |
| Explicit vs concise | **Explicit** | Concision that genuinely aids reading |
| Strict types vs speed of writing | **Strict** | A throwaway script |
| Library vs hand-rolled | **Library** for anything hard (crypto, dates, parsing) | A trivial need with a heavy dependency |
| Fail fast vs degrade | **Fail fast** internally, **degrade** at the user boundary | - |

## Process

| Trade | Usual answer | What flips it |
| --- | --- | --- |
| Ship now vs get it right | **Ship**, if the debt is recorded with a trigger | Data model, public API, security - these are irreversible |
| Small changes vs fewer reviews | **Small changes**, always | - |
| Test coverage vs speed of suite | **Faster suite** | The area is high-consequence |
| Document vs self-documenting | **Self-documenting**, then document the why | Operational knowledge always needs writing |
| Automate vs do it manually | **Automate on the third time** | It will genuinely not recur |

## The meta-trade: reversibility

When options are close, **choose the one that is cheaper to undo.** You can learn from a
reversible mistake; an irreversible one teaches you only that you were wrong.

This also sets the appropriate pace. Reversible decisions should be made quickly - deliberating
is more expensive than being wrong. Irreversible ones - a data model, a shard key, a public API,
a security boundary - justify slowing down and getting more input.

## How to state a trade-off honestly

1. Name the dimensions that actually matter **here**, not a generic list.
2. Say what the preferred option **gives up**, as plainly as what it gains.
3. Say **what would change the answer** - a threshold, a new requirement, a measurement.
4. Record it, so the decision can be re-evaluated on evidence rather than re-argued from scratch.

A recommendation with no stated cost is advocacy, not analysis.

---

## See also

- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]
- [[Coding Knowledge/10 - Engineering Experience/Practitioner Heuristics|Practitioner Heuristics]]
- [[Coding Knowledge/01 - Engineering Principles|Engineering Principles]]

## Sources

- Practitioner judgement. The reversibility asymmetry (one-way vs two-way doors) is widely used in engineering decision-making; the defaults here are this vault's stated position, not a citation.
