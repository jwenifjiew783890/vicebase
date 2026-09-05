---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# JavaScript

The runtime model and the coercion rules, which together explain most JavaScript surprises.

## The event loop

Single-threaded with a queue. Synchronous code runs to completion before any callback. Within a
tick: **all microtasks** (promise continuations, `queueMicrotask`) drain before the next
**macrotask** (`setTimeout`, I/O). A microtask that schedules another microtask starves the
macrotask queue entirely - an infinite promise chain freezes the page or the process.

`setTimeout(fn, 0)` is "after the current task and all its microtasks", never "now".

Blocking the loop blocks everything: a long synchronous loop, a giant `JSON.parse`, a
synchronous `fs` call in a server. Move heavy CPU work to a worker thread.

## Coercion and equality

- Use `===`. `==` coerces: `'' == 0`, `'0' == 0`, `null == undefined` are all true.
- `NaN !== NaN`. Test with `Number.isNaN`.
- `typeof null === 'object'` - a permanent language wart.
- `[] + {}` and friends: never rely on implicit conversion of objects.
- `0`, `''`, `NaN`, `null`, `undefined` and `false` are all falsy. Use `??` (nullish
  coalescing) when `0` or `''` are legitimate values - `||` will discard them, which is a
  frequent real bug in config handling.
- Sort is lexicographic by default: `[10, 9].sort()` gives `[10, 9]`. Always pass a comparator.
- Floating point: `0.1 + 0.2 !== 0.3`. Use integers of the smallest unit for money.

## `this` and functions

`this` is determined by **call site**, not definition, for regular functions. Arrow functions
capture `this` lexically and have no `arguments` - which makes them the right choice for
callbacks and the wrong choice for object methods that need the receiver, and for constructors.

## Async

- Every `async` function returns a promise; an uncaught rejection inside one is an unhandled
  rejection, which terminates modern Node by default.
- `await` in a loop serialises. Use `Promise.all` for independent work - but bound the
  concurrency, or 10,000 parallel requests will exhaust sockets or get you rate-limited.
- `Promise.all` rejects on the first failure and leaves the others running.
  `Promise.allSettled` when you need every outcome.
- A `forEach` callback that is `async` is not awaited - the loop finishes immediately and the
  work runs unobserved. Use `for...of` with `await`.

## Modules and packaging

ESM (`import`) and CommonJS (`require`) interoperate imperfectly: named exports from CJS are
not always statically analysable, `__dirname` does not exist in ESM, and a package's `type`
field plus its `exports` map determines what a consumer actually gets. Most "cannot find
module" and "require is not defined" errors are this boundary.

## Runtime realities

- `structuredClone` for deep copies; the `JSON.parse(JSON.stringify(x))` idiom loses
  `undefined`, `Date`, `Map`, `Set` and functions, and throws on cycles.
- Objects preserve insertion order except for integer-like keys, which sort numerically first.
- Timers are not precise; a throttled background tab clamps them heavily.
- Errors thrown across an async boundary lose their stack unless the runtime supports async
  stack traces - capture context in the message.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/TypeScript|TypeScript]]
- [[Coding Knowledge/02 - Programming & Languages/Async & Concurrency|Async & Concurrency]]
- [[Coding Knowledge/05 - Web & Application Engineering/Frontend Architecture|Frontend Architecture]]

## Sources

- MDN Web Docs - <https://developer.mozilla.org/> (content CC BY-SA 2.5; facts restated, text not copied). ECMAScript specification - <https://tc39.es/ecma262/>. Node.js documentation - <https://nodejs.org/docs/>.
