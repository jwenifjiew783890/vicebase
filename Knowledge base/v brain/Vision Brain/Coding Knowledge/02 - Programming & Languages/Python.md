---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Python

The semantics that surprise, the packaging model, and the performance realities.

## Semantics that bite

**Mutable default arguments.** `def f(items=[])` creates the list **once**, at definition time,
and every call shares it. Use `None` and build inside. This is the most common Python bug in
generated code.

**Late binding in closures.** `[lambda: i for i in range(3)]` gives three functions all
returning `2`. Bind with a default: `lambda i=i: i`.

**Identity vs equality.** `is` compares identity. It works for small ints and short strings by
accident of interning, and then fails on the real data. Use `==`, and `is` only for `None`,
`True`, `False`.

**Truthiness of empty containers.** `if items:` is false for both `None` and `[]`. When the
distinction matters - absent versus empty - test `is None` explicitly.

**Shallow copy.** `list(x)`, `x[:]` and `dict(x)` copy one level. Nested structures stay shared.
`copy.deepcopy` for the rest, and know it is slow.

**Exception scope.** In Python 3, the name bound by `except E as e` is deleted at the end of the
block. Assign it elsewhere if you need it after.

**Integer division and floats.** `/` is always float; `//` floors toward negative infinity, so
`-7 // 2 == -4`. `round()` uses banker's rounding: `round(0.5) == 0`. Use `decimal.Decimal` for
money, never `float`.

**Iterators are consumed.** A generator, `map`, `filter` or `zip` object yields once. Iterating
twice silently produces nothing the second time.

**Modifying while iterating** a list or dict raises or skips elements. Iterate a copy.

## Concurrency

The **GIL** means threads do not run Python bytecode in parallel. Therefore:

- **I/O-bound** work: threads or `asyncio` both work well.
- **CPU-bound** work: `multiprocessing` or a native extension that releases the GIL. Threads
  will not help.
- Free-threaded builds (PEP 703, 3.13+) exist as an option, but assume the GIL unless the
  deployment explicitly uses a free-threaded interpreter.

`asyncio`: one blocking call in a coroutine blocks the entire event loop, including every other
task. Use `run_in_executor`/`asyncio.to_thread` for blocking work. Always `await` or store a
task - a bare `create_task` result that is garbage collected can cancel silently, and
`asyncio.gather` propagates the first exception while leaving the rest running unless handled.

## Packaging and environments

- **Always a virtual environment.** `venv`, or a manager like `uv` or `poetry`.
- **Pin for applications** (a lock file); **range for libraries**.
- `pip install -e .` for local development.
- Import errors are usually one of: not installed in *this* interpreter, a name shadowing a
  stdlib or installed module (a local `logging.py`), a missing `__init__.py` in an intended
  package, or a circular import.
- `python -c "import x; print(x.__file__)"` answers "which one am I actually importing?" and
  resolves a large share of import confusion.

## Performance

- Attribute lookup, function calls and interpreter dispatch dominate tight loops. Hoist lookups
  out of loops.
- Prefer built-ins and comprehensions - they run in C.
- String concatenation in a loop is quadratic; build a list and `''.join()`.
- `dict`/`set` membership is O(1); `list` membership is O(n). Scanning a list inside a loop is
  the classic accidental O(n^2).
- Profile with `cProfile` for call counts, `tracemalloc` for allocations, `py-spy` for a live
  process without instrumenting it.

## Practical defaults

- Type hints on every public function; run `mypy` or `pyright` in CI. They catch a large class
  of defect at no runtime cost.
- `pathlib.Path` over string paths, especially on Windows.
- `logging`, never `print`, in anything long-lived.
- `dataclasses` or `pydantic` over dicts for structured data - a typo in a dict key is a runtime
  surprise, in a dataclass it is a static error.
- Context managers for anything with a lifecycle. `with` is the only reliable way to guarantee
  cleanup.
- `subprocess.run([...])` with a list argument, never `shell=True` with an f-string.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Async & Concurrency|Async & Concurrency]]
- [[Coding Knowledge/02 - Programming & Languages/Memory Management|Memory Management]]
- [[Coding Knowledge/02 - Programming & Languages/Error Handling|Error Handling]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Dependency & Version Conflicts|Dependency & Version Conflicts]]

## Sources

- Python documentation - <https://docs.python.org/3/>, particularly the language reference and `asyncio` docs. PEP 703 (free-threaded CPython) - <https://peps.python.org/pep-0703/>. Facts restated; no text reproduced.
