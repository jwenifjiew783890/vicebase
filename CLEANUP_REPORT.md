# Repository cleanup — removing the GTA VI site

**Date:** 2026-09-06
**Branch:** `claude/conversational-llm-architecture-a13xti`
**Cleanup commit:** `db64c8b`

The repository held two unrelated projects: a GTA VI fan site
(`vicebase`) and the personal AI runtime. The site is removed. This report
records what went, what stayed, why, and what was run to prove the runtime
survived intact.

---

## 0. One finding before anything else

The instructions asked me to preserve the **"Vision knowledge base"** and
the **"Vision Brain"**, and not to delete **"Obsidian-related
knowledge/memory material"**.

**No file, folder, or branch named `vision`, `brain`, or `knowledge` exists
in this repository.** I searched filenames and file contents across all
branches (`main`, `claude/conversational-llm-architecture-a13xti`, and both
remotes). The string "vision" appears four times, every one of them inside
the words *supervision* and *revision* in the research documents.

I did not guess which files were meant. I interpreted the instruction by
capability rather than by name, and preserved:

- **`personal-ai/pai/memory.py`** (574 lines) — the four-tier bitemporal
  memory store. The closest thing to a "brain".
- **`personal-ai/pai/obsidian.py`** (355 lines) — Obsidian vault retrieval,
  heading-aware chunking, BM25 + dense with RRF fusion.
- **`personal-ai/pai/learning.py`**, **`extract.py`**, and every associated
  test, fixture and transcript.

All are untouched. **If "Vision Brain" or "Vision knowledge base" refers to
something that lives elsewhere — another repository, a local folder, or work
not yet committed — it was never in this repository and this cleanup could
not have removed it.**

---

## 1. What was removed

**52 files**, all of them the GTA VI site.

| Path | Files | Contents |
|---|---:|---|
| `app/` | 11 | Next.js routes: home, characters, `[slug]`, vehicles, weapons, map, trailers, gameplay |
| `components/` | 10 | `Hero`, `Navbar`, `Footer`, `NewsSection`, `StorySection`, `CharacterGrid`, `CharacterHero`, `CharacterInfo`, `Charactercard`, `FeaturedCreators` |
| `data/` | 5 | `characters.ts` (Lucia Caminos, Jason, Cal, Raul…), `creators.ts`, `news.ts` ("GTA VI Trailer 2 Released"), `story.ts`, empty `media.ts` |
| `types/` | 2 | `Character`, `Creator` interfaces |
| `public/` | 17 | Character photographs, hero background, news screenshots, next/vercel/window SVGs |
| toolchain | 6 | `package.json`, `package-lock.json`, `next.config.ts`, `tsconfig.json`, `postcss.config.mjs`, `eslint.config.mjs` |
| root | 1 | `AGENTS.md` |

### Why each category went

**`app/`, `components/`, `public/`** — Next.js UI for a game companion
site. No AI, LLM, memory, retrieval or agent content; I grepped for all of
those terms across every file and got zero hits.

**`data/`, `types/`** — the site's content model. Inspected rather than
assumed: `characters.ts` is a list of GTA VI characters with slugs and
portrait paths. Nothing in `personal-ai/` reads any of it.

**Node toolchain** — `package.json` declares only `next`, `react`,
`react-dom`, `lucide-react`, `tailwindcss` and `eslint-config-next`. Its
scripts (`dev`, `build`, `start`, `lint`) exist solely to serve the site.
The runtime is pure Python standard library, so removing these takes away
nothing it uses.

**`AGENTS.md`** — its entire content was a Next.js instruction block telling
agents to read `node_modules/next/dist/docs/` before writing code. With the
framework gone that instruction is not merely useless but actively
misleading, which is why it was removed rather than left in place.

---

## 2. What was preserved

| Path | Why |
|---|---|
| `personal-ai/` (entire) | The runtime: 14 modules, 374 tests, 21 eval harnesses, 110 transcripts, committed audit evidence, all reports including superseded ones |
| `FINAL_HANDOFF/` (entire) | The portable record of the whole project |
| `docs/` | **The case the instructions warned about.** A generic name at the root, beside the site's files — and its two documents are the R&D evaluation and the architecture design that the entire runtime implements |
| `LICENSE` | MIT, applies to all work in the repository, not site-specific |
| `README.md`, `CLAUDE.md`, `.gitignore` | Kept as files, rewritten as content — see §4 |

### Specifically preserved, per the instructions

Conversational learning (`learning.py`, `signals.py`), memory and
personalisation (`memory.py`, `extract.py`), anti-sycophancy
(`test_sycophancy_pressure.py` and the A05 transcripts), routing
(`router.py`), the capability gateway (`gateway.py`), orchestration
(`orchestrator.py`), evaluation (all 21 harnesses and 110 transcripts), and
security (`trust.py`, `eval/data/injection_corpus.py`,
`test_gateway.py`). **None of it was touched.**

---

## 3. Ambiguous cases

Five things were not obvious. The rule applied was: if ambiguous, keep.

**1. `docs/` at the repository root — KEPT.** The name suggests site
documentation and the location sits beside the site's own files. The
contents are `conversational-llm-architecture.md` (the 680-line R&D
evaluation) and `personal-ai-architecture.md` (the 519-line design). Judging
this one by its path would have deleted two of the project's four current
reports.

**2. Next.js strings inside `personal-ai/eval/defence_probes.py` — KEPT
UNCHANGED.** The file contains stub web-search results about Next.js
releases. These are *test fixtures* — plausible fake search results used to
probe the web path — not application code. They are also frozen test data:
editing them would break comparability between measured rounds. A grep for
"next.js" in the runtime finds only these, and they are the reason the
dependency check needed reading rather than counting.

**3. `AGENTS.md` versus `CLAUDE.md` — one deleted, one rewritten.**
`AGENTS.md` was entirely Next.js rules. `CLAUDE.md` contained only
`@AGENTS.md`, but it is the entry point agents actually read, so deleting it
would leave the repository with no instructions at all.

**4. `data/media.ts` — DELETED.** Zero bytes. Empty, but unambiguously in
the site's namespace.

**5. `.gitignore` — REWRITTEN, not deleted.** Discussed in §4.

---

## 4. Documentation updated

**`README.md`** described "The Ultimate GTA VI Companion Platform" in two
lines. It now describes the runtime, the architectural claim, the measured
state, how to run the checks without a model, and how to read the evidence
labels.

**`CLAUDE.md`** instructed agents to read Next.js documentation. It now
states that this is a Python project, that stale Next.js instructions should
be reported rather than followed, and carries the five rules that matter
here — evidence labels are load-bearing; a passing test is not evidence; do
not edit source or commit while the mutation audit runs; the LLM is trusted
least; numbers in prose drift, so verify them.

**`.gitignore`** was the stock Node file. It is now Python, and
**deliberately does not ignore `logs` or `*.log`**. Those two rules had
already caused a near-miss: an attempt to commit raw mutation-audit output
to `eval/logs/` would have silently added nothing while the report pointed
at it. Raw run output is evidence in this project and belongs in git. The
new file says so, in the file, so the next person does not re-add them.

**`FINAL_HANDOFF/INDEX.md` and `code/CODE-MAP.md`** each contained a
sentence describing the Next.js app as present. Those sentences were updated
to record the removal rather than deleted, so the handoff stays accurate
without losing the history.

---

## 5. Dependency analysis

Checked in **both** directions before deleting anything.

| Check | Result |
|---|---|
| Python under `personal-ai/` importing or reading `app/`, `components/`, `data/`, `types/`, `public/` | **None** |
| TypeScript referencing `personal-ai/` or `pai/` | **None** |
| Eval fixtures loading site data files | **None** — the Obsidian `VAULT` fixture is an inline Python dict in `eval/harness.py` and `eval/demo.py` |
| Third-party Python imports | Only `llama_cpp` (lazy, inside a function, for live inference) and `soundfile` (in `asr_test.py`, which has never been run) |
| Tracked files newly hidden by the rewritten `.gitignore` | **None** — verified with `git check-ignore` over every tracked path |

**Nothing broke, because nothing was connected.** The two projects shared a
git remote and no code.

---

## 6. Tests executed, and results

Every check was run **before** the cleanup to establish a baseline and
**after** it to detect drift.

| Check | Before | After | |
|---|---|---|---|
| Unit tests | 374 passed, 3 skipped | **374 passed, 3 skipped** | identical |
| Frozen scenario checks | 183 / 183 | **183 / 183** | identical |
| Extractor sweep | 373 turns, 4 facts, 0 retractions | **373 turns, 4 facts, 0 retractions** | identical |
| Transcript tally | 110 transcripts, 373 turns | **110 transcripts, 373 turns** | identical |
| All 14 modules import | — | **OK** | |
| End-to-end pipeline (`eval/demo.py`) | — | **OK** | |
| Mutation audit | 88 / 88 | **88 / 88, 0 survived** | identical |

### The end-to-end run is the one that proves it functions

`eval/demo.py` drives the whole pipeline with a stub model. After cleanup it
still routes correctly across all four paths, detects language, retrieves
from the vault, acknowledges a slow web search, and gates actions:

```
hey                                    fast      en   -
what did we decide about auth          grounded  en   vault x1
what's the latest nextjs version       web       en   ack='one sec, checking'; ran web.search[EMPTY]
kya haal hai                           fast      hi   -
open opencode and fix the failing test action    en   code.delegate -> CONFIRM
delete the old notes                   action    en   file.delete -> CONFIRM_TYPED
```

A green test suite does not prove the code is reachable at runtime — that
mistake is the central lesson of this project (§3 of the final report,
where three requirements were marked passing while their components were
unreachable). This run is what rules it out here.

### Lint and type checks

**Not applicable, and removed on purpose.** The only linter and type checker
in the repository were `eslint-config-next` and `tsc`, both of which existed
to check the deleted TypeScript. The runtime is Python with no configured
linter; `python3 -m unittest` and the mutation audit are its checks. Adding
a Python linter would be new work, which this task explicitly excludes.

---

## 7. Issues discovered and fixed

**1. Two false statements in the handoff.** `FINAL_HANDOFF/INDEX.md` and
`code/CODE-MAP.md` both told the reader the repository contains a Next.js
app. True when written, false the moment the cleanup landed. Fixed by
updating both to record the removal and its date.

**2. `.gitignore` would have hidden future evidence.** Carried over from
§4: the Node ignore rules for `logs` and `*.log` had already nearly
swallowed committed audit output once. The rewritten file drops them and
explains why in a comment.

No issue was found that required a code change. Nothing broke.

---

## 8. Remaining limitations

Unchanged by this cleanup, and none of them caused by it:

- **No GPU.** Every RTX 4050 latency figure is RESEARCHED, not measured.
- **No audio device.** Voice policy is fully tested; every audio model
  (Whisper/Parakeet WER, TTS naturalness, end-to-end voice latency) is
  untested. Code-switched Hindi-English ASR is the biggest open risk.
- **`eval/asr_test.py` has never been run** and produces no result file.
- **OpenCode is not installed.** The client is tested against a real local
  HTTP server, never against OpenCode itself.
- **The 180-day drift result is SIMULATED**, not measured.
- **No Python linter or type checker is configured.** Removing the Node
  toolchain leaves the repository without static analysis. Adding one is
  reasonable future work and was out of scope here.

The full list is `FINAL_HANDOFF/status/LIMITATIONS.md`.

---

## 9. Final repository structure

```
.
├── CLAUDE.md               agent instructions -- rewritten for Python
├── CLEANUP_REPORT.md       this file
├── LICENSE                 MIT
├── README.md               rewritten: the runtime, not the site
├── .gitignore              rewritten: Python, and does NOT ignore logs
│
├── docs/                   the R&D evaluation and the architecture design
│   ├── conversational-llm-architecture.md
│   └── personal-ai-architecture.md
│
├── personal-ai/            THE RUNTIME
│   ├── pai/                14 modules, 5,736 lines
│   ├── tests/              374 tests across 16 files
│   ├── eval/               21 harnesses
│   │   ├── transcripts/    110 transcripts, 373 real user turns
│   │   ├── evidence/       raw mutation-audit output
│   │   └── data/           scenarios, injection corpus
│   └── docs/               reports, including superseded ones kept on purpose
│
└── FINAL_HANDOFF/          portable record of the whole project
    ├── INDEX.md
    ├── reports/  evidence/  transcripts/  status/  code/  specs/
```

**Tracked files: 401 → 351** (349 after the 52 deletions, plus this report
and the post-cleanup audit log). Everything removed remains recoverable from
git history at `0a3ef88` and earlier.

---

## 10. Confirmation

The personal AI runtime is intact and verified.

- Every module imports.
- **374 tests pass**, identical to the pre-cleanup baseline.
- **183 / 183** frozen scenario checks pass.
- **88 mutations applied, 88 killed, 0 survived, 0 anchors drifted** —
  a full audit re-run against the cleaned tree. Raw output committed at
  `personal-ai/eval/evidence/mutation_audit_88_post_cleanup.txt`.
- The full pipeline runs end to end: routing, language detection, vault
  retrieval, web acknowledgement, and gateway verdicts including
  `file.delete → CONFIRM_TYPED`.
- Memory, learning, extraction, Obsidian retrieval, routing, orchestration,
  the gateway, security and every evaluation artifact are untouched.

No Vision functionality was removed. Nothing that was removed was ever
referenced by it.
