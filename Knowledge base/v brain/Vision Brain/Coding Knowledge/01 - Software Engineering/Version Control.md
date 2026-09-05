---
type: note
domain: Coding Knowledge
section: 01 - Software Engineering
created: 2026-09-03
---

# Version Control

Using history as an investigative tool rather than a filing cabinet.

## History is a debugging instrument

The reason to care about commit hygiene is not tidiness. It is that `git bisect`, `git log -S`
and `git blame` are among the most powerful diagnostic tools available - and they only work if
each commit is a small, self-contained, working state with an explanation attached.

A history of "wip", "fix", "fix again" is a history you cannot bisect, and that costs real hours
during an incident.

## Commit practice

- **One logical change per commit.** If the message needs "and", it is two commits.
- **Each commit should build and pass tests.** Otherwise bisect lands on broken states.
- **Subject line: imperative, under ~72 chars, says what changes.** "Fix null deref in
  `parse_config`" not "fixed stuff".
- **Body: the why.** What was wrong, why this approach, what was rejected, what is still
  untested. This is the highest-value writing in the repository, because it is the only place
  the reasoning survives.
- **Never commit secrets.** Once pushed, treat the secret as compromised and rotate it -
  rewriting history does not recall what was already fetched.
- **Never commit generated artefacts, dependencies, or large binaries** unless deliberately
  vendored.

## Branching

Keep it as simple as the release process allows. Short-lived branches off a trunk, merged
often, is the default that works for almost everyone. Long-lived branches accumulate conflicts
superlinearly and delay integration problems until they are expensive.

Merge vs rebase: **rebase local work** to keep history linear before sharing; **do not rebase
anything others have pulled**. Merge commits on shared branches preserve what actually happened.

## The investigative commands

| Command | Answers |
| --- | --- |
| `git bisect start / bad / good` | Which commit introduced this? |
| `git log -S'text'` | When did this string appear or disappear? |
| `git log -L :func:file` | How did this function evolve? |
| `git blame -w -C` | Who last touched this line, ignoring whitespace and code moves? |
| `git reflog` | Where did that "lost" commit go? |
| `git diff --stat main...HEAD` | What does this branch actually touch? |

`git bisect run <script>` automates the search entirely, and turns a day's investigation into
minutes when a reliable reproduction exists.

## Recovery

Almost nothing committed is truly lost. `git reflog` finds detached commits, `git fsck
--lost-found` finds dangling objects, and a commit referenced anywhere survives until garbage
collection. Before any history-rewriting operation, note the current SHA - that one line makes
every mistake reversible.

## Failure modes

- **The giant commit.** Unreviewable, unbisectable, unrevertable.
- **Force-push to a shared branch.** Destroys other people's work and any history-based
  investigation.
- **Committing generated files.** Endless spurious conflicts.
- **Meaningless messages.** The reasoning is gone permanently; the code cannot be re-derived
  into a rationale.
- **Merging without reading the merge.** Conflict resolution is where subtle bugs enter, and it
  is rarely reviewed.
- **Long-lived feature branches.** The merge becomes an event with its own risk profile.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Regression Investigation|Regression Investigation]]
- [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]]
- [[Coding Knowledge/09 - Engineering Practices/Change Management|Change Management]]

## Sources

- Git documentation - <https://git-scm.com/docs>, particularly `git-bisect` and `git-log`. Practitioner synthesis for the commit and branching conventions.
