---
type: MOC
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Programming & Languages

Per-language working knowledge, weighted toward the traps that cost time rather than syntax that is easy to look up.

Part of [[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]].

> [!note] What these notes are, and are not
> They are **not tutorials**. Syntax is cheap to look up and an agent already knows it. Each
> note records the semantics that surprise people, the version-dependent behaviour, and the
> failure modes that are specific to that language.

| Note | Covers |
| --- | --- |
| [[Coding Knowledge/02 - Programming & Languages/Python\|Python]] | Mutable defaults, GIL, packaging, async, gotchas |
| [[Coding Knowledge/02 - Programming & Languages/JavaScript\|JavaScript]] | Event loop, coercion, `this`, module systems |
| [[Coding Knowledge/02 - Programming & Languages/TypeScript\|TypeScript]] | What the type system does and does not guarantee |
| [[Coding Knowledge/02 - Programming & Languages/C and C++\|C and C++]] | Undefined behaviour, ownership, build model |
| [[Coding Knowledge/02 - Programming & Languages/Rust\|Rust]] | Ownership, borrowing, error handling, async |
| [[Coding Knowledge/02 - Programming & Languages/Bash & PowerShell\|Bash & PowerShell]] | Quoting, error handling, the two object models |
| [[Coding Knowledge/02 - Programming & Languages/SQL\|SQL]] | Set thinking, indexes, isolation, plans |
| [[Coding Knowledge/02 - Programming & Languages/API Design\|API Design]] | Contracts, versioning, errors, idempotency |
| [[Coding Knowledge/02 - Programming & Languages/Async & Concurrency\|Async & Concurrency]] | The models, and where each breaks |
| [[Coding Knowledge/02 - Programming & Languages/Memory Management\|Memory Management]] | Allocation, GC, leaks, ownership |
| [[Coding Knowledge/02 - Programming & Languages/Error Handling\|Error Handling]] | Exceptions vs results, and what to do at boundaries |

## The cross-language rule

**Verify the API against the installed version.** The most frequent defect in generated code is
a call that is plausible but does not exist, or existed in a different major version. Check
before writing, not after the error.
