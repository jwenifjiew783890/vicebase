---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Dependency & Version Conflicts

"It worked yesterday" and "it works on my machine" - almost always a version, a resolution order, or an environment difference.

## The first question

**Which version is actually loaded?** Not which is in the manifest - which the running process
resolved. These differ far more often than people expect, and checking takes seconds:

| Environment | Command |
| --- | --- |
| Python | `python -c "import x; print(x.__version__, x.__file__)"` |
| Node | `node -e "console.log(require.resolve('x'))"`, `npm ls x` |
| Rust | `cargo tree -i <crate>` |
| Java | `mvn dependency:tree`, `gradle dependencies` |
| System | `which -a <cmd>`, `Get-Command -All` |

`__file__` and `require.resolve` answer "which copy" as well as "which version", and that is
frequently the actual bug - a local file shadowing an installed package, or a second copy in a
nested `node_modules`.

## The classes

**Diamond dependency.** A needs C>=2, B needs C<2. Resolution either fails loudly (good) or
silently picks one and breaks the other (bad). `npm` may install multiple copies; Python cannot,
so it fails or silently mismatches.

**Transitive drift.** Your direct dependencies are pinned; theirs are not. A patch release
downstream changes behaviour with no change on your side. **This is why lock files exist.**

**Shadowing.** A local file named `logging.py`, `types.py` or `email.py` takes precedence over
the standard library. Symptom: bizarre errors deep in unrelated library code.

**Environment mismatch.** Installed into a different interpreter or environment than the one
running. The most common Python confusion, resolved instantly by `python -m pip install` rather
than `pip install`.

**Native ABI mismatch.** A compiled extension built for a different Python, glibc, or compiler
version. Symptom: import errors mentioning symbols, or a segfault at import.

**Global versus local tooling.** A globally installed CLI shadowing the project's version.

## Lock files

- **Applications: commit the lock file.** It is the record of what actually worked.
- **Libraries: do not**; specify ranges, and test against the range boundaries.
- **CI must install from the lock** (`npm ci`, `pip install -r requirements.txt` from a compiled
  lock, `cargo build --locked`), or CI is testing a different dependency set than production.
- **A lock file that is regenerated on every install is not a lock file.**

## Diagnosing "it worked yesterday"

1. Did anything install or update? Check the lock file diff, and `pip list`/`npm ls` output
   against a known-good.
2. Was an unpinned dependency published? Check the package's release dates against the failure.
3. Did the base image change? `latest` tags, or a rebuilt image.
4. Did the environment change? Interpreter version, OS packages, environment variables.
5. Is there a cache involved? A stale build cache, a `__pycache__`, a `node_modules` from a
   different branch.

**The cheapest strong test: build in a clean environment.** A fresh container or a deleted and
recreated virtual environment eliminates every cached and local-state cause in one step.

## Prevention

- Pin exactly for applications, with a lock file, and update deliberately.
- Reproducible builds: pinned base images, `--locked` / `ci` installs, no network access at
  build time beyond the pinned resolver.
- Update on a schedule so the diff is small; a year of accumulated updates applied at once is
  unattributable when it breaks.
- Automated vulnerability scanning, since dependency vulnerabilities are a leading entry point.
- Minimise dependencies. Each one is a permanent maintenance and security obligation, and a
  small utility is often cheaper to write than to depend on.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Build & Deployment Failures|Build & Deployment Failures]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Regression Investigation|Regression Investigation]]
- [[Coding Knowledge/02 - Programming & Languages/Python|Python]]

## Sources

- Packaging documentation for each ecosystem (pip/PyPA, npm, Cargo, Maven). Practitioner synthesis for the diagnostic sequence.
