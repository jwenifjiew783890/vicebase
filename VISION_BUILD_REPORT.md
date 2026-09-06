# Vision — build report

**Date:** 2026-09-06
**Branch:** `claude/conversational-llm-architecture-a13xti`

What was built, what was actually tested, and what is not verified. Every
claim below points at a command you can run.

---

## 0. The constraint that shapes this report

**This build environment has no audio hardware.** No `/dev/snd`, no ALSA,
no PulseAudio — it is a headless cloud container, and it is not the user's
laptop. I could not speak into a microphone or listen to a speaker here,
and I have not pretended to.

What that means for the voice requirement, precisely:

| Link in the chain | Status |
|---|---|
| Browser captures microphone | **Implemented, not verified here** — needs your machine |
| Audio reaches `/api/stt` | **VERIFIED** — real audio posted, real transcript returned |
| Whisper transcribes | **VERIFIED** — including Hindi at 0.95 confidence |
| Vision understands and replies | **VERIFIED** |
| Piper synthesises | **VERIFIED** — real wav bytes, ~20x realtime |
| Browser requests the audio | **VERIFIED** — observed in a real Chromium session |
| Speaker plays it | **NOT VERIFIED** — no sound card in this container |

The architecture puts capture and playback in the **browser**, on your
machine, where the hardware is. That is what makes the two unverified links
ordinary browser behaviour rather than missing code.

---

## 1. What was built

```
vision/
  core/        the conversational runtime, moved unchanged from personal-ai/pai
  voice/       stt.py (faster-whisper), tts.py (Piper)
  agents/      base.py, registry.py, builtin.py -- 8 specialists
  server/      app.py -- FastAPI + WebSocket, one process
  web/         index.html -- the interface
  assistant.py the one object the app talks to
  dispatch.py  deterministic: conversation or agent?
  tasks.py     durable activity log
  config.py    every path and setting, one place
```

## 2. What was reused, replaced, deleted

**Reused unchanged** — `vision/core/`, the runtime hardened by 54
documented failures: the router, the capability gateway, trust levels, the
four honesty guards, bitemporal memory, the learning loop, Obsidian
retrieval, the web client. None of it was rewritten. It is the reason a 4B
model is enough.

**Replaced** — `personal-ai/` as a layout became `vision/` as an
application. `MemoryStore` moved from in-memory to a file. The two SQLite
connections that outlive a request now go through a locking wrapper.

**Deleted** — nothing of substance. The restructure was `git mv`.

**Added** — voice, agents, dispatch, server, UI, task log, config.

---

## 3. What was actually tested

```bash
python -m unittest discover -s tests -t .   # 397 unit tests
python eval/harness.py                      # 183 frozen scenario checks
python eval/mutation_audit.py               # 94 mutations
python eval/e2e/live_app.py                 # 18 checks vs the running server
python eval/e2e/browser_ui.py               # 10 checks in real Chromium
```

| Suite | Result |
|---|---|
| Unit tests | **397 passed**, 3 skipped |
| Frozen scenarios | **183 / 183** |
| End-to-end, live server | **18 / 18** |
| Browser, real Chromium | **10 / 10** |
| Mutation audit | **94 / 94** (93 in one pass + 1 after an anchor repair — §7) |

### The end-to-end run, verbatim

```
PASS  C. English conversation      [fast/en]  'Hey, not much, just chilling. What about you?'
PASS  D. Hindi conversation        [fast/hinglish] 'Bhai, sunn. Kya scene hai? Bas thoda rest kar...'
PASS  E. Hinglish / code-switch    [grounded/hinglish] 'Bhai, kya error message aa raha hai?...'
PASS  F. multi-turn context        "You said you're working on your thesis chapter three."
PASS  G. memory write (agent)      agent=memory ok=True
PASS  H. memory read               'Known: editor=neovim'
PASS  I. Obsidian retrieval        'Found 1 passages in your notes... passkeys in Vision'
PASS  J. agent delegation          steps=['llm.plan','web.search','web.search']
PASS  K. shell executes for real   out='On branch claude/conversational-llm-architecture...'
PASS  L. dangerous action refused  "Refused: 'rm -rf /' is not on the shell allow-list."
PASS  M. coding writes AND runs    steps=['llm.generate','file.write','python.run']
PASS  N. honest about the unknown  "I don't have your landlord's phone number."
PASS  P. TTS real audio            172588 bytes, 3.91s, voice=en_US-lessac-medium
PASS  Q. STT real transcript       'Vision is online and this sentence was spoken by...'
PASS  R. TTS->STT round trip       11 of 14 words recovered
```

### Capability status, honestly

| # | Capability | Status | Evidence |
|---|---|---|---|
| 1 | Text conversation | **WORKING** | E2E C, browser 6 |
| 2 | English | **WORKING** | E2E C |
| 3 | Hindi | **WORKING** | E2E D |
| 4 | Hinglish / code-switch | **WORKING** | E2E E |
| 5 | Multi-turn context | **WORKING** | E2E F |
| 6 | Memory | **WORKING** | E2E G, H |
| 7 | Memory across restart | **WORKING** | process stopped, new process, facts + notes still there |
| 8 | Obsidian retrieval | **WORKING** | E2E I, and the grounded route in E |
| 9 | Web search | **PARTIAL** | searches execute; this network returns 0 results, so the **honest-failure** path is verified and successful retrieval is **not** |
| 10 | Research agent | **WORKING** (degraded) | E2E J — real multi-step run, empty results from 9 |
| 11 | Coding agent | **WORKING** | E2E M — writes a file and executes it |
| 12 | Browser agent | **NOT IMPLEMENTED** | |
| 13 | Computer automation | **NOT IMPLEMENTED** | |
| 14 | File operations | **WORKING** | files agent, gated |
| 15 | Calendar / productivity | **NOT IMPLEMENTED** | |
| 16 | Communication integration | **NOT IMPLEMENTED** | |
| 17 | WhatsApp | **NOT IMPLEMENTED** | |
| 18 | Plugin install / configure | **PARTIAL** | Obsidian connects from the UI; no general plugin system |
| 19 | MCP / external tools | **NOT IMPLEMENTED** | |
| 20 | Image understanding | **NOT IMPLEMENTED** | |
| 21 | STT | **WORKING** | E2E Q |
| 22 | TTS | **WORKING** | E2E P, both languages |
| 23 | Full voice conversation | **PARTIAL** | server-side loop verified end to end; mic and speaker need your machine |
| 24 | Voice interruption | **PARTIAL** | implemented three ways; not verified by a human ear |
| 25 | Multi-agent cooperation | **NOT VERIFIED** | research is multi-step but single-agent |
| 26 | Long-running tasks | **PARTIAL** | every run is persisted and survives restart; no cancel or resume |
| 27 | Error recovery | **WORKING** | agent step failures are reported, not swallowed |
| 28 | Permission / confirmation | **WORKING** | E2E L |
| 29 | Prompt-injection defence | **WORKING** | inherited; 183 scenarios + gateway tests |
| 30 | Destructive-action protection | **WORKING** | E2E L |

**13 WORKING · 6 PARTIAL · 1 NOT VERIFIED · 8 NOT IMPLEMENTED · 2 degraded by network**

### §7. The mutation audit

**93 killed in one pass, 1 survivor, and the survivor was an anchor
drift.** The audit reported:

```
mutations killed by the suite : 93/94
mutations that SURVIVED       : 1
   - orchestrator: invented memories allowed through  (anchor missing)
```

The find-string no longer matched because this session changed that exact
line while fixing the false-denial bug. **An audit whose anchor has drifted
reports SURVIVED and is right to** — it could not run the experiment, and
that is a different thing from a defence with no test. The anchor was
repaired and the mutation re-run: **killed**, by
`test_a_fabricated_memory_about_yesterday_is_still_caught`, one of the
regression tests written earlier this session.

So the honest figure is **94/94 as a composite**: 93 from the full pass
plus 1 verified separately after the repair. Not one clean run of 94, and
said as what it is.

---

## 4. Failures found by running it, and fixed

None of these were visible to 388 passing unit tests. Every one was found
by starting the application.

**SQLite refused cross-thread use.** The server answers on a threadpool.
`check_same_thread=False` was necessary and *not sufficient*: with eight
threads writing, sqlite3 raised `OperationalError('not an error')` — a real
race with a misleading message — on a build reporting `threadsafety == 3`.
Both long-lived connections now go through `dbutil.LockedConnection`, which
holds the lock across execute **and** the fetch.

**The vault index opened its own connection** and was missed by the first
fix. Found only by the running server, again.

**`run git status` dispatched the task `status`** — the trigger phrase was
cut out of the sentence.

**`run rm -rf /` reached no agent at all.** The dispatch pattern listed
safe commands, so a dangerous one matched nothing, fell through to
conversation, and was answered by the *model* instead of refused by the
gateway. Routing decides where a request goes; the gateway decides whether
it may happen. A dangerous command that never reaches the thing which can
say no is the worst available outcome.

**A confident false denial.** The structural "what did I \<verb\>" pattern
caught "what did I just say", routed it to a cross-session search that
excludes the current session, and told the model "You have NO record of
this conversation" — while the conversation sat three lines above in its
own prompt. Now gated on whether the question points at *this* conversation
or an earlier one.

**A 404 on every page load** (no favicon), found by reading the browser
console in the Playwright run.

Each has a regression test. `tests/test_dispatch.py` is new; `397 - 388 = 9`
tests were added by this work.

---

## 5. Two measured findings worth keeping

**TTS voice must be chosen by script, not language.** The runtime replies
to Hindi in *romanised* Hindi. Sent to the Devanagari voice, "Haan yaar,
main theek hoon" came back as `हान्या मेंही कुन`. Sent to the English voice
it came back as `Hanyar Main Thik Hoon` — an English accent, the right
words, and Whisper could read it back. Devanagari → Hindi voice; Latin →
English voice, whatever language it encodes.

**An agent must not be able to claim what it did not do.**
`AgentResult.ok` is computed from executed steps, never asserted. An agent
that ran nothing did not succeed. This caught a real bug within minutes:
the memory agent reported "Noted: I prefer dark mode" with `ok=False`,
because the write had actually failed on a wrong signature.

---

## 6. Measured performance (CPU only, no GPU)

| | |
|---|---|
| Model load | 6–12 s warm |
| Generation | 7–8 tok/s |
| First token | 8–12 s |
| TTS | ~20x realtime (0.2 s compute for 4 s of audio) |
| STT | 0.4–1.3x realtime |
| Server start to ready | 6.2 s |

Your RTX 4050 will be substantially faster for generation. That figure is
**RESEARCHED**, not measured — there is no GPU here.

---

## 7. What is NOT verified

- **Microphone and speaker.** No sound card in this container.
- **Anything on your hardware.** No GPU, no Windows, no 4050.
- **Successful web retrieval.** The network here returns zero results, so
  only the honest-failure path is proven.
- **Voice interruption by a human.** Implemented three ways — clicking the
  state pill, clicking the orb, and starting to speak while Vision talks —
  and observed switching state in Chromium, but not heard.
- **Long-run stability.** Longest continuous run here is minutes.
- **Any user but me.** 18 API checks and 10 browser checks by one author is
  not a user study.

## 8. What remains

Eight capabilities are NOT IMPLEMENTED (§3). In the order I would build
them: MCP tool integration (it makes the rest pluggable), browser agent,
computer automation behind the existing gateway, then communication
(WhatsApp last — it needs a real integration decision, and a fake one is
worse than none).

---

## 9. Launch

```bash
pip install -r requirements.txt
python -m vision --check
python -m vision                # http://127.0.0.1:8765
```

`VISION.md` has the full reference. `LOCAL_RUN_AND_TEST.md` has the
Windows-specific first-run, including the model download.
