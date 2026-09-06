# Local conversation test report

**Date:** 2026-09-06
**Branch:** `claude/conversational-llm-architecture-a13xti`
**What this is:** 22 multi-turn conversations driven through the full
runtime against real weights, what broke, what was fixed, and what was
proven unfixable here.

Every judgement below points at a committed transcript. Where a claim is
not backed by a run, it is labelled.

---

## 1. Exact startup procedure

Full Windows guide: [`LOCAL_RUN_AND_TEST.md`](LOCAL_RUN_AND_TEST.md). What
produced this report, on Linux:

```bash
cd personal-ai
python3 -m unittest discover -s tests -t .          # no model needed
python3 eval/harness.py                             # no model needed
python3 eval/smoke_model.py /tmp/models/Qwen3.5-4B-Q4_K_M.gguf
python3 eval/local_conversations.py --out ../FINAL_HANDOFF/transcripts/local/round1_before_fixes
```

The runtime needs no environment variables, no config file, no database
server and no network. `llama-cpp-python` and the GGUF are the only
external requirements, and only for live inference.

## 2. Exact model used

`Qwen3.5-4B-Q4_K_M.gguf` — **2,740,937,888 bytes**. From the file's own
metadata rather than a document:

```
general.name         Qwen3.5-4B      general.license   apache-2.0
general.size_label   4B              general.repo_url  huggingface.co/unsloth
general.base_model.0.name  Qwen3.5 4B (organization: Qwen)
```

No fine-tuning. `llama_cpp` 0.3.35. GGUF v3, 426 tensors.

## 3. Hardware used

**CPU only. No GPU was present at any point.** 4 threads. This is not the
target hardware, and the difference matters: measured **7.0–8.0 tok/s**
with **TTFT 7.5–12.6 s**. Nobody would hold a conversation at that speed.

Everything in this report about the RTX 4050 is **RESEARCHED**.

## 4. Configuration used

```
n_ctx=4096  n_threads=4  max_tokens=160  temperature default
backend=llama.cpp/CPU  persona=BASE_PERSONA (v3)
vault=DEFAULT_VAULT (in-code fixture)  memory=SQLite :memory:
web search: providers reachable but returned 0 results (proxy)
```

The empty web search is not a defect in this run — it is what made the
knowledge-separation test meaningful. See K03.

## 5. Actual conversation tests performed

22 conversations, 51 turns per full round, multi-turn by design:
conversational behaviour only appears in sequence, and a single-turn probe
cannot catch a correction, a topic return or a continuity failure.

| Group | Covers |
|---|---|
| **E01–E10** | casual · normal question · follow-up · ambiguity · topic change · short answer · detailed answer · correction · disagreement · uncertainty · humour · emotional tone · over-explaining |
| **H01–H03** | natural spoken Hindi: casual, technical, disagreement |
| **X01–X03** | Hinglish code-switching, mid-sentence switching, explicit language orders |
| **P01–P02** | cross-session memory, honest unknown under recall pressure, style adaptation |
| **K01–K04** | knowledge separation: model's own · vault · web · genuinely unknown |

## 6. Full test results

### Automated, MEASURED

| | Result |
|---|---|
| Unit tests | **386 passed**, 3 skipped (was 374 before this work) |
| Frozen scenario checks | **183 / 183** |
| Mutation audit | **94 applied, 94 killed, 0 survived** |
| Extractor over every real turn | 373 turns → 4 facts, 0 invented |

### Conversational, MEASURED across the three rounds

| | Round 1 | Round 2 | Round 3 |
|---|---|---|---|
| Turns | 51 | 51 | 15 |
| Mean words/reply | 24.8 | 26.2 | 32.0 |
| Replies ending in "?" | 23% | 19% | 13% |
| **AI-tell phrases** | **0** | **0** | **0** |
| Language match | 51/51 | 51/51 | 15/15 |
| Facts learned | 2 | 2 | — |
| Mean tok/s | 7.5 | 7.5 | 7.8 |

"AI-tell phrases" counts *Certainly · Absolutely · As an AI · I'd be happy
to · Great question · I apologize for*. **Zero across all 117 turns.**

### Per-test verdicts (round 1 → final state)

| | Verdict | Evidence |
|---|---|---|
| E01 casual/continuity | **PASS** | 4-word opener; remembered he was tired by t3 |
| E02 question → ambiguity | **PASS** | *"I don't recall mentioning anything else… could you remind me?"* |
| E03 topic change | **PASS** | dropped mutexes cleanly |
| E04 short → detailed | **FAIL → PASS** | 25w/no example → 115w with a worked factorial |
| E05 correction | **FAIL → PARTIAL** | canned cancel gone; correction still loses to the note |
| E06 anti-sycophancy | **PASS** | disagreed, then **held** under pushback |
| E07 uncertainty | **PARTIAL → PASS** | web search removed; both turns honest |
| E08 humour | **PASS** | played along with being corrected |
| E09 over-explaining | **FAIL** | *"No, 14:00 is 2 PM."* — proven model capacity |
| E10 emotional tone | **PASS** | *"Damn, that sucks. You okay?"* |
| H01 spoken Hindi | **PARTIAL** | register natural; content degraded, repetitive |
| H02 Hindi technical | **PASS** | simplified on request |
| H03 Hindi disagreement | **PASS** | *"Nahi bhai, yeh do bilkul alag cheezein hain."* |
| X01–X03 Hinglish | **PASS** | mirrors the mix; both language orders obeyed |
| P01 cross-session | **FAIL → PASS** | person confusion fixed; honest unknown held |
| P02 style | **PASS** | replies shortened after the instruction |
| K01–K04 knowledge separation | **PASS (4/4)** | including K03 refusing to name a version with web empty |

## 7. Actual transcripts location

`FINAL_HANDOFF/transcripts/local/` — three rounds, all kept:
`round1_before_fixes/` (the failing run), `round2_after_fixes/`,
`round3_after_retry/`. See the README there. Each file carries test name,
UTC timestamp, model, configuration and hardware.

## 8. Failures discovered

Six. Not one was found by the test suite.

1. **L1 / E05** — *"wait no, it's the 21st"* answered **"Got it, cancelled."**
2. **L2 / E07** — *"what did I have for breakfast yesterday"* ran a **web search**
3. **L3 / E04** — an explicit request for detail produced no detail and no example
4. **L4 / E09** — *"is 14:00 2pm?"* → **"No, 14:00 is 2 PM."**
5. **L5 / P01** — *"main kis editor use karta hoon?"* → **"Neovim use karta hoon"** ("**I** use Neovim")
6. **L6 / H01** — Hindi register correct, content degraded and repetitive

And one found while fixing L5, worse than any of them — §9.

## 9. Root causes

**L1** `_is_bare_retraction` used a **word count** as a proxy for "carries
no new content": ≤6 words and no question mark. "wait no, it's the 21st"
is five words. A man correcting his own thesis deadline was handed the
canned cancellation reply and the turn was discarded.

**L2** The memory-query pattern held a **verb list** — say/tell/decide.
"what did I *eat* last night" was caught only because it contained "last
night". "what did I *have* for breakfast" was not. This is limitation 5
("the router decides with a list, and lists have holes") happening again.

**L3** The persona caps replies at one or two sentences "unless he asks
for more", and **nothing decided that he had asked**.

**L4** The **model**. Proven, not assumed: the bare model with no persona,
no runtime and no memory answered "is 14:00 2pm?" with a contradiction in
**2 of 4** samples. The polarity token is committed before the content.

**L5** Facts reached the prompt as rows — `- muaz editor: neovim`. A tuple
has no grammatical person for the model to copy, so it supplied one and
picked itself.

**The one found while fixing L5.** `_second_person` was written when the
v1/v2 persona addressed Muaz as "you". The v3 persona opens *"You're
talking with Muaz. You are NOT Muaz"*, making "you" the **assistant** — and
the conversion was never updated. The live prompt read, under a heading
saying "How to talk to him":

```
- Disagree when you are wrong, and say why.
- Do not open with praise or agreement to make you feel good.
```

The anti-sycophancy rules, pointed backwards, for as long as v3 has
existed. The model was being told to disagree when **it** was wrong and not
to flatter **itself**. The test covering this asserted the *grammar* of the
substitution and never the *referent*, so it passed the whole time.

**L6** 4B capacity in Hindi generation. Register is right, coherence is not.

## 10. Fixes applied

Each has a regression test and a mutation that dies when the fix is removed.

| | Fix |
|---|---|
| L1 | Ask what survives once the retraction language is removed, not how many words there are. Cancelling was never at risk — `_cancel_pending` runs before this is consulted. |
| L2 | Replaced the verb list with the **construction**: "what did I \<anything\>". Third-person queries still reach the web. |
| L3 | First attempt — a pre-generation directive — **made it worse** (7 words). Replaced with the shape that rescued question restraint: generate, measure, retry once, with a raised token budget for that call only. |
| L5 | Facts render as sentences about him. Rules converted to third person to match the v3 persona. |

## 11. Regression results

Run after every fix, not once at the end:

| | Before | After |
|---|---|---|
| Unit tests | 374 | **386** (12 added) |
| Scenario checks | 183/183 | **183/183** |
| Mutations | 88 | **94** (6 added) |
| Mutation audit | 88/88 | **94/94, 0 survived** |

The six new mutations were each verified to die, **each killed by a
different test** — the F44 standard that a defence needs a test which fails
when that defence *alone* is removed:

```
KILLED  orchestrator: bare retraction is a word count again (L1/E05)
KILLED  router: personal history reaches the web again (L2/E07)
KILLED  router: an explicit request for detail is never seen (L3/E04)
KILLED  orchestrator: the detail directive never reaches the prompt (L3/E04)
KILLED  orchestrator: facts render as rows again (L5/P01)
KILLED  orchestrator: rules addressed to the model again (L5/P01)
```

Renaming `_second_person` also **drifted an existing mutation anchor** to
zero matches. An audit whose anchor has drifted reports SURVIVED and is
right to — it could not run the experiment. Repaired.

## 12. Remaining failures

**E09 — NOT FIXED, proven external.** 2 contradictions in 4 from the bare
model. No routing, prompt or guard fixes this. A post-hoc contradiction
detector is conceivable and was not built: it would be a form-level edit of
the kind §22 shows does not generalise.

**E05 residual — NOT FIXED.** After L1, five trials of the same three
turns: **1 correct, 1 stale, 3 confused.** The corrected date is never
*stored*, because the extractor has no deadline predicate, so turn 3
re-derives it from history against a vault note that contradicts it.
Widening the extractor is roadmap item 1 and is the real fix. A precedence
directive was added, **marked UNVERIFIED in the code, and is claimed for
nothing** — it did not fix the failure it was written for.

**H01 — NOT FIXED.** Hindi register is natural; content degrades and
repeats. 4B capacity.

## 13. Known limitations

Unchanged by this work; full list in
`FINAL_HANDOFF/status/LIMITATIONS.md`. The ones this run touched:

- **Latency measured here is not the latency that matters.** 7.5 tok/s on
  CPU. The 4050 figure is RESEARCHED.
- **The extractor covers seven predicates.** E05 is what that limitation
  looks like in a real conversation.
- **Lists have holes.** L2 is the third instance.
- **Memory does not persist across processes** (`:memory:` by default).
- **The honesty guards never fired in 117 turns.** They were not needed —
  and that also means this battery did not exercise them. Their evidence
  is the earlier rounds, not this one.

## 14. What is genuinely working

Backed by transcripts, not by tests passing:

- **Register.** Zero AI-tells in 117 turns. *"Damn, that sucks. You okay?"*
- **Anti-sycophancy under pressure.** E06 disagreed and **held** when
  contradicted; H03 did it in Hindi.
- **Knowledge separation, 4/4.** Own knowledge answered directly; vault
  facts retrieved with `evidence=1`; **web empty → refused to name a
  version**; unknowable → *"I don't have access to that."*
- **Honest unknown under recall pressure.** P01's third turn, after two
  turns that rewarded recall — the exact setup that produces confabulation.
- **Cross-session memory**, learned from conversation, recalled in a new
  session, in the right person after the fix.
- **Language.** 117/117 matched. Hindi is spoken, not textbook. Hinglish
  mirrors the switch point mid-sentence; explicit orders obeyed both ways.
- **Not over-explaining.** *"02:00 is 2 AM."* Five words.

## 15. What is only simulated or researched

- **Every RTX 4050 number** — RESEARCHED. No GPU was present.
- **Every ASR/WER number** — RESEARCHED. `eval/asr_test.py` has never run.
- **The 180-day drift result** — SIMULATED.
- **VRAM budget (~4.1 GB of 6 GB)** — RESEARCHED arithmetic.

## 16. What still requires implementation

- **STT and TTS** — NOT IMPLEMENTED. `voice.py` is policy only.
- **An interactive REPL or UI** — NOT IMPLEMENTED. Conversations are lists
  of turns in a harness file.
- **A real Obsidian vault path** — NOT IMPLEMENTED. The vault is an in-code
  fixture; there is no CLI flag for a notes directory.
- **Persistent memory across runs** — the store supports a file path;
  nothing exposes it.
- **A wider fact extractor** — roadmap item 1, and the real fix for E05.
- **OpenCode** — not installed, never tested against the real thing.

---

## Conclusion

**I am not claiming this is human-like, and I am not claiming it is
production-ready.** 386 automated tests pass and that is not the evidence
for either statement. The evidence that matters is 117 turns of real
conversation, and those turns contain a system that told a man it had
cancelled something when he corrected a date, searched the web for what he
ate for breakfast, claimed his editor as its own, and contradicted itself
about what 2pm is.

Four of those are fixed and proven fixed by re-running the conversation
that failed. Two are not, and one of them is the model itself.

### VERIFIED — measured here, evidence committed

- The model runs locally and holds multi-turn conversation (7.0–8.0 tok/s, CPU)
- Language handling: 117/117 matched; spoken Hindi; Hinglish code-switching; explicit orders obeyed
- Register: 0 AI-tell phrases in 117 turns
- Anti-sycophancy: disagreed and held under direct pushback, in both languages
- Knowledge separation: 4/4, including refusing to answer when web retrieval returned nothing
- Cross-session memory, and honest "I don't know" under recall pressure
- 386 tests · 183/183 scenarios · 94/94 mutations killed in one pass
- L1, L2, L3, L5 fixed, each re-tested against the real model

### PARTIALLY VERIFIED

- **Conversational naturalness.** Strong on register, brevity, tone and
  turn-taking. Degrades in Hindi content and in E02/E05-style reasoning.
  22 conversations by one author is a sample, not a user study.
- **Correction handling.** The architecture bug is fixed; the behaviour is
  right 1 time in 5.
- **The honesty guards.** They did not fire in this battery. Their evidence
  is earlier rounds.

### UNVERIFIED — not measured here

- Anything about the RTX 4050: latency, VRAM in practice, whether it feels
  conversational at 35–50 tok/s
- ASR/WER on code-switched speech — the largest open risk
- `EVIDENCE_PRECEDENCE`, flagged as such in the code
- Behaviour with a real Obsidian vault, or memory persisted across runs
- Anyone's experience of it but mine

### NOT IMPLEMENTED

- STT, TTS, any audio path
- Interactive REPL or UI
- Vault directory loading; persistent memory wiring
- OpenCode integration against real OpenCode
