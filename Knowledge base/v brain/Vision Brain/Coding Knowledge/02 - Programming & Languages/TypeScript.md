---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# TypeScript

What the type system actually guarantees at runtime, which is less than most people assume.

## The central fact

**Types are erased at compile time.** There is no runtime checking whatsoever. A value typed
`User` that arrives from an HTTP response is only a `User` because you said so - if the server
sends something else, the program runs happily with a lie until it crashes somewhere unrelated.

Therefore: **validate at every boundary** - network responses, `JSON.parse`, environment
variables, file contents, user input - with a runtime validator (Zod, Valibot, io-ts, or a hand
written type guard). Everything inside the boundary can then trust its types.

`as` is an assertion, not a check. `as any` and `as unknown as T` disable the type system
exactly where it was about to be useful. Each one is a place a runtime error will originate.

## Compiler settings that matter

`strict: true` is the baseline. Without `strictNullChecks` in particular, `null` and `undefined`
are assignable to everything and the type system catches very little.

Also worth enabling: `noUncheckedIndexedAccess` (makes `arr[i]` correctly `T | undefined` -
catches a real class of bug), `noImplicitOverride`, `exactOptionalPropertyTypes`.

## Practical typing

- **Prefer inference.** Annotate function parameters, return types of exported functions, and
  little else. Over-annotation makes refactoring painful without adding safety.
- **Discriminated unions over optional fields.** `{status:'ok', data:T} | {status:'error',
  error:string}` makes the invalid combination unrepresentable, where `{data?:T, error?:string}`
  permits both and neither.
- **`unknown`, not `any`,** for genuinely unknown input; it forces a narrowing check.
- **Type guards** (`function isUser(x: unknown): x is User`) connect a runtime check to the
  type system. Note the compiler does not verify the guard is correct - a wrong guard is a
  silent lie.
- **`readonly` and `as const`** to prevent accidental mutation and to narrow literal types.
- **Template literal types, `satisfies`, and mapped types** are genuinely useful for config and
  route definitions. They are also where type-level code becomes unreadable - if a type needs a
  comment to explain what it computes, prefer the simpler version.
- **Utility types**: `Partial`, `Pick`, `Omit`, `Record`, `ReturnType`, `Awaited`. Deriving
  types from a single source keeps them from drifting.

## Failure modes

- **Trusting parsed JSON.** `JSON.parse` returns `any`; the type after it is fiction.
- **Assertion instead of validation.** `as User` on an API response.
- **`any` spreading.** One `any` propagates through every downstream inference silently.
- **Enum surprises.** Numeric enums allow arbitrary numbers and are not fully type-safe; string
  literal unions are usually better.
- **`@ts-ignore` left in place.** It suppresses the error and everything after it on that line.
  `@ts-expect-error` at least fails when the underlying problem is fixed.
- **Structural typing surprises.** Two unrelated types with the same shape are interchangeable.
  Use a branded type when identity matters (`type UserId = string & {__brand:'UserId'}`).
- **Declaration files that lie.** A hand-written or outdated `.d.ts` for a JS library describes
  an API that may no longer exist.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/JavaScript|JavaScript]]
- [[Coding Knowledge/02 - Programming & Languages/API Design|API Design]]
- [[Coding Knowledge/01 - Software Engineering/Testing|Testing]]

## Sources

- TypeScript Handbook - <https://www.typescriptlang.org/docs/handbook/>; `tsconfig` reference - <https://www.typescriptlang.org/tsconfig>. Facts restated, text not copied.
