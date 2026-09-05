---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Proven Solutions

Fixes verified by real execution in this stack, with the mechanism that makes each one work.

> [!note] "Proven" means executed
> Every item here was verified by running the system and observing the result, not by reading
> the configuration. Static correctness is not evidence.

## Orchestration

**Registry-driven hub.** Agents, capabilities and permissions live in `agent-registry.json`; the
hub and the architecture map are generated from it. *Mechanism*: adding an agent is a data
change. *Verified*: registering a new agent left the hub at exactly the same node count.

**`enabled: false` for FUTURE slots.** *Mechanism*: keeps the entry out of the router and the
dispatcher allowlist, so a declared-but-unbuilt agent cannot be called. *Verified*: the
dispatcher refused a cross-domain call under attack.

**Sentinel item instead of an empty result.** *Mechanism*: n8n skips every downstream node when a
node emits nothing; a sentinel keeps the pipeline flowing. *Verified*: fixed an agent that had
been halting silently with every execution marked success.

**Explicit non-null success test.** `error !== null && error !== undefined`. *Mechanism*: a
successful sub-workflow returns `error: null`, so `=== undefined` scored every success as a
failure. *Verified*: scoring corrected.

**Named trigger reads for chained data.**
`$('When Executed by Another Workflow').first().json.knowledge`. *Mechanism*: `$json` at a prompt
node is the previous node's output, so in a multi-hop capability the knowledge block rendered
empty with no error. Naming the trigger is correct in both shapes. *Verified*: standards now
reach multi-hop capabilities.

**Structural chaining in `Prepare Stage`.** The executor supplies the previous stage's output
automatically. *Mechanism*: removes the planner's opportunity to forget. *Verified*: fixed
drafts that had been pure placeholders while reporting success.

**Registry `material_field` + `Validate Choice`.** *Mechanism*: the orchestrator knows which
field carries the substantive input for each capability, so material reaches the right place.
*Verified*: fixed `draft_notification` receiving a one-line `purpose`.

**Colon-free thrown error messages.** *Mechanism*: n8n surfaces only the text after the last
colon, so a path in the message ate the explanation. *Verified*: explanations now arrive intact.

**Fullest snapshot from `SplitInBatches` done output.** *Mechanism*: done carries one item per
iteration; `.first()` reports only stage 1. *Verified*: multi-stage runs now report correctly.

## Model calls

**`responsesApiEnabled: false` on every model node.** *Mechanism*: NVIDIA does not implement the
Responses API and returns a silent zero-token reply rather than an error.

**`timeout: 60000`, `maxRetries: 1` on every `lmChatOpenAi` node.** *Mechanism*: bounds the worst
case. *Verified*: an unbounded call hung for 302 seconds against a degraded provider; bounded, it
fails cleanly at 61 seconds.

**Plan-then-execute instead of a tool loop.** *Mechanism*: avoids the tool-result message shape
the provider rejects, and makes cost and failure attribution deterministic.

**Explicit precedence wording in the knowledge prefix.** *Mechanism*: a soft preamble lost to the
capability's own "write exactly these sections" instruction; only *these OUTRANK everything that
follows* won. *Verified*: standards are now applied.

## Integration

**Curated tool surface (2 tools, not 188).** *Mechanism*: removes `permission.reply` and the
other dangerous operations entirely, and improves tool-selection accuracy.

**Six read-only Obsidian tools, ten mutating denied.** *Mechanism*: read access is all the coding
agents need; `command_execute` in particular is a full escape.

**Dual enforcement of the project allowlist.** n8n `Resolve Project` **and** OpenCode's
`external_directory: deny`. *Mechanism*: one misconfiguration is not sufficient to escape.
*Verified*: a cross-domain write attempt was refused.

**Traversal rejected, not resolved.** *Mechanism*: no legitimate project path contains `..`, so
rejecting is strictly safer than normalising.

**`NODE_EXTRA_CA_CERTS` for the Obsidian certificate.** *Mechanism*: solves the actual problem -
the certificate is not in the trust store - while keeping verification on.

**Launcher refuses to start without `OPENCODE_SERVER_PASSWORD`.** *Mechanism*: makes the
unauthenticated state unreachable rather than merely discouraged. *Verified*: 401 on
unauthenticated requests.

## Operations

**n8n execution pruning.** `EXECUTIONS_DATA_PRUNE=true`, `MAX_AGE=168`, `PRUNE_MAX_COUNT=500`,
`N8N_LOG_LEVEL=warn`. *Mechanism*: bounds unbounded growth using the application's own mature
control rather than a custom cleanup job.

**`.wslconfig` with `memory=4GB`, `swap=2GB`, `autoMemoryReclaim=gradual`, `sparseVhd=true`.**
*Mechanism*: caps the WSL VM, returns unused memory, and lets the VHDX shrink.

**Measure with private commit, and take a CPU delta.** *Mechanism*: private commit attributes
memory correctly; a CPU delta over a fixed interval distinguishes an active job from idle
residency. *Verified*: identified a 2.9 GB "leak" as an in-flight ingestion job running at 184%
of one core.

---

## See also

- [[Coding Knowledge/10 - Engineering Experience/Proven Fixes|Proven Fixes]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Failure Modes|Known Failure Modes]]
- [[Coding Knowledge/11 - Vision & OpenCode/n8n Integration Patterns|n8n Integration Patterns]]

## Sources

- All items executed and verified in this project during 2026-09-03 work. Recorded in `D:\n8n\workflows\AGENT-REGISTRY.md`, the generator scripts, `D:\opencode\README.md`, `D:\n8n\n8n-env.ps1` and `%UserProfile%\.wslconfig`.
