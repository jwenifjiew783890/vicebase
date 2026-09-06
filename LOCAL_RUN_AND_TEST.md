# Running the Vision LLM locally on Windows

Every command below corresponds to a file that exists in this repository.
Where something does not exist, the section says **NOT CURRENTLY
IMPLEMENTED** or **REQUIRES EXTERNAL MODEL/DEPENDENCY** rather than
offering a command that would fail.

Assumed: Windows, CMD, RTX 4050 Laptop 6 GB, 16 GB RAM, git installed, the
repository already cloned to `C:\Users\<username>\vicebase`.

---

## 0. The short answer to "is the LLM actually runnable?"

**Yes.** The model runs, and this document was written while it was
running: 22 multi-turn conversations were driven through the full runtime
against real weights, and the transcripts are in
`FINAL_HANDOFF\transcripts\local\`.

What you need that is **not** in this repository is the model file itself
(2.74 GB, downloaded separately) and `llama-cpp-python`.

The distinction that matters:

| | Status |
|---|---|
| Conversational runtime (routing, memory, retrieval, gateway, guards) | **In this repository.** Runs with no model and no dependencies. |
| The LLM | **REQUIRES EXTERNAL MODEL** — a 2.74 GB GGUF you download. |
| Inference engine | **REQUIRES EXTERNAL DEPENDENCY** — `llama-cpp-python`. |
| STT / TTS | **NOT CURRENTLY IMPLEMENTED** — see §9. |
| Obsidian vault | Not required. The vault used by every test is a Python dict in the code. See §8. |

---

## 1. Check Python

```cmd
cd C:\Users\<username>\vicebase
python --version
```

Needs **3.10 or newer** (3.11 is what this was developed and measured on;
the code uses `X | None` type syntax, which is 3.10+). If `python` is not
found, install from python.org and tick "Add python.exe to PATH".

---

## 2. Run everything that needs no model and no installs

Do this first. It proves the runtime works before any download.

```cmd
cd C:\Users\<username>\vicebase\personal-ai
python -m unittest discover -s tests -t .
```

Expected: `Ran 386 tests` … `OK (skipped=3)`. The 3 skips are opt-in
live-network tests, not failures. Takes about 10 seconds.

```cmd
python eval\harness.py
```

Expected: `TOTAL   183   183   100%`.

```cmd
python eval\demo.py
```

Drives the whole pipeline with a stub model — routing, language detection,
vault retrieval, the web acknowledgement, and gateway verdicts. This is the
fastest way to see the architecture work end to end without weights.

```cmd
python eval\tally.py
python eval\extractor_sweep.py
```

None of the above needs `pip install` of anything.

---

## 3. Install the inference engine

**REQUIRES EXTERNAL DEPENDENCY.**

```cmd
cd C:\Users\<username>\vicebase\personal-ai
python -m pip install -r requirements.txt
```

That installs `llama-cpp-python`, which is the only thing the runtime needs
for live inference. On Windows this may build from source and take several
minutes; if it fails, use a prebuilt wheel:

```cmd
python -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```

### Optional: build it with CUDA for the 4050

CPU works and is what every measurement in this project used. GPU is a
speed change, not a capability change.

```cmd
set CMAKE_ARGS=-DGGML_CUDA=on
python -m pip install llama-cpp-python --force-reinstall --no-cache-dir
```

This needs the CUDA Toolkit and Visual Studio Build Tools installed. If you
do not want to deal with that, skip it — everything below still works.

---

## 4. Get the model

**REQUIRES EXTERNAL MODEL.** It is not in this repository and is not in git.

Exactly which model: **`Qwen3.5-4B-Q4_K_M.gguf`**, 2,740,937,888 bytes
(2.74 GB). Read from the GGUF's own metadata, not from a document:

```
general.name              Qwen3.5-4B
general.size_label        4B
general.license           apache-2.0
general.repo_url          https://huggingface.co/unsloth
general.base_model.0      Qwen/Qwen3.5-4B
```

So: the **unsloth** GGUF quantisation of **Qwen3.5-4B**, Q4_K_M, Apache-2.0.

```cmd
mkdir C:\models
python -m pip install huggingface_hub
python -m huggingface_hub.commands.huggingface_cli download unsloth/Qwen3.5-4B-GGUF Qwen3.5-4B-Q4_K_M.gguf --local-dir C:\models
```

**Honest caveat on that repo id.** The GGUF records the *organisation*
(`huggingface.co/unsloth`) but not the repository name, and no download
command was ever recorded in this repository. `unsloth/Qwen3.5-4B-GGUF`
follows unsloth's naming convention and is the expected id — but it is
**inferred, not verified**. If it 404s, search huggingface.co for the
filename `Qwen3.5-4B-Q4_K_M.gguf` and take the unsloth result. Any
Q4_K_M GGUF of Qwen3.5-4B will behave the same.

### Where the model is expected to live

Nowhere in particular. Every script takes `--model`, and the built-in
default is the Linux path this project was developed on
(`/tmp/models/Qwen3.5-4B-Q4_K_M.gguf`), which **does not exist on
Windows**. You must pass `--model` on every command below.

---

## 5. Confirm the model loads and generates

```cmd
cd C:\Users\<username>\vicebase\personal-ai
python eval\smoke_model.py C:\models\Qwen3.5-4B-Q4_K_M.gguf
```

Prints load time, then one English and one Hindi reply with TTFT and
tokens/sec. On this project's CPU: load ~225 s cold, then **7.3–7.9 tok/s**
with TTFT 1.5–2.6 s on short prompts. On your 4050 expect substantially
faster generation; that projection is **RESEARCHED**, not measured — no GPU
was available here.

If this prints two sensible replies, everything else in this document will
work.

---

## 6. Have an actual conversation

The full battery, 22 multi-turn conversations, the same ones whose
transcripts are committed:

```cmd
python eval\local_conversations.py --model C:\models\Qwen3.5-4B-Q4_K_M.gguf --out ..\FINAL_HANDOFF\transcripts\local\my_run
```

One conversation at a time:

```cmd
python eval\local_conversations.py --model C:\models\Qwen3.5-4B-Q4_K_M.gguf --only E01 --out ..\FINAL_HANDOFF\transcripts\local\my_run
```

The frozen twenty used for every round-to-round comparison in the reports:

```cmd
python eval\mandatory_conversations.py --model C:\models\Qwen3.5-4B-Q4_K_M.gguf --out eval\transcripts\my_mandatory
```

Other harnesses, all taking `--model` the same way:

```cmd
python eval\defence_probes.py      --model C:\models\Qwen3.5-4B-Q4_K_M.gguf --out eval\transcripts\my_defence
python eval\cross_session_probe.py --model C:\models\Qwen3.5-4B-Q4_K_M.gguf --out eval\transcripts\my_xsession
python eval\learning_e2e.py        --model C:\models\Qwen3.5-4B-Q4_K_M.gguf
python eval\planner_reliability.py C:\models\Qwen3.5-4B-Q4_K_M.gguf
```

Every one writes a transcript with the turns, the routing decisions, TTFT
and tokens/sec.

### Typing at it yourself

**NOT CURRENTLY IMPLEMENTED.** There is no interactive REPL and no chat UI.
Conversations are defined as lists of turns in a harness file. To try your
own, add an entry to `CONVERSATIONS` in `eval\local_conversations.py` — the
list at the top of the file — and re-run with `--only <your id>`.

---

## 7. Entry points, precisely

**The conversational runtime entry point** is one method:

```python
Orchestrator.handle(session_id, user_text, channel) -> TurnResult
```

in `personal-ai\pai\orchestrator.py`. Everything — routing, retrieval,
memory, the planner, the gateway, the four honesty guards, the retries —
happens inside that call. `TurnResult` carries the reply plus the routing
decision, evidence count, actions, guard trips and timings.

**The LLM entry point** is `LlamaBackend` in `personal-ai\pai\llm.py`,
which wraps `llama_cpp.Llama` and is imported lazily inside the
constructor. Two adapters sit on it: `LlamaConversation` (speaks, sees
untrusted retrieved content, sampled for natural speech) and
`LlamaPlanner` (proposes typed actions, never sees retrieved content,
sampled near-greedily).

**The wiring** is `Harness` in `personal-ai\eval\conversation.py`: one
user, one memory store, many sessions. Every model-facing harness uses it.

---

## 8. What is and is not required

| | Required? |
|---|---|
| Python 3.10+ | Yes |
| `llama-cpp-python` | Only for live inference |
| The GGUF model file | Only for live inference |
| CUDA / GPU | **No.** CPU works; GPU is speed only |
| An Obsidian install or a real vault | **No** — see below |
| Internet | **No.** Web search is optional and degrades honestly |
| OpenCode | **No** — and it is not installed or tested here |
| Environment variables | **None.** Nothing reads `os.environ` |
| Config files | **None.** Everything is a CLI flag |
| A database server | **No.** SQLite, in-memory by default |

**Obsidian is not needed for any test.** `Harness` builds its vault from
`DEFAULT_VAULT`, a dict of markdown strings at the top of
`eval\conversation.py`. Retrieval is fully exercised against it — K02 in
the committed transcripts retrieves a real decision from it. To point at
your own notes you would pass `vault_notes=` to `Harness`; there is no CLI
flag for a vault directory, which is **NOT CURRENTLY IMPLEMENTED**.

**Memory does not survive the process.** `MemoryStore()` defaults to
`:memory:`. Cross-session tests work because one process runs two session
ids against one store; close the process and it is gone. To persist, pass
a filename to `MemoryStore(path=...)` — there is no CLI flag for that
either.

### Will it run on a 4050 with 6 GB?

Yes, with room. From §30 of the final report, all **RESEARCHED**:

| | VRAM |
|---|---|
| Qwen3.5-4B-Q4_K_M | ~2.5 GB |
| KV cache, 4k context | ~0.4 GB |
| Whisper-small (if voice is ever built) | ~1.0 GB |
| Embeddings | ~0.1 GB |
| **Total** | **~4.1 GB of 6 GB** |

The weights are 2.74 GB on disk and this project ran them in 16 GB of
system RAM on CPU, so the arithmetic is not in doubt. What has **never
been measured** is end-to-end latency on that GPU.

---

## 9. Voice — STT and TTS

**NOT CURRENTLY IMPLEMENTED as a runnable pipeline.**

`personal-ai\pai\voice.py` exists and is tested (22 tests), but it contains
only the parts that need no audio: semantic endpointing, clause chunking
for streaming TTS, barge-in, and the rule that an irreversible action
requested by voice needs a **typed** confirmation.

There is no microphone capture, no Whisper, no Piper, no audio device code,
and no way to speak to it. `eval\asr_test.py` is a WER harness that **has
never been run** and produces no result file; every ASR number in every
report is **RESEARCHED**. Code-switched Hindi-English ASR at ~42% WER for
monolingual models is the largest untested risk in the design.

---

## 10. If something goes wrong

**`ModuleNotFoundError: llama_cpp`** — §3. The tests do not need it; only
live inference does.

**The model path default fails** — it is `/tmp/models/...`, a Linux path.
Pass `--model C:\models\Qwen3.5-4B-Q4_K_M.gguf`.

**Web searches return nothing** — expected in a restricted network, and the
correct behaviour is that it says so instead of inventing an answer. That
is exactly what transcript `K03` records.

**It is slow** — 7–8 tok/s is CPU. See §3 for the CUDA build.

**A reply looks wrong** — read the bracketed run log in the transcript
before judging it. `evidence=0` on a reply that sounds well-sourced means
the content was invented, and three of the worst defects in this project
were invisible in the reply text alone.
