---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# C and C++

Undefined behaviour, ownership, and the build model - the three things that account for most time lost in these languages.

## Undefined behaviour is the defining hazard

UB does not mean "unpredictable result". It means the compiler is entitled to assume it cannot
happen and to optimise on that basis. This is why UB bugs behave insanely: the code appears to
work at `-O0` and breaks at `-O2`, or a null check is deleted because a pointer was already
dereferenced above.

The common sources:

- reading uninitialised memory
- out-of-bounds access, including one past the end for reads
- use after free, double free
- signed integer overflow (unsigned wraps and is defined; signed is UB)
- shifting by >= the bit width, or by a negative amount
- strict aliasing violations - accessing an object through an incompatible pointer type
- data races - two threads, one write, no synchronisation
- null pointer dereference, including "checking after using"
- modifying a string literal

**Sanitizers are not optional.** Build tests with `-fsanitize=address,undefined` and, for
threaded code, `-fsanitize=thread`. They convert silent corruption into an immediate, located
report and are the single highest-value tool in this ecosystem. `valgrind` remains useful where
sanitizers cannot be used.

## Memory and ownership

In C, ownership is a convention that lives in comments. Document, for every function returning
a pointer, who frees it and when. Most C memory bugs are ownership ambiguity, not arithmetic.

In modern C++, ownership is expressible - use it:

- `std::unique_ptr` for single ownership (the default)
- `std::shared_ptr` only when ownership genuinely is shared; it costs atomics and creates cycles
- `std::weak_ptr` to break those cycles
- containers and `std::string` over raw buffers
- **RAII for everything with a lifecycle**: files, locks, sockets. The destructor is the only
  cleanup mechanism that survives early returns and exceptions.
- **The rule of zero**: if a class needs a custom destructor, copy constructor or assignment
  operator, it probably should be holding a type that already handles it.

Dangling references are the modern equivalent of dangling pointers: a `string_view` or
`span` outliving its buffer, or a reference captured by a lambda that escapes the scope.

## Build model

The preprocessor/compile/link separation explains most build errors:

- **"undefined reference"** is a *linker* error: declared but not defined, or the library is
  missing or in the wrong order.
- **"multiple definition"**: a definition in a header included twice; use `inline` or move it.
- **ODR violations** across translation units compiled with different flags produce silent
  corruption rather than errors.
- **ABI mismatch** between libraries built with different compilers, standard library versions
  or flags manifests as crashes far from the cause.
- Header include order and macros can change semantics - a macro named `min` will break code
  that has nothing to do with it.

## Practical defaults

- `-Wall -Wextra -Wpedantic -Werror` in CI. Most C/C++ warnings are latent bugs.
- Every input length checked; never `gets`, `strcpy`, `sprintf` on untrusted input.
- `static_assert` for compile-time invariants.
- Deterministic builds: pin the toolchain, and record the flags.
- Prefer the standard library to hand-rolled containers and algorithms.

---

## See also

- [[Coding Knowledge/02 - Programming & Languages/Memory Management|Memory Management]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Memory Problems|Memory Problems]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Build & Deployment Failures|Build & Deployment Failures]]

## Sources

- ISO C and C++ standards (behaviour summarised, text not reproduced). cppreference - <https://en.cppreference.com/>. C++ Core Guidelines - <https://isocpp.github.io/CppCoreGuidelines/>. LLVM sanitizer documentation - <https://clang.llvm.org/docs/AddressSanitizer.html>.
