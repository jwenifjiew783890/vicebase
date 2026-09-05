---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Rust

What the borrow checker is actually enforcing, and the idioms that make it stop fighting you.

## The model

Every value has one owner. When the owner goes out of scope, the value is dropped. You may have
**either** any number of shared references (`&T`) **or** exactly one mutable reference
(`&mut T`), never both at once, and no reference may outlive the value it points to.

Those rules are the whole language design. They statically eliminate use-after-free, double
free, and data races between threads - which is why "if it compiles it usually works" is more
true here than elsewhere.

## Fighting the borrow checker usually means the design is wrong

When the checker refuses, the common causes and their real fixes:

| Symptom | Usual cause | Fix |
| --- | --- | --- |
| "cannot borrow as mutable more than once" | Two aliases into one structure | Split the borrow, use indices, or restructure |
| "borrowed value does not live long enough" | Returning a reference into a local | Return an owned value |
| Lifetime annotations spreading everywhere | Struct holding references | Hold owned data, or `Arc` |
| Needing mutation through a shared reference | Genuine shared mutability | `RefCell` (single-thread) or `Mutex`/`RwLock` (threads) |
| Cyclic structure (graph, tree with parents) | Ownership is genuinely cyclic | `Rc`/`Arc` + `Weak`, or an arena with indices |

Reaching for `clone()` to silence the checker is acceptable while learning and while
prototyping. Reaching for `unsafe` is not - `unsafe` does not disable the rules, it moves
responsibility for them onto you.

## Error handling

`Result<T, E>` and `Option<T>` are the mechanism; there are no exceptions.

- `?` propagates, converting error types via `From`.
- **Libraries**: define a concrete error enum, typically with `thiserror`, so callers can match.
- **Applications**: `anyhow::Result` with `.context("what was being attempted")` - the context
  chain is what makes a Rust error message actually diagnostic.
- `unwrap()`/`expect()` are for cases that genuinely cannot fail, and `expect` with a message
  explaining *why* it cannot fail is far better than a bare `unwrap`. In production paths,
  treat every `unwrap` as a deliberate panic.
- Panics abort the thread (or the process, if configured); they are not a control-flow mechanism.

## Async

- Futures are **lazy**: nothing runs until polled. An un-awaited future does nothing at all,
  silently.
- You need a runtime - almost always Tokio. Mixing runtimes, or calling a runtime-specific API
  under a different executor, fails at runtime rather than at compile time.
- **Blocking inside an async task starves the executor.** Use `spawn_blocking` for file I/O,
  CPU work or blocking libraries.
- `Send + 'static` bounds propagate aggressively through spawned tasks; holding a non-`Send`
  type (like `Rc` or a `RefCell` guard) across an `.await` is a common compile error and the
  fix is usually to narrow the scope of the guard.
- Cancellation is by dropping the future - so anything requiring cleanup must be
  cancellation-safe.

## Practical defaults

- `clippy` in CI; its lints are unusually high signal.
- `cargo fmt` - the formatting debate does not exist here, do not restart it.
- Derive `Debug` on everything; `Clone`/`Copy` deliberately.
- Newtypes for identifiers, so a `UserId` cannot be passed where an `OrderId` is expected.
- Iterator chains over index loops - they optimise well and eliminate bounds errors.
- `cargo test` covers unit, integration and doc tests; doc examples that compile are
  documentation that cannot rot.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Memory Management|Memory Management]]
- [[Coding Knowledge/02 - Programming & Languages/Error Handling|Error Handling]]
- [[Coding Knowledge/02 - Programming & Languages/Async & Concurrency|Async & Concurrency]]

## Sources

- *The Rust Programming Language* - <https://doc.rust-lang.org/book/> (MIT/Apache-2.0); the async book - <https://rust-lang.github.io/async-book/>; Tokio documentation - <https://tokio.rs/>. Facts restated, text not copied.
