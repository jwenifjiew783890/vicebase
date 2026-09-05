---
type: note
domain: Coding Knowledge
section: 02 - Programming & Languages
created: 2026-09-03
---

# Bash & PowerShell

Two shells with different object models. Most scripting bugs are quoting, error handling, or assuming one behaves like the other.

## The fundamental difference

**Bash pipes text.** Everything is a byte stream; structure is imposed by splitting on
whitespace and newlines, which is why quoting matters so much.

**PowerShell pipes objects.** `Get-Process | Where-Object CPU -gt 10` filters real objects with
typed properties. Text formatting happens only at display time - which is why capturing
PowerShell output as text and parsing it is usually a mistake.

Conflating the two produces most cross-platform scripting failures.

## Bash: the safety preamble

```bash
set -euo pipefail
IFS=$'\n\t'
```

- `-e` exit on error - **but** it does not fire inside `if`, `&&`, `||` conditions or most
  function calls used in a test. It is a safety net, not a guarantee.
- `-u` error on undefined variable - catches typos, which otherwise expand to empty and can turn
  `rm -rf "$dir/"` into `rm -rf /`.
- `-o pipefail` - without it, a pipeline's status is the *last* command's, so a failing first
  stage is invisible.

## Bash: quoting is the whole language

- **Always `"$var"`**, never bare `$var`. Unquoted expansion word-splits and glob-expands. A
  filename with a space becomes two arguments.
- `"$@"` preserves arguments; `$*` joins them into one string. Almost always `"$@"`.
- `$(cmd)` over backticks - it nests and is readable.
- Command substitution strips trailing newlines.
- `[[ ]]` over `[ ]` in bash - no word splitting inside, and it supports `=~` and `&&`.
- Use `--` before user-supplied arguments (`rm -- "$file"`) so a filename starting with `-` is
  not read as a flag.
- `find ... -print0 | xargs -0` for filenames that may contain spaces or newlines.
- `mktemp` for temporary files, and `trap 'rm -rf "$tmp"' EXIT` to clean up on every exit path.

## PowerShell: the traps

- **`$?` and native executables.** In Windows PowerShell 5.1, redirecting a native command's
  stderr with `2>&1` wraps each line as an ErrorRecord and sets `$?` to false even on exit code
  0. Use `$LASTEXITCODE` for native commands and `$?` for cmdlets.
- **Encoding.** `Set-Content`/`Add-Content` default to the system ANSI codepage in 5.1; pass
  `-Encoding utf8` explicitly for anything another tool will read. `Out-File` and `>` differ
  again by version.
- **Version differences matter.** `&&`/`||`, ternary, `??` and `ConvertFrom-Json -AsHashtable`
  are PowerShell 7+ only and are parser errors in 5.1. Check `$PSVersionTable` before assuming.
- **`-ErrorAction SilentlyContinue` suppresses the message, not the failure.** To truly ignore,
  `try { ... -ErrorAction Stop } catch {}`.
- **Type coercion in comparisons** uses the *left* operand's type: `'10' -gt 9` compares
  strings. Cast explicitly.
- **Property type mismatch across sources.** `Win32_Process.ProcessId` is `UInt32` while
  `Get-Process.Id` is `Int32`; using one as a hashtable key and looking up with the other
  silently misses. Cast both (`[int]`) when joining data from CIM and `Get-Process`. *(Measured
  in this project - it silently dropped three processes from a memory census.)*
- Prefer `Join-Path` and `[IO.Path]` over string concatenation for paths.

## Universal rules

- **Never build a command from an unvalidated string.** Pass an argument array.
- **Check exit codes explicitly** for anything that matters.
- **Idempotence**: a script that is safe to re-run is worth far more than one that is not.
- **`--dry-run` / `-WhatIf`** for anything destructive, and default to it while developing.
- When a script grows past roughly 100 lines of logic, or needs data structures, move to Python.
  Shell is glue, not an application language.

---

## See also

- [[Coding Knowledge/06 - DevOps & Infrastructure/Linux|Linux]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Windows Services|Windows Services]]
- [[Coding Knowledge/05 - Web & Application Engineering/Web Security|Web Security]]

## Sources

- Bash reference manual - <https://www.gnu.org/software/bash/manual/>; Greg's Wiki BashPitfalls - <https://mywiki.wooledge.org/BashPitfalls>; PowerShell documentation - <https://learn.microsoft.com/powershell/>. The CIM/Get-Process type mismatch was measured in this project.
