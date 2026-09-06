# Vision

A personal AI assistant that runs on your machine. One application: you
talk to it, it talks back, it remembers you, it reads your notes, it
searches the web, and it delegates real work to specialist agents.

**Install it once:**

| | |
|---|---|
| Windows | double-click `install\Install-Vision.bat` |
| macOS / Linux | `bash install/install.sh` |

That creates a private Python environment, installs everything, downloads
the models (~2.9 GB, resumable) and puts a **Vision** shortcut on your
Desktop and Start Menu. Then:

```
python -m vision            # or the Vision shortcut
python -m vision --check    # what is available, what is missing
```

---

## What it is

```
   browser  ──mic audio──▶  /api/stt  ──▶  Whisper
      ▲                                      │
      │                                   text
   speaker ◀── wav ── /api/tts ◀─ Piper     │
                                      ▲     ▼
                                      │  ┌──────────────────────────┐
                                   reply  │        Vision            │
                                      └───│  dispatch: talk or work? │
                                          └────┬────────────────┬────┘
                                     conversation            agent
                                          │                    │
                              router → retrieval →      web · knowledge
                              model → 4 honesty         memory · files
                              guards → gateway          shell · coding
                                                        research · planner
```

**The browser owns the microphone and the speaker.** The server owns the
models. That split is not an implementation detail: a headless server has
no audio hardware, and putting capture in the browser is what makes voice
work on the machine you actually sit at.

**The LLM is the component trusted least.** Routing, permissions, memory
writes and action validation are ordinary deterministic code. The model
understands and speaks; it does not decide. This is inherited from the
runtime in `vision/core/` and is the reason a 4B model is enough.

---

## Launch

```bash
pip install -r requirements.txt
python -m vision --check        # preflight
python -m vision                # http://127.0.0.1:8765
```

On Windows, `python` instead of `python3`; everything else is identical.
Full first-run instructions, including the model download, are in
[`LOCAL_RUN_AND_TEST.md`](LOCAL_RUN_AND_TEST.md).

### Configuration

Everything is an environment variable; there is no config file to edit.

| Variable | Default | What |
|---|---|---|
| `VISION_HOME` | `~/.vision` | everything persistent lives here |
| `VISION_LLM` | `~/.vision/models/Qwen3.5-4B-Q4_K_M.gguf` | the conversational model |
| `VISION_LLM_GPU_LAYERS` | `0` | raise to offload to the GPU |
| `VISION_STT_MODEL` | `small` | any faster-whisper model name |
| `VISION_TTS_EN` / `VISION_TTS_HI` | `en_US-lessac-medium` / — | Piper voices |
| `VISION_VAULT` | — | path to your Obsidian vault |
| `VISION_WORKSPACE` | `~/vision-workspace` | where the file and coding agents work |
| `VISION_PORT` | `8765` | |

---

## Models

| Role | What | Where |
|---|---|---|
| Conversation | **Qwen3.5-4B-Q4_K_M** via llama.cpp | `vision/core/llm.py` |
| Speech in | **faster-whisper** (`small`) | `vision/voice/stt.py` |
| Speech out | **Piper** (`en_US-lessac-medium`, `hi_IN-pratham-medium`) | `vision/voice/tts.py` |

**Whisper** was chosen because it is multilingual in a way that survives
code-switching. Vision's user mixes English and Hindi inside one sentence;
a monolingual recogniser forces a choice the speaker did not make.

**Piper** runs ~20x realtime on CPU, which costs nothing beside a 4B model
generating at 8 tok/s, and each voice is one self-contained ONNX file.

**The TTS voice is chosen by script, not by language,** and that is
measured rather than obvious. The runtime replies to Hindi in *romanised*
Hindi because that is how the user writes. Sent to the Devanagari voice,
"Haan yaar, main theek hoon" came back as `हान्या मेंही कुन`. Sent to the
English voice it came back as `Hanyar Main Thik Hoon` — an English accent,
but the right words, and Whisper could read it back. So Devanagari goes to
the Hindi voice and Latin goes to the English one, whatever language it
encodes.

### Replacing a model

The conversational model is a path: point `VISION_LLM` at any GGUF.
Anything larger than about 4B will not fit 6 GB of VRAM at a useful
quantisation, but it will run on CPU. STT and TTS are equally swappable —
`VISION_STT_MODEL` takes any faster-whisper name, and any Piper voice
dropped into `~/.vision/voices` is picked up on restart.

---

## Agents

Eight, not eighty. An agent earns its place when specialisation makes it
more reliable, not when it makes the diagram fuller — jobs sharing the same
tools and the same failure modes are one agent.

| Agent | Does | Gated |
|---|---|---|
| `web` | live search and page reads | |
| `browser` | drives a **real Chromium**: loads JS-rendered pages, extracts, screenshots | ✓ |
| `knowledge` | searches your Obsidian vault | |
| `memory` | reads and writes what Vision knows about you | |
| `files` | finds, reads and writes files | ✓ |
| `shell` | runs allow-listed commands | ✓ |
| `coding` | writes a script **and runs it** | ✓ |
| `research` | plans sub-queries, searches each, synthesises | |
| `planner` | breaks a goal into ordered steps | |
| `crew` | plans, **delegates to the others**, verifies what ran | |
| `desktop` | screenshots, launches apps — needs a graphical session | ✓ |
| `mcp` | calls tools from connected MCP servers | ✓ |

**An agent cannot claim what it did not do.** `AgentResult.ok` is computed
from executed steps, never asserted: an agent that ran nothing did not
succeed, and one whose steps failed did not succeed however confident its
summary reads. The coding agent writes a file and then executes it; if the
code does not run, the result is not ok. That is enforced in
`vision/agents/base.py` and is the difference between an agent harness and
a story about one.

### Adding one

```python
from vision.agents.base import BaseAgent, AgentContext, AgentResult
from vision.agents.registry import register

@register
class CalendarAgent(BaseAgent):
    name = "calendar"
    description = "Reads and writes your calendar."
    def run(self, task: str, ctx: AgentContext) -> AgentResult:
        events = self.step("cal.list", task, lambda: fetch(task), ctx)
        return self.result(f"Found {len(events)} events.")
```

Then add a routing rule to `vision/dispatch.py`. Routing is deterministic
on purpose: the model is not asked which agent to use, because that is
control flow.

---

## Plugins (MCP)

Vision speaks the Model Context Protocol, so anything with an MCP server
becomes a tool it can use. Connect one from **Plugins** in the UI, or:

```bash
curl -X POST http://127.0.0.1:8765/api/mcp/connect \
  -F name=filesystem \
  -F "command=npx -y @modelcontextprotocol/server-filesystem /path/to/dir"
```

The tools appear immediately — ask *"what tools do you have"* and Vision
lists them; name one and it runs it. MCP tools are **not** more trusted for
having arrived over a protocol: they cross the same capability gateway as
everything else.

## Long-running tasks

Work that outlasts a chat round-trip (`crew`, `research`, `browser`,
`coding`) becomes a **job**: an id, a live log, a result, and a cancel
button, all persisted. Close the tab and come back — the **Tasks** panel
shows what happened. Cancellation is cooperative and says so: a job stops
between steps, not mid-network-call. Jobs left "running" by a process that
died are marked interrupted on the next start, because a row still claiming
to run is a lie.

---

## Memory

Four tiers in one SQLite file at `~/.vision/vision.db`, and it survives
restarts — verified by stopping the process and asking again.

- **Working** — the live conversation
- **Episodic** — notes and what happened, with timestamps
- **Semantic** — facts about you, **bitemporal**: never overwritten, always
  superseded, so "you used to use helix, you switched in June" is
  answerable and stale facts cannot silently win
- **Procedural** — learned rules about how to talk to you, capped at 40

Writes are controlled rather than blanket. Extraction covers seven
predicates and refuses negations, questions, hypotheticals and third-person
statements; run over 373 real conversation turns it invented zero facts.
The Memory tab in the UI shows everything stored, and retiring a fact keeps
its history.

---

## Obsidian

Set `VISION_VAULT`, or paste the path into Settings in the UI. Vision
indexes every `.md` file (heading-aware chunking, BM25 + dense retrieval
fused with RRF) and consults it two ways: the router pulls relevant notes
into ordinary conversation when they pass a relevance threshold, and the
`knowledge` agent searches it on request.

Retrieval is threshold-gated, and when the vault has nothing the honest
answer is the one you get — injecting weak matches is worse than injecting
nothing, because the model will try to use whatever it is given.

---

## Web

Real DuckDuckGo queries with a 9-second total budget across providers. When
search returns nothing, Vision says so; it does not fill the gap. The
`NO_EVIDENCE_DIRECTIVE` and the source-claim guard exist because an earlier
version of this system confidently described what "the internet said" with
an empty context.

---

## Safety

Every capability crosses the gateway in `vision/core/gateway.py`:
permission tiers (READ / WRITE / IRREVERSIBLE / DESTRUCTIVE) map to
verdicts (ALLOW / CONFIRM / CONFIRM_TYPED / DENY), and a request arriving by
voice escalates irreversible actions to a **typed** confirmation.

Retrieved content is `Tainted` by type and can neither write memory nor
emit an action, so a web page or a note cannot instruct Vision. Routing
decides *where* a request goes; the gateway decides *whether it may
happen* — `run rm -rf /` is dispatched to the shell agent precisely so that
something with the authority to refuse actually sees it.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| `no model` at startup | `VISION_LLM` path is wrong. Vision still runs and says so. |
| Mic button does nothing | Browsers only allow `getUserMedia` on `localhost` or HTTPS. |
| STT unavailable | `pip install faster-whisper`. First use downloads the model. |
| No voices | `python -m piper.download_voices en_US-lessac-medium --data-dir ~/.vision/voices` — then check the file is ~63 MB; a truncated download fails ONNX parsing. |
| Web returns nothing | Often correct. A restricted network blocks DuckDuckGo, and Vision reports that rather than inventing results. |
| Slow | 7–8 tok/s is CPU. Set `VISION_LLM_GPU_LAYERS=20` or higher. |

---

## What was tested, and how

See [`VISION_BUILD_REPORT.md`](VISION_BUILD_REPORT.md) for the full record,
including what is **not** verified. Briefly:

```bash
python -m unittest discover -s tests -t .   # 397 unit tests
python eval/harness.py                      # 183 frozen scenario checks
python eval/mutation_audit.py               # 94 mutations
python eval/e2e/live_app.py                  # 18 checks vs the running server
python eval/e2e/capabilities.py              # 14 checks: MCP, browser, crew, jobs
python eval/e2e/browser_ui.py                # 12 checks in real Chromium
```

The end-to-end suite is the one that matters: it talks to the real HTTP and
WebSocket API of a live process, the way the browser does. Component tests
cannot tell you whether the application works — three of this project's
worst defects were green in unit tests while unreachable at runtime.
