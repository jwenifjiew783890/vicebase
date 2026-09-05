# Personal AI — Final Architecture and Engineering Report

Target hardware: **RTX 4050 Laptop (6 GB VRAM), 16 GB RAM, Core i7**
Languages: **English + Hindi + Hinglish**
Date: 2026-09-05

---

## 0. What this report is, and what it is not

**Built, run and tested here:** the entire deterministic runtime — memory,
learning loop, capability gateway, injection defence, vault retrieval,
router, orchestrator — plus a 157-scenario frozen evaluation set, an
injection corpus, and a 180-day drift simulation.

**97 unit tests · 125/125 deterministic scenario checks · 0 simulation
failures.**

**Researched but NOT measured:** everything requiring a GPU. This sandbox has
no CUDA and no torch, so every model, STT, TTS and latency figure below is
sourced from published benchmarks for this hardware class, not measured on
your laptop. They are sized to be decision-grade, and §11 lists exactly what
you must measure before trusting them.

48 of the 157 scenarios require a model judge and were not run.

---

## 1. Three research findings that changed my previous answer

I did not carry forward my earlier recommendations. Three did not survive
contact with your actual requirements.

### 1.1 Parakeet TDT is wrong for you — it has no Hindi

I previously recommended NVIDIA Parakeet TDT 0.6B v3 for STT. Its
[model card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) lists **25
European languages**. Hindi and every Indic language are absent. That
recommendation was simply wrong once Hindi entered the requirements.

### 1.2 Qwen, not Gemma

I leaned toward Gemma 4 E4B. For a Hindi/Hinglish assistant that reverses:
Qwen 3.5 covers **201 languages** (up from 82 in Qwen 3), and on the
IndicParam benchmark Qwen3-4B outperformed Gemma-3-4B on several Indic
tasks. The consensus in 2026 comparisons is that Qwen wins multilingual and
low-VRAM; Gemma wins math and reasoning. Your workload is the former.

### 1.3 Code-switching is the single biggest technical risk in this project

This is the finding that should shape your expectations more than any other:

> Monolingual ASR models hit roughly **42% WER on code-switched speech** —
> a 30–50% relative WER increase versus monolingual input.

Hinglish is your *default* register, not an edge case. An assistant that
mistranscribes two words in five will feel broken no matter how good the
model, the memory or the personality are. **Budget more effort for ASR than
for the LLM fine-tune.**

---

## 2. Your central question: framing

You asked whether this is "a small conversational LLM" or "a personal AI
system built around one," and asked me to challenge the second.

**It is neither, quite.** The accurate framing, which the implementation
now demonstrates rather than asserts:

> **A deterministic personal-agent runtime, in which a small LLM is the
> language and personality layer — and is the component trusted least with
> decisions.**

Concrete evidence from building it: the runtime makes every routing,
permission, memory-write and injection decision, and it does so in **~1 ms
of pure Python** with no model call. Handing any of those to a 4B model
would cost latency, reliability and auditability and buy nothing.

The published numbers support this. The
[Constraint Tax](https://arxiv.org/pdf/2605.26128) study found hard schema
decoding produced **100% schema validity but cost 43.5 points of executable
accuracy**; small models with naive prompting hit
[85% task accuracy and 0% output accuracy](https://arxiv.org/html/2605.02363v1).
The prescription is "reason free, constrain late." That is why the
conversation adapter and the orchestrator adapter are separate interfaces in
`orchestrator.py`, not two prompts on one model.

Countervailing evidence, which I take seriously:
[ParaManager](https://arxiv.org/html/2604.17009) is a Qwen3-4B orchestrator
coordinating 30B+ agents at 70.5% average and 86.5% on unseen agent pools.
**A 4B model can orchestrate** — but the design choices that made it work
are all structural (unified action space, typed state feedback, SFT before
RL). Those are implemented here.

---

## 3. Final architecture

```
                        ┌────────────────────────────┐
                        │     USER  (voice / text)   │
                        └──────┬──────────────▲──────┘
                               ▼              │
        ┌──────────────────────────┐  ┌───────┴──────────────────┐
        │ Silero VAD + semantic    │  │ TTS  (single engine,     │
        │ endpointing              │  │ clause-boundary stream)  │
        │ Qwen3-ASR-0.6B (Hindi ✓) │  └───────▲──────────────────┘
        └──────────┬───────────────┘          │
                   ▼                          │
 ╔═════════════════════════════════════════════╧══════════════════════╗
 ║  ORCHESTRATOR  — deterministic, ~1 ms, no model call               ║
 ║  session state · language · permission tier · audit · budgets      ║
 ╚══┬────────────┬──────────────────┬─────────────────┬───────────────╝
    │ always     │ every turn       │ if action       │ if hard
    ▼            ▼                  ▼                 ▼
┌────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐
│ MEMORY │ │ CONVERSATION     │ │ ORCHESTRATOR     │ │ ESCALATION     │
│ T0..T3 │→│ ADAPTER          │ │ ADAPTER          │ │ specialist     │
│ rules  │ │ Qwen3.5-4B +LoRA │ │ same base, 2nd   │ │ agent brings   │
│ → sys  │ │ speaks freely    │ │ LoRA; typed      │ │ its own model  │
│ prompt │ │ SEES untrusted   │ │ actions only;    │ └────────────────┘
│        │ │ CANNOT act       │ │ NEVER sees       │
└───▲────┘ └────────┬─────────┘ │ untrusted text   │
    │               │ streams   └────────┬─────────┘
    │               │ to TTS             ▼
    │               │        ╔═══════════════════════════╗
    │               │        ║  CAPABILITY GATEWAY       ║
    │               │        ║  schema · taint · tier    ║
    │               │        ║  voice rule · audit       ║
    │               │        ╚═══════════╤═══════════════╝
    │               │                    │
    │      ┌────────┴───┬────────┬───────┴──┬──────────┬─────────┐
    │      ▼            ▼        ▼          ▼          ▼         ▼
    │  Obsidian       Web    OpenCode   Computer   Browser    Shell
    │  hybrid RAG   search   :4096      control   Playwright  allowlist
    │      │            │        │          │          │         │
    │      └────────────┴───┬────┴──────────┴──────────┴─────────┘
    │                       │  results = TAINTED, quarantined
    │        ┌──────────────┘
    ▼        ▼
 ╔══════════════════════════════════════════════════════════════════╗
 ║  LEARNING LOOP — offline, nightly, never in the hot path         ║
 ║  signal → candidate → dedup → contradiction → evidence(N≥3,      ║
 ║  distinct sessions) → YOUR WEEKLY REVIEW → promote → decay       ║
 ╚══════════════════════════════════════════════════════════════════╝
```

### Why each component exists

| Component | Exists because |
|---|---|
| Deterministic orchestrator | Routing decisions must be fast, auditable, and impossible to argue past. Measured at ~1 ms. |
| Two adapters on one base | The constraint tax. Also, structurally, it is the primary injection defence. |
| Capability gateway | A model can be talked out of a rule; a permission check cannot. |
| Taint tracking | Prompt injection only matters if the component reading untrusted text can also act. It cannot. |
| Four-tier memory | Facts, events and *behaviour* have different lifetimes and different retrieval patterns. |
| Protected rules | Preference learning optimises toward agreement. Without a floor it erodes honesty over months. |
| Evidence threshold | One bad day must not become permanent behaviour. |
| Human review queue | Without it, drift is invisible until it is large. |
| Bitemporal T2 | Memory staleness is a named open problem in the 2026 benchmark literature. Superseding beats deleting. |
| Hybrid retrieval | Your vault is full of invented codenames. Dense-only retrieval cannot see them. |

---

## 4. Inside the LLM vs outside — the definitive split

### Inside (trained in)
Conversational style, register, warmth · brevity/verbosity policy ·
turn-taking and follow-up policy · **language mirroring (EN/HI/Hinglish)** ·
intent understanding · abstention and calibrated hedging · grounded-answer
behaviour with citation · repair behaviour · action *selection* within a
validated space · basic world knowledge (inherited, never trained, never
stripped).

### Outside (code, storage, config)

| Never in the model | Where it lives here |
|---|---|
| Facts about you | `memory.py` T2, bitemporal |
| Behavioural rules | `memory.py` T3, capped, versioned, rollback-able |
| Credentials | OS keychain. Never in context, never in memory tables |
| **Permission logic** | `gateway.py`. A model can be persuaded; code cannot |
| Tool registry + schemas | `gateway.REGISTRY` |
| Routing thresholds | `router.RouteConfig` |
| Conversation history | `memory.turns` |
| Exact values (paths, dates, IDs) | Tools |
| Retry budgets, kill switch | `gateway.RETRY_POLICY` |
| Audit log | `gateway.audit`, append-only |

**Rule: if it must be exactly right, auditable, or reversible, it is not the
model's job.**

---

## 5. Model recommendations

### Conversational model
**Qwen3.5-4B (dense, Apache-2.0, released 2026-03-02), Q4_K_M.**
Rationale: 201-language coverage, documented Indic strength at 4B, strongest
tool-calling lineage, smallest VRAM footprint of the credible candidates.

Fine-tune **Gemma 4 E4B in parallel on identical data** and pick by blind
A/B. It is cheap to test and the Indic evidence is thin enough that I would
not bet on it unmeasured.

**Two LoRA adapters, ~40–80 MB each**, on one base:

| | Conversation adapter | Orchestrator adapter |
|---|---|---|
| Output | Natural language only | Typed actions only |
| Constrained decoding | **Never** (kills warmth) | Yes, grammar-enforced |
| Sees retrieved content | Yes | **Never** |
| Can emit actions | **Never** | Yes |

Serving: llama.cpp supports per-request adapter selection. Pragmatic
fallback if multi-adapter serving is fiddly: one model, two system-prompt
modes, constrained decoding only on the tool path.

### Escalation
- **Tier 1** 4B, ~95% of turns
- **Tier 2** 8–9B loaded on demand — only if VRAM allows after measurement
- **Tier 3** specialist agents bring their own model. **For coding, delegate
  to OpenCode — do not escalate the conversational model.** This is why 4B
  suffices: the hard cognition lives in the agents.

### Training strategy
1. **Phase 0 first: no training.** Stock model + system prompt + the runtime
   already built. Measure it. It is the bar every checkpoint must clear.
2. LoRA SFT — 8–12k conversations. Composition and the messy-user synthetic
   recipe are in `docs/conversational-llm-architecture.md`. **Critical
   addition for you: at least 35% of the corpus must be Hindi and Hinglish,
   with mid-sentence code-switching**, generated from your own logged turns
   where possible. A model trained on clean English will not mirror your
   register.
3. DPO on rejection-sampling pairs.
4. Character training (Constitutional-AI style).
5. On-policy distillation repair — documented to restore instruction-
   following from 85%→45% collapse back to 83%, where 30% replay mixing
   failed.
6. Orchestrator adapter: **SFT before RL, always.** Direct GRPO caused
   policy collapse (the model stopped using tools entirely) in the
   ParaManager ablation.

Cost: ~$300–500 rented GPU including failed runs. This is not a compute-
constrained project.

---

## 6. Voice architecture

### STT — **Qwen3-ASR-0.6B** (Apache-2.0)
Hindi explicitly supported, 30 languages, ~700 MB at INT8, streaming via
vLLM. The 1.7B variant is SOTA among open ASR but doubles the VRAM.

⚠️ **Plan for a Hinglish fine-tune.** Published code-switched WER (~42% for
monolingual models) is not acceptable for a daily assistant. Precedent
exists: Orato-ASR full-parameter fine-tuned Qwen3-ASR-0.6B on ~1,000 hours
of Hindi/English/Hinglish audio. **Budget this as real work, not a config
change.** Consider AI4Bharat IndicVoices (23,700 h) and the HiACC
code-switched corpus.

### TTS — decision driven by measurement, rule encoded in `latency.py`

**Single engine, not language routing.** Routing between a Hindi and an
English voice changes the voice audibly mid-conversation; for a companion
assistant that reads as broken. Sarvam handles code-switching at the model
level for exactly this reason.

| Engine | First audio | Hindi | Local |
|---|---|---|---|
| Kokoro-82M | ~120 ms | weak | ✅ |
| **IndicF5** (MIT, 1,417 h, 11 Indic langs) | ~700 ms est. | strong | ✅ |
| Sarvam Bulbul v3 | ~250 ms | strong, single-pass Hinglish | ❌ cloud |

`choose_tts()` implements the rule: measure first-audio on your laptop, then
prefer local single-engine; fall back to cloud only if you accept that
response text (which may contain vault content) leaves the machine;
language-routing is the last resort.

### Endpointing
Silero VAD + semantic endpointing. **Budget real tuning time here.** At
220 ms it is the largest single term in the fast path after TTS, and
cutting the user off mid-sentence destroys the illusion faster than any
model deficiency.

---

## 7. Latency and VRAM — computed, not asserted

`pai/latency.py` is a runnable model. Optimised critical path
(tuned endpointing, clause-splitting at 8 tokens):

| TTS | Fast path | Grounded |
|---|---|---|
| Kokoro | **773 ms** responsive | 1033 ms |
| Sarvam | 903 ms responsive | 1163 ms |
| IndicF5 | 1353 ms | **1613 ms** |

**Honest conclusion: with a local Hindi-quality TTS, sub-1 s is not
achievable on this hardware in 2026. ~1.4–1.6 s is.** That reads as
"thoughtful," not "broken" — but it is not the 200 ms of human conversation
and you should not expect it to be.

**The masked web path is the fastest perceived turn in the system at 558 ms**,
because the acknowledgement fires before the search starts. That result
validates the acknowledgement design quantitatively.

### VRAM on 6144 MB

| Configuration | Used | Free | |
|---|---|---|---|
| LLM + STT + draft model | 5010 MB | 1134 MB | fits |
| LLM + STT, no draft | 4490 MB | 1654 MB | fits |
| LLM only, STT on CPU | 3790 MB | 2354 MB | fits |

Recommended: **LLM + STT on GPU, TTS and embeddings on CPU.** A Tier-2 8B
model does **not** fit alongside — escalation on this laptop means a
specialist agent or cloud, not a second local model. Budget ~450 MB for the
Windows desktop compositor.

---

## 8. Memory and learning — as implemented

| Tier | Contents | Storage | Reaches model |
|---|---|---|---|
| T0 | Live turns | RAM | Context |
| T1 | Episodes | SQLite | Retrieved |
| T2 | Facts, **bitemporal** | SQLite | Retrieved |
| **T3** | **Behavioural rules** | SQLite, **cap 40** | **Always, prompt-cached** |

Pipeline: `signal → candidate → dedup → contradiction → evidence(N≥3,
distinct sessions) → review queue → promote → decay (60-day half-life,
0.30 floor)`.

Three guards, all tested:
- **One session cannot manufacture a threshold** (unique index on
  `(rule_id, session_id)`).
- **Contradictions never silently overwrite** — the old rule is weakened,
  both queue for review, you decide.
- **Protected rules cannot be archived, decayed, or overwritten**, and
  candidates matching the sycophancy tripwire are rejected regardless of
  evidence.

**Weights: quarterly at most, versioned, A/B'd, never in place.**
[Sparse Memory Finetuning](https://arxiv.org/abs/2605.03229) found LoRA and
full fine-tuning both drift measurably when learning small amounts of new
information, because LoRA updates are global — they change the
representation of every token. Personalisation is exactly that case.

### 180-day simulation result

Preference held (days 0–59) → reversed (60–119) → abandoned (120–179):

- Rule set peaked at **10 active (5 learned + 5 protected)**, cap 40 ✅
- System prompt block peaked at **607 characters** ✅
- Brevity learned in phase 1, **reversal followed** by day 120 ✅
- No contradictory pair ever active simultaneously ✅
- Under **relentless praise with an auto-approving reviewer** (worst case —
  a real user rejects some proposals): all 5 protected rules intact at full
  confidence, zero agreement rules promoted ✅

---

## 9. Obsidian, web, tools

**Obsidian:** heading-breadcrumb chunking · section-based splitting ·
hybrid BM25(FTS5) + dense, fused with RRF · one-hop `[[wikilink]]`
expansion · gentle recency boost · frontmatter tags · everything returned
`Tainted` with path and age so staleness is visible.

**The hybrid claim is tested, not asserted.** With an embedder that
reproduces real dense retrieval's weakness on rare tokens, the vault
codename "Thornbury" is **invisible to dense search, found by BM25 at rank
1, and found by the hybrid** — while semantic queries still work.

**Web:** gated by deterministic pre-checks (temporal markers), model
request, or an uncertainty signal; overridden by explicit user phrasing in
both languages; **always masked by an acknowledgement**.

**OpenCode:** `opencode serve --port 4096` gives a headless HTTP API;
`opencode-mcp` bridges it to MCP. Capability tier IRREVERSIBLE → confirm.
⚠️ **The task brief your 4B writes is the quality bottleneck** — turning a
vague spoken request into a precise agent spec is a specific skill and needs
dedicated SFT examples.

**Typed feedback** (`OK/PARSE_ERR/DENIED/EXEC_ERR/TIMEOUT/EMPTY`) with a
bounded retry policy. `EMPTY` carries the instruction *"Do NOT answer from
memory instead"* — that is the anti-hallucination hook at the tool boundary.

---

## 10. Security — tested, not designed

| Tier | Policy | Tested |
|---|---|---|
| READ | auto, logged | ✅ |
| WRITE | auto, logged, undoable | ✅ |
| IRREVERSIBLE | confirm every time | ✅ |
| DESTRUCTIVE | confirm + typed phrase | ✅ |

**The voice rule: speech can never authorise an irreversible action.** Not
because voice is untrusted, but because misrecognition is inevitable.
Tested against realistic mishearings including the worst case — *"no, don't
push"* heard as *"now push"*. No spoken phrase in either language can
complete a typed confirmation.

**Taint tracking is the primary injection defence.** Tainted arguments are
**denied, not escalated to confirmation** — a confirmation prompt whose text
was written by the attacker is not a safeguard.

Corpus: 20 payloads including Devanagari and romanised-Hindi overrides,
false pre-authorisation, and authority claims. **All denied.** Critically,
there is a test proving the gateway still denies everything **with the
pattern scanner replaced by a regex that matches nothing** — the structural
defence does not depend on the lexical one.

---

## 11. Tests performed, failures found, fixes applied

**97 unit tests · 125/125 deterministic scenarios · 0 simulation failures.**

| # | Failure found by testing | Fix |
|---|---|---|
| 1 | `"the"` listed as a romanised Hindi marker (थे) misclassified most English as Hinglish — would have misrouted TTS voice on a large share of turns | Three-way word classification with a neutral ambiguous bucket |
| 2 | Excluding ambiguous words from the Hindi set made them count as *English*, so pure Hindi scored as mixed | Ambiguous words count for neither side |
| 3 | **RRF fusion scores used as a relevance threshold.** RRF is rank-based: anything ranked #1 by both retrievers scores 2/(60+1) regardless of match quality. A garbage vault hit was suppressing a needed web search | RRF for ranking; raw BM25/dense scores for gating |
| 4 | Definitional questions ("what's a for loop") pulled vault context | Explicit general-knowledge short-circuit ahead of retrieval gating |
| 5 | **5 of 6 unicode evasions defeated the injection scanner** (zero-width, Cyrillic homoglyphs, fullwidth, NBSP, combining marks) | NFKC + confusable folding + invisible stripping before scanning |
| 6 | **The sycophancy tripwire reported 0 rejections over 180 simulated days** — because the deterministic proposer never proposes agreement rules. The test was passing vacuously | Added a naive-LLM proposer that commits the realistic failure, incl. a candidate reusing a protected rule's key. 7 new tests |
| 7 | False-authorisation and authority-claim injections had no override markers and evaded pattern matching | Patterns added, **plus** a test proving the structural defence covers what the scanner cannot |
| 8 | TTS selection compared raw engine latency against a whole-pipeline threshold — accepted a 1600 ms engine that puts the pipeline at 2.5 s | Compare budgets, not raw latency |
| 9 | Delegation used a "let me check" acknowledgement; checking and doing are different promises | Ack sets split by intent |
| 10 | Missing Hindi greeting markers (`namaste`, `shukriya`, `haal`, `khol`) — an entire class of Hindi smalltalk read as English | Markers added |

Finding #6 is the one I would flag hardest: **a green test that was green
for the wrong reason.** It looked like proof the anti-sycophancy design
worked and was actually proof it had never been exercised.

---

## 12. Remaining limitations — stated plainly

1. **No model was run.** Every LLM/STT/TTS/latency number is researched, not
   measured. Measure before trusting.
2. **Code-switched ASR at ~42% WER is the largest risk in the project.** A
   Hinglish fine-tune is not optional.
3. **Retrieval thresholds are calibrated against a stand-in TF-IDF embedder
   on a 5-note vault.** Score distributions differ completely with a real
   embedder on 5,000 notes. Sweep them against the eval set before shipping.
4. **Language ID is a wordlist heuristic (~90%).** Replace with a small LID
   model or let the conversational model tag the turn.
5. **48 scenarios need a model judge** and are unverified.
6. **Multi-turn degradation still applies** — 39% average on frontier models,
   worse at 4B. Memory helps *across* sessions, not *within* a long one.
7. **Sub-1 s with local Hindi TTS is not achievable on this hardware.**
8. **A Tier-2 8B model does not fit** alongside the 4B and STT in 6 GB.
9. **The injection scanner is unbounded whack-a-mole.** It is defence in
   depth. The taint check is the defence.
10. **Windows VRAM reservation is an estimate.** Verify headroom on your box.

---

## 13. Roadmap — what is done, what remains

### ✅ Done (this session, tested)
Trust model · four-tier memory with bitemporal T2 and capped T3 · learning
loop with evidence threshold, contradiction detection, review queue, decay ·
anti-sycophancy with protected rules and tripwire · capability gateway with
tiers, taint, voice rule, audit · typed execution feedback and retry policy ·
injection corpus and scanner with unicode normalisation · Obsidian
heading-aware chunking and hybrid retrieval with wikilink expansion ·
deterministic router with fast path and general-knowledge short-circuit ·
acknowledgement policy · orchestrator turn lifecycle · latency/VRAM model ·
157-scenario eval set · 180-day simulation · end-to-end demo.

### Remaining

| Phase | Work | Gate |
|---|---|---|
| **1** | Wire real embedder; index your vault; **sweep retrieval thresholds** | Injection precision/recall on your own notes |
| **2** | Ollama/llama.cpp + Qwen3.5-4B; real adapters; web UI | Phase-0 baseline measured |
| **3** | Real signal→rule extraction with a strong model nightly; review CLI | Rules you would actually keep |
| **4** | Voice: Qwen3-ASR + VAD + endpointing + **measure TTS**; run `choose_tts()` | p95 first-audio < 1.6 s |
| **5** | **Hinglish ASR fine-tune** | Code-switched WER < 20% |
| **6** | Conversation adapter: SFT → DPO → character → distillation repair | >60% blind A/B vs Phase 0; IFEval within 5 pts |
| **7** | Orchestrator adapter (SFT then GRPO); OpenCode; browser; computer control **last** | 0 injection-triggered actions |

---

## 14. Final recommendation

> **If I were building this on your laptop today:**

1. **Qwen3.5-4B Q4_K_M**, two LoRA adapters. Fine-tune Gemma 4 E4B in
   parallel and pick by blind A/B.
2. **Deterministic runtime owns everything the model should not.** It is
   built, it is tested, and it costs ~1 ms per turn.
3. **Treat Hinglish ASR as the hardest problem in the project**, ahead of
   the LLM fine-tune. 42% code-switched WER is the number that decides
   whether this feels usable.
4. **One TTS engine for both languages.** Measure IndicF5 on your box, then
   run `choose_tts()`. Accept ~1.5 s; do not chase 200 ms locally.
5. **LLM + STT on GPU, TTS + embeddings on CPU.** 5010/6144 MB. Escalation
   means a specialist agent or cloud, not a second local model.
6. **Build memory and the learning loop before the fine-tune.** Memory is
   what makes it *yours*; the fine-tune makes it *pleasant*. Pleasant-but-
   generic is a model you can download.
7. **Keep the weekly review queue.** Five minutes. It is the difference
   between learning you and learning noise about you.
8. **Keep the protected rules and watch the rejection count.** A tripwire
   reporting zero rejections is not necessarily working — that was finding
   #6, and it is the most instructive failure in this report.
9. **Computer control ships last**, allowlisted and confirmation-gated,
   after the injection corpus passes clean.

### Bottom line

The architecture is sound and the hard half is built and tested. Your
laptop is sufficient. The 4B model is sufficient, because the hard cognition
lives in the agents and the hard decisions live in code.

**The two things that will decide whether this succeeds are not the model.**
They are Hinglish ASR accuracy, and whether you spend five minutes a week on
the review queue. Everything else here is engineering that is now largely
done.
