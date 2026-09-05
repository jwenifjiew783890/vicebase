---
type: Proposal
domain: Agents
status: PROPOSED — awaiting approval, nothing selected or installed
created: 2026-09-03
---

# Self-Improving Layer — Candidate Comparison (PROPOSED)

**Up:** [[Vision Brain]] › [[Agents/00 - Agents|Agents]] ·
Requirements: [[Agents/Self-Improving Agent Layer — Requirements]]

> [!warning] Proposed only
> This is step 2 of [[Decisions/Vision Architecture Decisions|ADR-013]] — audit, research
> and comparison. **Nothing was installed, configured or changed.** No option is selected
> until Muaz approves one.

## Audit — what `VISION — AGENTS` actually is

An **active n8n workflow** (21 nodes), the top of a three-tier hub sitting alongside 26 other
Vision workflows:

```
VISION — AGENTS                    orchestrator
  Manager (GPT-OSS 120B) → Validate Plan → Loop Stages
    → Prepare Stage → Route To Agent → Run Agent → Collect Results
  → Evaluate Results → Synthesize Answer → Format Reply

  5 specialist agents   Research · Content · Monitoring · Business · Coding
  2 hub workflows       Tool Dispatcher · Knowledge Retriever
 ~14 leaf capabilities  research_topic, code_edit, analyze_data, …
```

Findings that decide the design:

- **`Evaluate Results` already computes a deterministic per-stage record** — `succeeded`,
  `failed`, `empty`, `complete`, plus human-readable notes. The learning signal a
  self-improving layer needs **already exists**; nothing new has to be instrumented to
  detect success or failure.
- **`Knowledge Retriever` is already scoped, on-demand Obsidian retrieval** — declared
  folders → list folder → targeted note reads over the Obsidian REST API. This is the
  approved architecture, already working. No vault duplication anywhere.
- **Permission boundaries already exist.** Each agent holds an `OWNED` capability
  allowlist and validates the model's choice against it; `Tool Dispatcher` resolves against
  a registry. A model cannot invent a capability.
- **There is no memory, skill or learning machinery of any kind today.** Grep across all 27
  workflows: nothing. This is a genuine greenfield gap, not a partial implementation.

## Hermes status in this environment

**Entirely absent.** No Hermes code, no packages, no container, and **no Hermes or Nous
model available through the configured provider** (85 models; zero matches). The only local
grep hits were `hermite` polynomials in numpy. Integration status: **nothing exists.**

## Candidates evaluated

Research prototypes and papers were excluded deliberately — SkillOpt, SkillForge, WikiSkill,
EvoSkill, SkillOS and similar are arXiv work, not maintained systems, and padding the list
with them would be dishonest. Three serious projects remain.

### Hermes Agent — NousResearch

MIT · ~240k stars · 27,615 commits · very active · Feb 2026.

A **complete standalone agent**: TUI, gateways for Telegram/Discord/Slack/WhatsApp/Signal/
email, cron scheduler, subagent spawning, browser automation, its own terminal backends.
Skills are Python procedural files in `~/.hermes/skills/`; memory is a bounded
`MEMORY.md` (2,200 chars) + `USER.md` (1,375 chars) injected as a frozen prompt block, with
SQLite FTS5 session search and optional external providers (Honcho, Mem0). Memory entries
are scanned before acceptance. Works with **arbitrary OpenAI-compatible endpoints**, so our
provider and Nemotron are fine. 1–2 GB RAM, no GPU. Drivable headlessly via ACP, a gateway
JSON-RPC, an OpenAI-compatible server, or a Python in-process embed.

### OpenSpace — HKUDS (HKU Data Science Lab)

MIT · ~7.5k stars · v2 July 2026 · active.

Explicitly **"the skill management layer for AI agents"** — not a standalone agent. Plugs
into a host agent as an **MCP server** (stdio, SSE or streamable HTTP). Skills are
`SKILL.md` Markdown in discoverable directories. Evolution is **FIX** (repair a broken
skill), **DERIVED** (specialise an existing one) and **CAPTURED** (save a workflow when the
trace shows the action *and* a validated outcome). Skills carry **trust state**: provisional
by default, promoted only after independent successful use, demoted after failures; a
validated release checks the improvement before replacing a working version. Quality
tracking records selected / applied / completed / failed / fell back. LiteLLM for provider
abstraction. Python 3.12+, Node ≥20, ~50 MB, SQLite. **Runs fully local**; the community
cloud is optional, upload is disabled by default and requires an explicit command, a
`trusted` local record, and manually provisioned credentials.

### Letta (formerly MemGPT)

~24k stars · active · memory-first.

OS-inspired tiered memory (core / recall / archival) with a REST API and Python/TS SDKs;
added Skill Learning in Dec 2025. Architecturally an **agent server** — you create Letta
agents that run inside Letta. Its strength is memory, which is the requirement Vision is
already closest to satisfying (Obsidian plus the existing `vision_temporal_memory` tool).

## Comparison against the 14 requirements

| # | Requirement | Hermes | OpenSpace | Letta |
|---|---|---|---|---|
| 1 | Learns from success/failure/correction/feedback | ✅ | ✅ | ⚠️ mostly memory |
| 2 | Creates, improves, persists, reuses skills | ✅ | ✅ core purpose | ⚠️ newer, thinner |
| 3 | Persistent memory | ✅ bounded ~3.5 KB | ⚠️ skills, not memory | ✅ strongest |
| 4 | Improves workflows over time | ✅ | ✅ FIX/DERIVED/CAPTURED | ⚠️ |
| 5 | Works with our providers / Nemotron | ✅ OpenAI-compatible | ✅ LiteLLM | ✅ |
| 6 | **Sits underneath the orchestrator** | ❌ **designed to be the agent** | ✅ **by design** | ⚠️ own runtime |
| 7 | Obsidian stays source of truth | ⚠️ own memory competes | ✅ skill dir is configurable | ⚠️ own DB |
| 8 | No vault duplication | ✅ | ✅ | ✅ |
| 9 | **No second giant agent architecture** | ❌ **is exactly that** | ✅ a layer | ⚠️ a runtime |
| 10 | Reviewable / reversible / isolated | ⚠️ scanning only | ✅ trust states + validated release | ⚠️ |
| 11 | Cannot rewrite Vision core | ⚠️ has shell + browser | ✅ scope is skills | ✅ |
| 12 | Heavy executors OFF → TASK → OFF | ❌ designed to run persistently | ✅ invoked per call | ⚠️ server |
| 13 | Coexists with Islamic system, MCP, OpenCode | ✅ | ✅ MCP is already our mechanism | ✅ |
| 14 | Practical locally | ✅ 1–2 GB | ✅ ~50 MB | ⚠️ heaviest |

## The deciding argument

Hermes is the larger, more popular, more active project. It is **the wrong shape for this
requirement**, and one specific consequence settles it:

> **Hermes learns from Hermes's own work.** If `VISION — AGENTS` plans a task and routes it
> to the n8n Coding agent, Hermes never observes it and learns nothing. To make Hermes learn
> from Vision's work, Vision's work has to run *inside* Hermes — which means Hermes replaces
> the specialist agents. That is precisely what requirements 6 and 9 forbid.

OpenSpace is invoked **by** the host agent as MCP tools, so it learns from the host's tasks
while the host stays in charge. Vision already speaks MCP with three servers configured, so
this is an extension of an existing mechanism rather than a new one.

## Recommendation — **B: OpenSpace, not Hermes**

Better *fit*, explicitly not "better software". Hermes is the more impressive project; it
would require adopting a second agent architecture to obtain one feature.

Proposed minimal integration, if approved:

```
VISION — AGENTS                     unchanged, still the orchestrator
  └── Evaluate Results ─────────────► learning signal (already exists)
  └── Tool Dispatcher / agents ─────► openspace-mcp  (4th MCP server, local, stdio)
                                        skills read/written as SKILL.md files in
                                        the Obsidian vault: Agents/Skills/
```

Pointing `OPENSPACE_HOST_SKILL_DIRS` at a folder **inside the vault** means learned skills
are Obsidian notes from birth — reviewable in Obsidian, diffable, reversible, and covered by
the existing source-of-truth rule without any copying. Execution stays in Vision's existing
capability workflows; OpenSpace is used for skill discovery, capture and evolution only.

**Honest risk in this recommendation:** OpenSpace's full model expects to execute tasks via
`delegate-task`. The minimal integration deliberately uses only the discovery/capture/
evolution subset and keeps execution in n8n. Whether that subset is comfortable to use is
the main open question, and it should be settled by a throwaway spike before any commitment.
If it proves awkward, fall back to **option C** — a small Vision-native skill layer using the
same `SKILL.md` format, so nothing learned or written is wasted.

## Related

[[Agents/Self-Improving Agent Layer — Requirements]] ·
[[Decisions/Vision Architecture Decisions|ADR-013]] · [[Agents/Agent Strategy]]

---

## Spike result — 2026-09-03 — **DO NOT INTEGRATE**

A throwaway spike ran OpenSpace 2.0.0 in an isolated venv against a disposable
vault-shaped directory. The production vault and Vision were never touched.

**The proposed minimal integration is not achievable.** OpenSpace exposes six MCP tools.
`search_skills` (discovery) and `fix_skill` (FIX) work standalone, but **CAPTURED and
DERIVED — the mechanisms that learn a new skill from work — run only inside
`execute_task` step 4.** There is no standalone capture tool. Getting OpenSpace to learn
therefore requires OpenSpace to execute the task, which is what requirements 6 and 9 forbid.

Two further blockers:

- **~70 s cold start on every fresh process** (~52 s of it GroundingAgent init), not cached
  across processes. Under `OFF → TASK → OFF` every task pays it. Warm calls are <0.1 s, but
  staying warm means a resident 86–159 MB process, which is what the rule excludes.
- **Broken as shipped**: imports `mcp.server.fastmcp.FastMCP`, removed in the mcp 2.x SDK,
  while pinning `mcp>=1.0.0` unbounded. Requires pinning `mcp<2` to start at all.

What did pass: skills are Markdown + YAML frontmatter and work from a vault-shaped directory;
create/modify/version/revert are plain-file operations with a real diff, backed by lineage and
evidence tables; the cloud stayed completely off (zero non-local connections); it coexisted
with Vision, n8n and the three MCP servers without interference.

Smaller notes: writes a hidden `.skill_id` into each skill folder; 533 MB on disk against
~50 MB documented; exits with code 120 rather than 0; defaults to
`openrouter/anthropic/claude-sonnet-4.5`; its documented SSE port 8080 collides with Vision.

**Consequence:** option B is withdrawn on evidence. The remaining candidate is **option C** —
a small Vision-native layer — but that is not proposed or approved here. Nothing was
integrated and no dependency was added to Vision.

---

## Hermes component-extraction investigation — 2026-09-03 — source inspection only

Question asked: not "install Hermes" but "can its self-improving *mechanism* be
extracted and run underneath VISION — AGENTS?" Hermes cloned for reading only (MIT, 260 MB,
NousResearch/hermes-agent); nothing installed from it.

**Where self-improvement lives** — a real subsystem in `agent/` + `tools/`:
`learn_prompt.py` (skill authoring), `curator.py` (2057 ln, background maintenance),
`background_review.py` (1822 ln, review fork), `memory_manager.py` (1436 ln),
`skill_usage.py` (lifecycle telemetry), `skills_guard.py` (security scan),
`skill_provenance.py` (write-origin), `learning_graph.py` / `learning_mutations.py`
(journey graph + edit/revert).

**The loop is NOT extractable.** `learn_prompt.build_learn_prompt()` returns a **10 KB prompt
string**, not an engine — its own docstring: *"There is no separate distillation engine and no
model-tool footprint: the agent does the work with its existing toolset."* `curator.py`
*"spawns a forked AIAgent"*; `background_review.py` spawns a *"full-privilege background
subagent"*. Both import `run_agent` — the complete Hermes AIAgent runtime. So the learn →
curate → evolve loop **requires Hermes's full runtime**. Per instruction, not installed.

**What IS cleanly extractable (verified by copying each file alone into an empty dir and
importing with nothing else on the path):**

| Component | Lines | Deps | Extraction test | Reuse value |
| --- | --- | --- | --- | --- |
| `tools/skills_guard.py` | 1360 | **stdlib only** | ✅ imported alone; passed a benign skill, **blocked** an exfiltration skill | High — a real security asset |
| `tools/skill_provenance.py` | 78 | **stdlib only** | ✅ imported alone | Design pattern (write-origin) |
| `agent/learn_prompt.py` | 237 | **none** | ✅ produced a 10 KB authoring prompt | Reference prompt text |
| `agent/skill_usage.py` (lifecycle states, sidecar telemetry) | 1398 | light | pattern, not lift | Reference design |

**Q1–Q10 answers:** (1) the `agent/`+`tools/` modules above; (2) leaf utilities operate
independently, the loop does not; (3) loop → `run_agent` + `hermes_cli` + `cron` + `yaml`,
leaves → stdlib; (4) **it cannot consume our `Evaluate Results`** — the loop is driven by
Hermes's own idle/session lifecycle, there is no external event-ingestion API; (5) **yes**,
skills can live in the vault — `skills.external_dirs` config + `HERMES_HOME`, and `SKILL.md`
is an **open standard** (agentskills.io v1.0.0, 40+ platforms), not Hermes-specific; (6) the
loop needs the runtime alive to detect idleness — **not on-demand**; leaves are; (7) leaves
negligible, full runtime as previously measured; (8) `skills_guard` is itself a security
gain, but importing the loop pulls in full-privilege subagent spawning; (9) **MIT — extraction
and reuse are legally fine with attribution**; technically only the leaves are reasonable;
(10) the better mature alternative is the **open `SKILL.md` standard itself** — shared by
Hermes *and* OpenSpace *and* Claude — which decouples the format from either runtime.

**Recommendation — C, now evidence-backed.** Neither Hermes nor OpenSpace yields its learning
loop without its full runtime, and both runtimes violate the OFF→TASK→OFF and
no-second-architecture rules. The correct build is a small Vision-native layer that:
reuses the **open SKILL.md format** (portable, not a dependency); optionally **vendors
`skills_guard.py` verbatim** (MIT, attributed, stdlib-only, proven) to scan any skill before
it is trusted; borrows Hermes's **lifecycle states** (active/stale/archived/pinned, archive-
never-delete) and **provenance** (agent-written vs user-written) as design; and is driven by
the **`Evaluate Results` signal Vision already emits**, which neither external runtime can
consume. Skill authoring is a prompt to an existing Vision model — exactly Hermes's own
design — so no new runtime is needed. This is still a PROPOSAL; not built.
