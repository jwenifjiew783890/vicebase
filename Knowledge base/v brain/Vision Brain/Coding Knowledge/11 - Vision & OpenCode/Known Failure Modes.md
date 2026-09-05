---
type: note
domain: Coding Knowledge
section: 11 - Vision & OpenCode
created: 2026-09-03
---

# Known Failure Modes

Ways this stack has actually broken. Each is a real incident, not a hypothetical.

> [!important] Why this note exists
> Every entry cost real time once. Reading it is cheaper than rediscovering any of them, and
> several were **silent** - the system reported success while producing nothing useful.

## Silent failures - the expensive class

**A node emitting zero items halted an agent, with every execution marked success.** A slow
Obsidian made a folder listing time out; the retriever returned nothing; n8n skipped every
downstream node. There was no error anywhere. *Fix*: sentinel item.

**`error === undefined` scored every success as a failure.** Successful sub-workflows return
`error: null`. *Fix*: explicit non-null check.

**`$json.knowledge` rendered empty in multi-hop capabilities.** `$json` at a prompt node is the
previous node's output, not the workflow input. The retrieved standards vanished with no error.
*Fix*: read from the named trigger.

**Stage 2 received empty context, so drafts were pure placeholders** - while every step reported
success. *Fix*: `Prepare Stage` supplies the previous output structurally.

**The knowledge preamble was ignored.** A polite "follow the standards" lost to each capability's
own "write markdown with exactly these sections". *Fix*: explicit precedence wording.

**Material never reached the field.** `draft_notification` received a one-line `purpose` instead
of the substantive input. *Fix*: registry `material_field` plus `Validate Choice`.

## Provider failures

**A silent zero-token reply from NVIDIA.** The n8n `lmChatOpenAi` node defaults to the Responses
API, which NVIDIA does not implement. Not an error - an empty answer. *Fix*:
`responsesApiEnabled: false` on every model node.

**`content.0 Input should be a valid dictionary or instance of Content`.** NVIDIA rejects
LangChain's tool-result message shape. *Fix*: plan-then-execute instead of an agent tool loop.

**A 302-second hang from one 504.** Unbounded timeout; a retry was still hanging past ten
minutes. *Fix*: `timeout: 60000`, `maxRetries: 1` - worst case now ~2 minutes, usual case an
immediate honest failure.

## Truncation and reporting

**An error message was eaten at the last colon.** n8n surfaces only the text after the final
colon, so `D:\...` in a message discarded the explanation and handed the model a fragment to
relay. *Fix*: colon-free thrown messages; the permitted roots are named in the tool description
instead.

**`.first()` on a `SplitInBatches` done output reported only stage 1** of a multi-stage run.
*Fix*: take the fullest snapshot.

## Operational

**Force-killing Docker Desktop caused ~20 minutes of downtime.** It left a stale
`sailor-ingest.sock`; containers returned on their own because of `unless-stopped`. *Lesson*:
stop a daemon through its own shutdown path.

**A PowerShell type mismatch silently dropped three processes from a memory census.**
`Win32_Process.ProcessId` is `UInt32`; `Get-Process.Id` is `Int32`. Used as a hashtable key and
looked up with the other type, the lookups simply missed - no error. *Fix*: cast `[int]`.

**A misdiagnosis of memory use.** ~2.9 GB attributed to idle waste was an **active
bulk-ingestion job**, identified by a CPU delta of 184% of one core over a 30-second sample.
Separately, "the models run remotely" was false for embeddings - local SentenceTransformers and
Whisper weights accounted for ~2.5 GB. *Lesson*: check the configuration, not the mental model,
and use the metric that discriminates.

**An orphaned scheduled task.** `Vision Backend` reported state `Ready` with
`LastTaskResult = 0xFFFFFFFF` while the process was in fact running - it had been started outside
the task's control. *Lesson*: a task's state describes the scheduler's view, not the world;
verify the process independently.

## Configuration

**A `PersistentConfig` value overrode the environment variable.** Open WebUI stores many settings
in `webui.db` on first run, after which the env var is ignored - so the change appeared to do
nothing. *Lesson*: when a config change has no effect, look for something holding a stored copy.

## The common thread

Most of these were **silent**, and most were found only because someone checked the *output*
rather than the *status*. The general defence appears throughout this domain: **assert on the
outcome, not on the absence of an error.**

---

## See also

- [[Coding Knowledge/11 - Vision & OpenCode/Proven Solutions|Proven Solutions]]
- [[Coding Knowledge/11 - Vision & OpenCode/Known Constraints|Known Constraints]]
- [[Coding Knowledge/10 - Engineering Experience/Common Failure Patterns|Common Failure Patterns]]
- [[Coding Knowledge/04 - Agent Engineering/Failure Recovery|Failure Recovery]]

## Sources

- All incidents observed in this project during 2026-09-03 work and recorded in `D:\n8n\workflows\AGENT-REGISTRY.md`, the generator scripts and the session transcripts.
