# Building a Small, Conversation-Specialized Local LLM

**An engineering and research evaluation**
Date: 2026-09-05

---

## 0. Executive verdict

**Is it feasible?** Yes — but not in the shape you described.

**The three-sentence version:**

1. **Do not train from scratch, and do not try to "remove knowledge to buy conversational capacity."** That trade doesn't exist. Knowledge and conversational competence are not separate parameter budgets; broad pretraining knowledge is the *substrate* that pragmatic understanding runs on. Start from a strong 3–5B open-weight base and change its **behavioral policy**, not its knowledge content.

2. **Most of what you call "conversational ability" is post-training policy + system design, not model capacity.** Brevity discipline, tone-matching, follow-up questions, knowing when to defer to retrieval, abstention — these are installable in a 4B model with a few thousand well-made examples. The parts that *are* capacity-bound (multi-turn state tracking, deep implicit intent, genuine humor) will remain your ceiling and no amount of conversational fine-tuning fixes them.

3. **In a voice assistant, perceived conversational quality is dominated by latency and turn-taking, not word choice.** Human conversational gaps average ~200ms. If your pipeline answers in 2.5s, it feels robotic no matter how witty the text. A large fraction of your engineering budget belongs in the pipeline, not the model. This is the highest-leverage insight in this document.

**Expected outcome if you execute well:** a system that feels *clearly* better than a stock 4B model — noticeably better on tone, brevity, consistency, and honesty — and feels *much* better as a whole product, mostly because of retrieval, memory, and latency rather than because of the fine-tune. It will not feel like Claude or GPT-5. It will feel like a good, fast, personal assistant that knows your notes. That is a genuinely valuable thing to have built.

---

## 1. Challenging your assumptions

### Assumption 1: "I can skip knowledge and spend the capacity on conversation." — Mostly wrong

Three independent reasons:

**(a) You can't "not spend" capacity you're inheriting.** You will not pretrain from scratch (see §6). Any base model you start from has already spent its capacity. Fine-tuning does not reclaim it. The only way to act on this assumption would be to pretrain, which costs millions of GPU-hours for a model that would still be worse than a stock Gemma 4 E4B at conversation, because conversational competence rides on general language competence.

**(b) The capacity numbers don't support the intuition anyway.** Allen-Zhu & Li's controlled study ([arXiv:2404.05405](https://arxiv.org/abs/2404.05405), ICLR'25) found transformers store ~2 bits of factual knowledge per parameter. A 4B model ≈ 8 Gbit ≈ 1 GB of facts — they estimate a 7B model's capacity exceeds English Wikipedia plus textbooks. Factual knowledge is *cheap* in parameters. It is not what's crowding out your conversational ability.

**(c) Knowledge is load-bearing for conversation.** Your own requirement list includes "understanding implicit meaning and intent." That is a world-model task. A model that doesn't know what a mortgage, a standup, or a deadline *is* cannot respond appropriately when you're stressed about one. Every attempt to strip knowledge from a model (aggressive pruning, narrow-domain retraining) degrades everything, chat included.

**The correct reframing:** keep all the knowledge. Change the model's **epistemic policy** so it treats internal knowledge as *conversational priors* rather than *citable facts*, and defers to retrieval for anything specific, personal, verifiable, or time-sensitive. That is a training objective you can actually hit.

### Assumption 2: "Training a conversation-specialized model is the main work." — Wrong by a factor of ~4

Rough attribution of perceived quality in a system like this:

| Contributor | Share of perceived quality | Effort to get right |
|---|---|---|
| End-to-end latency & turn-taking | ~30% | Medium |
| Retrieval quality (Obsidian) + memory about you | ~25% | Medium-high |
| System prompt / persona / orchestration | ~20% | Low |
| Conversational fine-tuning of the model | ~15–25% | **High** |
| Base model choice | ~10% | Trivial |

The fine-tune is the most expensive item and not the largest. It is still worth doing — persona robustness, tool-gating precision, and abstention are hard to get from prompting alone and they degrade under long conversations — but it should be **step 4**, not step 1.

### Assumption 3: The linear pipeline `User → LLM → decide → Obsidian → web → answer` — wrong shape

Two problems:

- **Most turns need zero retrieval.** Putting a retrieval decision on the critical path of every turn taxes the 90% case to serve the 10% case.
- **Retrieval that blocks speech kills the conversational feel.** Web search is 1–3s. If the assistant goes silent for 3s, you've lost.

Better shape (detailed in §12–14): **retrieve Obsidian always, inject sometimes; gate the web behind an explicit, trained decision; and never let retrieval block the first audible token.**

### Assumption 4 (unstated): One model does everything

Your best architecture is **two-speed**. A small fast model owns conversation and speaks immediately; hard turns escalate to a larger model (local 8–14B, or a cloud API). Users do not notice a 2-second pause on "explain the tradeoffs of my caching design." They absolutely notice it on "how's it going." Uniform latency is *worse* than bimodal latency that matches question difficulty.

### The thing missing from your list: memory about *you*

You specified project knowledge (Obsidian) and world knowledge (web). You did not specify **episodic/personal memory** — what you told it last Tuesday, your preferences, your ongoing threads, your writing style. This is the single largest driver of "it feels like it knows me," and it is a *storage and retrieval* problem, not a model problem. Add it. Details in §11.

---

## 2. Feasibility (Q1)

Feasible, with these honest caveats:

| Capability | 4B feasibility | Notes |
|---|---|---|
| Natural, fluent conversational text | ✅ Solved | Stock 2026 4B models already do this well |
| Tone/register matching, warmth | ✅ Achievable | Post-training; robust with character training |
| Brevity/verbosity control | ✅ Achievable | Needs explicit training; prompting is unreliable |
| Good follow-up questions | ✅ Achievable | Trainable behavior |
| Turn-taking / interruption handling | ✅ Achievable | Pipeline problem, not model problem |
| Handling corrections & topic shifts | 🟡 Partial | Trainable, but degrades in long contexts |
| Multi-turn state tracking (10+ turns) | 🟡 Weak | **Your hard ceiling.** See below |
| Understanding implicit intent | 🟡 Partial | Capacity-bound |
| Genuine humor | ❌ Unreliable | See §9 — aim for *lightness*, not jokes |
| Reliable abstention / not hallucinating | 🟡 Improvable | Reduce and make visible; never eliminate |

**The multi-turn ceiling is empirically documented.** ["LLMs Get Lost In Multi-Turn Conversation"](https://arxiv.org/abs/2505.06120) found an **average 39% performance drop** across six generation tasks when the same information is delivered across turns instead of in one shot — across *all* top open- and closed-weight models tested. Crucially, they decompose this into a *minor loss in aptitude and a significant increase in unreliability*: "when LLMs take a wrong turn in a conversation, they get lost and do not recover." Follow-up work ([TurnWise, arXiv:2603.16759](https://arxiv.org/pdf/2603.16759)) confirms multi-turn capability is a distinct dimension not captured by single-turn evals.

If frontier models drop 39%, a 4B model drops more. **This is the real limit of your project, and it is architectural, not fixable by more conversational training data.** Your mitigations are system-level: aggressive state summarization, an explicit "current goal" slot maintained outside the model, and periodic context re-grounding. Design for them from day one.

---

## 3. Should you train at all? (Q2)

**Answer: Yes, but only after you've exhausted prompting, and only for four specific things.**

Prompting + good system design gets you: fluency, general tone, most persona, basic follow-ups. Free, instant, zero risk.

Training buys you four things prompting cannot reliably deliver:

1. **Persona robustness under length and pressure.** System-prompt personas decay over long conversations and collapse under adversarial or emotional input. [Open Character Training](https://arxiv.org/abs/2511.01689) demonstrated exactly this — Constitutional-AI-style character fine-tuning on open-weight models produced persona changes "more robust to adversarial prompting" than system prompts or activation steering, with "little to no effect on general capabilities."
2. **Length/format discipline.** Small models ignore "be concise" roughly 30–40% of the time. Trained-in brevity holds.
3. **Tool-gating precision.** When to search Obsidian vs. web vs. neither. Prompt-based gating in small models is noisy; trained gating is dramatically better.
4. **Abstention.** Saying "I don't know" is *anti-natural* for an instruction-tuned model. It must be trained in with explicit negatives.

**Do not train for:** raw fluency, knowledge, or "being smarter." You will not move those, and you risk moving them backwards.

---

## 4. Architecture (Q3)

**Recommendation: do not design a new architecture. Use the base model's architecture unmodified.**

There is no known architectural change that buys conversational quality at this scale. Novel architecture is where hobby LLM projects go to die. The architectural levers that *do* pay off are all inference-side:

| Lever | Benefit | Cost |
|---|---|---|
| **Prompt caching** of system prompt + persona + memory header | Removes 500–2000 tokens of prefill from every turn | Trivial |
| **Speculative decoding** with a 0.6–0.8B draft model | 1.5–2.5× decode speedup | Low |
| **KV cache quantization** (Q8) | Longer conversations at same RAM | Trivial |
| **Sliding-window attention** (already in Gemma 4) | Cheap long context | Free |
| **Sentence-boundary streaming to TTS** | Cuts perceived latency ~40% | Low |

Note Gemma 4's architecture is already well-suited: hybrid local sliding-window + global attention (512-token windows on E2B/E4B), Per-Layer Embeddings on the small variants for on-device efficiency, 128K context ([model card](https://ai.google.dev/gemma/docs/core/model_card_4)).

---

## 5. How small can it be? (Q4)

| Size | Verdict |
|---|---|
| **<1B** | Fluent-sounding, but no reliable multi-turn state or tool-gating. Useful only as a router/draft model. |
| **1–2B** | Good for short casual exchanges. Breaks on corrections, topic shifts, and any tool decision. Viable only if latency is your absolute constraint. |
| **3–5B** | **The sweet spot.** ~2.5–3.5 GB at Q4_K_M. Reliable tool-calling, coherent 10–15 turn conversations, real personality. |
| **7–9B** | Noticeably better on implicit intent and multi-turn recovery. ~5 GB at Q4. Halves your tokens/sec. Best as the **slow-path escalation model**, not the primary. |
| **>12B** | Not a laptop conversational model. Use as teacher or cloud escalation. |

**Target: 4B class as primary, with an optional 8–9B slow path.** Past ~4B, tokens/sec matters more to perceived quality than parameters.

---

## 6. Base models and teachers (Q5, Q6)

### Recommended base models (as of Sept 2026)

| Model | Params | License | Why |
|---|---|---|---|
| **Gemma 4 E4B** ⭐ | 4.5B effective (8B w/ embeddings), 42 layers, 128K ctx | Apache 2.0 | **My primary pick.** Gemma line has the strongest conversational "feel" per parameter. Native **audio input** (E2B/E4B/12B) means you can optionally collapse STT into the model. Per-Layer Embeddings tuned for on-device. |
| **Qwen3.5-4B** | 4B dense, released 2026-03-02 | Apache 2.0 | Strongest alternative. Qwen line has the best tool-calling lineage — pick this if tool reliability is your top concern. |
| **Gemma 4 E2B** | 2.3B effective | Apache 2.0 | Fallback if 4B is too slow on your hardware; also a good router model. |
| **Qwen3.5-0.8B / 2B** | 0.8B / 2B | Apache 2.0 | Router / draft model for speculative decoding. |
| **SmolLM3-3B** | 3B | Apache 2.0 | Only if you want a *fully* open recipe (data + code) for research reproducibility. Reported competitive with 4B-class models across 12 benchmarks. |

**Build both. Fine-tune Gemma 4 E4B and Qwen3.5-4B on identical data and pick the winner by blind A/B.** The base-model choice is cheap to test and you will be wrong if you guess.

### Teacher models

Two distinct uses, with different constraints:

**(a) Teacher for synthetic *data generation*** — any strong model works. A frontier API model produces the best conversational data. ⚠️ **Check the provider's terms of service**: most commercial API providers prohibit using outputs to train competing models. For a personal, non-distributed assistant this is usually permissible, but read it, and do not publish the weights if it isn't.

**(b) Teacher for *on-policy distillation*** — **must be open-weight and self-hosted.** On-policy distillation requires teacher log-probabilities on *your student's sampled tokens*; no API exposes that usefully. Candidates: **Qwen3.6-27B** (Apache 2.0), **Qwen3.5-27B**, **Gemma 4 31B**, or **Qwen3.6-35B-A3B** (MoE — only 3B active, so it's cheap to serve as a teacher).

### Train from scratch, fine-tune, or distill? (Q6)

| Approach | Verdict |
|---|---|
| **From scratch** | ❌ **Absolutely not.** You'd need ~10²²–10²³ FLOPs and trillions of curated tokens to reach parity with a free model. Six figures of compute to build something worse than what you can download. There is no research argument for it either — conversational specialization is a post-training phenomenon. |
| **Continued pretraining** | ❌ Not worth it. High forgetting risk, requires billions of tokens, buys you nothing you can't get from post-training. |
| **SFT (LoRA)** | ✅ **Yes — the core of your work.** |
| **Preference optimization (DPO/KTO/SimPO)** | ✅ **Yes — where the "feel" actually comes from.** |
| **Character training (Constitutional AI)** | ✅ **Yes — for persona robustness.** |
| **On-policy distillation** | ✅ **Yes — high leverage, underused.** See below. |
| **RL with programmatic rewards (GRPO)** | 🟡 Optional stage 5. Only for objectively-scorable behaviors. |

**On-policy distillation deserves special attention.** [Thinking Machines' analysis](https://thinkingmachines.ai/blog/on-policy-distillation/) reports it reaching SFT-equivalent quality at **9–30× lower training compute**, and 7–10× faster convergence than RL. More importantly for you, it solves a problem you *will* hit:

> Fine-tuning Qwen3-8B on internal company documents degraded instruction-following from **85% → 45%** on IF-eval. **Mixing in 30% chat data did not prevent the regression.** On-policy distillation from the original model's behavior restored **83% IF-eval while retaining 41% of the new knowledge.**

Read that twice. **Replay mixing — the standard folk remedy for catastrophic forgetting — was insufficient.** When your conversational SFT damages the base model's instruction-following (it will), on-policy distillation is the documented repair.

---

## 7–9. Data strategy

### Volume (Q7)

**5,000–20,000 high-quality multi-turn conversations.** Not millions. At LoRA scale on a 4B model, quality dominates volume brutally. 3,000 excellent conversations beat 100,000 mediocre ones, and mediocre synthetic data actively *harms* — it installs a style attractor that makes every response sound the same.

### Composition (Q8)

| Category | Share | Purpose |
|---|---|---|
| Casual multi-turn chat (5–15 turns) | 20% | Baseline conversational flow |
| **Context/state tracking** (referring back 5+ turns) | 12% | Directly attacks your weakest axis |
| **Tool-gating: correct decisions** | 12% | Obsidian vs. web vs. neither — *both* directions |
| **Abstention & uncertainty** | 10% | ⭐ Most-skipped, highest-value category |
| Grounded answering from retrieved context | 10% | Using RAG results naturally, with citation |
| **Repair & correction** ("no, I meant...") | 8% | Attacks the "gets lost, doesn't recover" failure |
| Emotional register & support | 8% | Tone matching, when to stop being useful |
| Brevity discipline (short Q → short A) | 6% | Trains the length policy |
| Follow-up question generation | 5% | Only when genuinely needed |
| Topic shifts & interruptions | 5% | Clean pivots without re-preamble |
| Light humor / playfulness / callbacks | 4% | See warning below |

Two categories carry disproportionate weight and are almost always omitted:

- **Abstention data**: conversations where retrieval returned *nothing useful* and the correct response is "That's not in your notes, and I couldn't find anything reliable — want me to search differently?" Instruction-tuned models are trained to always produce an answer; you have to actively untrain that.
- **Repair data**: the user interrupts, contradicts, or corrects mid-conversation. This is precisely the failure mode the multi-turn literature identifies, and it is trainable.

### Generating the data (Q9)

**Pipeline:**

1. **Seed matrix.** Cross-product of `{situation} × {user emotional state} × {desired assistant behavior} × {knowledge requirement}`. ~300 situations × 5 states × 6 behaviors ≈ 9,000 seeds. Generate the matrix programmatically, not by hand.

2. **Two-agent self-chat with an asymmetric user persona.** ⭐ **This is the trick most people get wrong.** Generate the *user* side with a separate model instructed to be a **messy human**: typos, fragments, lowercase, mid-sentence topic changes, "wait no", ambiguous pronouns, unstated context, occasional rudeness. Standard synthetic dialogue has unrealistically clean user turns — which is *exactly* why models fine-tuned on it feel brittle the moment you talk to them naturally. Your data must contain the mess.

3. **Rejection sampling.** Generate 4–8 assistant candidates per turn; have a judge model pick the best against an explicit rubric (appropriate length, no preamble, right register, correct tool decision, no invented facts). Keep the winner for SFT; keep `(winner, loser)` pairs for DPO. You get both datasets from one pass.

4. **Mine your own real conversations.** ⭐ **200–500 real turns where you are the actual user are worth thousands of synthetic ones.** Log every session from day one. This is your only source of *your* actual conversational patterns.

5. **Character-training data.** Follow the [Open Character Training](https://arxiv.org/abs/2511.01689) recipe: write an explicit constitution for your assistant's character (10–20 principles), generate synthetic introspective data, have the model critique and revise its own responses against the constitution, fine-tune on revisions. Released implementation available.

6. **Deliberate diversity injection.** Sample generations at high temperature, use ≥2 different teacher models, and explicitly forbid recurring tics ("Great question!", "Certainly!", "I'd be happy to", em-dash-heavy cadence). Then *measure* n-gram diversity and response-length distribution on your dataset before training. If your data has a style attractor, your model will too, permanently.

### ⚠️ On humor — be honest with yourself

**Humor is the hardest item on your list and the least likely to succeed at 4B.** Humor requires precise world-knowledge collisions, timing, and theory of mind about what the listener finds surprising. Small models trained on "be funny" data reliably produce a specific failure: the *quirky-assistant voice* — forced whimsy, random exclamations, jokes that land nowhere. It is worse than no humor.

**Aim instead for:**
- **Lightness** — brevity, low formality, willingness to be brief and dry
- **Callbacks** — referencing something you said earlier in the conversation ⭐ this is achievable and feels *disproportionately* human
- **Mild self-deprecation** — "I completely lost the thread there, say that again?"
- **Not over-explaining a joke you make** — the single biggest tell

Callbacks are the highest-ROI item here and they're partly a *memory* feature, not a model feature.

---

## 10. How frontier assistants achieve their feel — and what transfers

| Technique | What it produces | Transfers to 4B? |
|---|---|---|
| Massive pretraining scale | Depth of implicit understanding | ❌ No |
| Enormous, expensive human preference data (RLHF) | Fine-grained response calibration | 🟡 Partially — via synthetic preference pairs |
| **Constitutional AI / RLAIF** | Consistent values and character | ✅ **Yes** — [documented on open weights](https://arxiv.org/abs/2511.01689) |
| **Character training** | Stable, robust persona | ✅ **Yes** — this is the most transferable piece |
| Long-context reasoning over dialogue | Multi-turn recovery | ❌ Largely no — your ceiling |
| Extensive red-teaming | Graceful handling of edge cases | 🟡 Partially |
| Careful length/format calibration | Right-sized responses | ✅ **Yes** |
| Tool-use RL at scale | Reliable tool decisions | 🟡 Partially — needs your own GRPO stage |

**What transfers is character, calibration, and format. What doesn't is depth.** Plan accordingly: your model can be *stylistically* excellent and *cognitively* modest. That combination is actually fine for a conversational assistant with good retrieval — and it's exactly what your architecture is set up to exploit.

---

## 11. Internal vs. external knowledge (Q11)

**Keep 100% of the base model's knowledge.** Do not attempt removal. Instead train a **three-way epistemic policy**:

| Class | Examples | Policy |
|---|---|---|
| **Conversational priors** | What a deadline is, how people express frustration, that Paris is in France, basic arithmetic, common idioms | Answer directly, no hedging |
| **Personal / project** | Your architecture decisions, your meeting notes, your reading list, who "Sam" is | **Always** check Obsidian |
| **Specific / volatile / verifiable** | Version numbers, prices, current events, exact statistics, anything dated | **Never** answer from memory. Retrieve or abstain |

Train this taxonomy explicitly with labeled examples in each class, including the boundary cases. The failure mode to train against is a model that *hedges on everything* (annoying, kills conversational flow) or *asserts everything* (dangerous). The distinction is learnable.

### The missing fourth store: personal memory

Add a memory layer separate from Obsidian:

- **Facts about you** — preferences, constraints, people in your life, ongoing projects
- **Conversation summaries** — rolling compressed summaries of past sessions
- **Open threads** — "you said you'd decide on the database by Friday"

Implementation: after each session, a background pass extracts candidate memories, deduplicates against the existing store, and writes to a small SQLite table. Retrieved and injected into the system prompt header each session (and prompt-cached). ~500 tokens.

This is cheap and it is the highest-impact "feels like it knows me" feature in the entire system.

---

## 12. Obsidian retrieval layer (Q12)

**Do not build naive chunk-and-embed.** Obsidian vaults have structure — exploit it.

### Chunking
- **Heading-aware**: chunk = section under a heading; split long sections at paragraph boundaries
- **Prepend the heading breadcrumb** to every chunk (`Projects > ViceBase > Auth decisions > ...`) — massively improves both embedding quality and the model's ability to cite
- Target 200–400 tokens; 15% overlap
- Carry frontmatter (tags, dates, aliases) as metadata, not chunk text

### Retrieval — hybrid, always
- **Dense**: `EmbeddingGemma-300M` or `Qwen3-Embedding-0.6B` (reported 70.7 MTEB-eng-v2, ~1.5 GB, Apache 2.0). Both run locally at ~10–30ms/query.
- **Sparse**: SQLite FTS5 / BM25
- **Fuse** with Reciprocal Rank Fusion

⭐ **Hybrid is not optional for a personal vault.** Your notes are full of idiosyncratic proper nouns, project codenames, and abbreviations that embeddings handle badly and exact-match handles perfectly. Dense-only retrieval on a personal vault is the most common reason these systems feel useless.

### Obsidian-native superpowers
- **1-hop `[[wikilink]]` expansion**: after retrieving a chunk, pull in the linked notes' summaries. Your vault is a graph — generic RAG throws that away.
- **Recency boost** for daily notes and recently-modified files
- **Tag filters** as hard pre-filters when the query mentions a known tag

### Storage
**`sqlite-vec` or LanceDB.** Single file, embedded, no server process. Do **not** run Chroma/Qdrant as a service for a personal vault — you'll be babysitting a daemon for a 5,000-note corpus.

### Indexing
Watch the vault directory; re-index on `mtime` change; debounce 2s. Full re-index of a 5k-note vault: ~2–5 minutes. Incremental: milliseconds.

### Output contract
Every chunk returned must carry `{file_path, heading_path, mtime, score}`. The model cites it; you verify it; the UI links to it.

### ⚠️ The failure mode nobody warns you about
**Your Obsidian vault is not a clean corpus.** It contains half-finished thoughts, superseded decisions, notes-to-self that were wrong, and contradictions. Retrieval will surface a two-year-old note stating the opposite of your current view, and the model will confidently relay it. Mitigations: surface `mtime` in the injected context and train the model to prefer recent notes and to *flag* contradictions rather than silently pick one.

---

## 13. Web search fallback (Q13)

**Pipeline:** query rewrite → search API → fetch top 2–3 → main-content extraction (`trafilatura`) → passage rerank → inject top 1–2k tokens.

- **Search API**: Brave Search API or Tavily (LLM-optimized results). Self-hosted SearXNG if you want zero third-party dependency — slower and flakier.
- **Query rewriting matters more than you'd expect.** A 4B model's raw conversational phrasing makes terrible search queries. Train a dedicated rewrite step, or use a template.
- **Cache aggressively** (24h TTL, keyed on normalized query). You will re-ask the same things.
- **Latency: 1–3s.** This *must* be masked. See §14.

---

## 14. The routing decision (Q14) — the most important design choice

**Do not leave this to free-form model judgment.** Small models are unreliable at tool gating, and both failure directions are costly: over-retrieval is slow and pollutes the context window; under-retrieval hallucinates.

### Layered routing

**Layer 1 — Obsidian: retrieve always, inject sometimes.** ⭐

Local vector search costs ~30ms. Run it on **every** turn, in parallel with the model's first tokens. Then a **score threshold** — not the model — decides whether to inject. This removes the Obsidian routing decision from the model entirely. It is the single best simplification available to you.

**Layer 2 — deterministic pre-checks.** Cheap regex/heuristic signals that set strong priors before any model call: temporal markers (`latest`, `current`, `2026`, `today`), possessives (`my`, `our`, `the project`), question shape, presence of a known vault tag.

**Layer 3 — web search: trained tool call + uncertainty gate.** The model emits a search call, but back it with an uncertainty signal. [TARG (arXiv:2511.09803)](https://arxiv.org/pdf/2511.09803) shows a training-free approach: sample a short no-context draft, compute mean token entropy / margin from the prefix logits, and gate retrieval on that. Cheap and effective, and it catches the case where the model is confidently wrong about being confident.

**Layer 4 — user override.** "Search the web for..." always forces it. "Just answer" always skips it. Non-negotiable escape hatches.

### ⭐ Never let retrieval block the first audible token

When a web search fires, the assistant should **immediately** speak an acknowledgment ("let me look that up") while retrieval runs in the background. This is 90% of what makes the difference between "thinking" and "frozen." It costs nothing and it is the highest-ROI 10 lines of code in the project.

---

## 15. Preventing hallucination (Q15)

Layered, because no single layer is sufficient:

1. **Mode separation.** Explicit system-level state: *chat mode* (no factual claims expected) vs. *answer mode* (all claims must be grounded). This is orchestrator state, not a model whim.
2. **Trained abstention** with explicit negatives (§8). The most important layer.
3. **Citation requirement in answer mode.** Every factual sentence carries a source marker. Ungrounded claims become *visible*, which is nearly as valuable as preventing them.
4. **Post-hoc entailment check.** A small NLI model verifies each factual sentence is entailed by the retrieved context. ~100ms. Flag or strip failures. Worth it for high-stakes queries only.
5. **Calibrated hedging trained in** — "I think", "I'm not certain, but" — with the *policy* of when to use them trained, not prompted.
6. **Show the sources in the UI.** Voice: "according to your note on X." Text: linked citations.

**Be honest with yourself: you will not eliminate hallucination at 4B.** The realistic goal is to reduce it substantially and make the remainder *visible and checkable*. A system that says "I'm not sure, here's where I got this" is more trustworthy than one that's silently right 95% of the time.

---

## 16. STT and TTS (Q16)

### STT
| Option | Why |
|---|---|
| **NVIDIA Parakeet TDT 0.6B v3** ⭐ | Leads the Open ASR leaderboard on WER (~6.3%), native streaming, 600M params. **Transducer architecture is structurally hallucination-resistant** — no audio evidence, no tokens. This matters: Whisper is known to hallucinate confident text on silence and noise, which is catastrophic in an always-listening assistant. |
| Nemotron 3.5 ASR Streaming 0.6B | Similar class; `parakeet.cpp` for easy local deployment |
| Qwen3-ASR-1.7B | Best reported WER (~5.9%) but larger and batch-oriented |
| Whisper large-v3-turbo | Only if you need 99-language breadth |
| **Gemma 4 E4B native audio** | ⭐ Worth prototyping — collapses STT into the LLM, removing a pipeline stage and its latency |

### ⚠️ VAD and endpointing — the unsung hero
**Endpointing quality affects perceived conversational quality more than STT accuracy does.** Cutting the user off mid-sentence, or waiting 1.5s after they clearly finished, both destroy the illusion instantly.

Use Silero VAD + a **semantic endpointing** check ("is this utterance syntactically complete?"). 2026 work on this (FastTurn, JAL-Turn) unifies acoustic and streaming semantic cues. Budget real time for tuning this. It is boring and it matters enormously.

### TTS
| Option | Why |
|---|---|
| **Kokoro-82M** ⭐ MVP | 82M params, Apache 2.0, faster than realtime on CPU, 54 voices. The right default. |
| **Chatterbox Turbo** | 350M, ~75ms latency, ~6× realtime, voice cloning. Reported 65.3% vs 24.5% preference against ElevenLabs in blind testing. The upgrade path. |
| Qwen3-TTS | If you need strong multilingual |

**Stream at clause boundaries.** Do not wait for the full LLM response before starting TTS. Emit the first clause as soon as it's complete. This alone cuts perceived latency ~40%.

### Full-duplex speech models — not yet, for you
Moshi (~200ms end-to-end, runs on a single GPU) and [PersonaPlex](https://research.nvidia.com/labs/adlr/files/personaplex/personaplex_preprint.pdf) (205ms, 100% interruption success on FullDuplexBench vs. 43.9% for Gemini Live) are genuinely impressive on latency and turn-taking.

**But they trade content quality and tool use for it.** For a knowledge-grounded assistant with RAG, the cascaded pipeline is the correct 2026 choice. Revisit in a year. A hybrid is interesting long-term: duplex model handles backchannels and turn-taking, cascade handles content.

---

## 17. Hardware (Q17)

### Training — rent, don't buy

| Stage | Hardware | Time | Cost |
|---|---|---|---|
| LoRA SFT, 4B, 10k convs | 1× A100 80GB | 2–4 h | ~$10 |
| DPO, 4B, 5k pairs | 1× A100 80GB | 2–3 h | ~$8 |
| Character training | 1× A100 80GB | 2–4 h | ~$10 |
| On-policy distillation (27B teacher 4-bit + 4B student) | 1× H100 80GB | 4–8 h | ~$30 |
| GRPO (optional) | 1× H100 80GB | 8–16 h | ~$50 |
| Synthetic data generation | API or rented inference | — | $50–200 |

**Total for the full ladder, including several failed runs: $200–500.** This is not a compute-constrained project. It is a *data-quality and evaluation* constrained project.

Local fine-tuning is possible (24GB consumer GPU with QLoRA; 32–64GB Mac via `mlx-lm` LoRA) and fine for iteration, but rent for the real runs.

### Inference — your laptop

| Config | Verdict |
|---|---|
| 16 GB RAM, Apple Silicon | ✅ Workable — 4B Q4 + Kokoro + embeddings ≈ 5 GB |
| **32 GB, Apple Silicon (M3/M4 Pro or better)** ⭐ | ✅ **Ideal.** Room for the 4B, an 8B slow path, STT, TTS, and embeddings resident simultaneously |
| NVIDIA laptop GPU ≥8 GB VRAM | ✅ Good |
| 16 GB, CPU-only x86 | 🟡 Marginal — expect 8–15 tok/s; usable for text, painful for voice |

**Apple Silicon is the best laptop platform for this**, primarily because unified memory lets you keep every model resident and avoid load/unload thrash between pipeline stages.

---

## 18. Quantization and inference optimization (Q18)

| Technique | Gain | Priority |
|---|---|---|
| **Q4_K_M GGUF** (or MLX 4-bit) | 4× smaller, minimal quality loss | Essential |
| ⭐ **imatrix quantization calibrated on YOUR data** | Meaningfully better preservation of your fine-tune's specific behaviors | High — commonly skipped |
| **QAT checkpoints** if the base ships them | Better than post-hoc quant at same size | High, if available |
| **Prompt caching** (system + persona + memory) | Removes 500–2000 tokens of prefill per turn | ⭐ Essential |
| **Speculative decoding** (0.8B draft) | 1.5–2.5× decode | High |
| **KV cache Q8** | Longer conversations, same RAM | Medium |

**Runtime:** on Apple Silicon, MLX is reported 30–50% faster than llama.cpp for decode (Ollama 0.19, March 2026, switched its Metal path to MLX). ⚠️ **But watch long-context prefill** — at least one analysis found MLX's *effective* throughput including prefill collapsing badly at long context while decode looked fine. **Benchmark end-to-end time-to-first-audio on your actual conversation lengths, not decode tok/s.** Decode tok/s is the number everyone quotes and the wrong number for a voice assistant.

Otherwise: `llama.cpp` (broadest), `Ollama` (easiest), `vLLM` (if you end up on an NVIDIA box).

---

## 19. Realistic latency (Q19)

Voice pipeline, 4B Q4, M4 Pro-class, no web search:

| Stage | Time | Notes |
|---|---|---|
| VAD endpoint detection | 100–300 ms | ⚠️ Tunable; dominates perceived responsiveness |
| STT finalization (streaming) | 100–200 ms | Runs during speech |
| Obsidian retrieval | 20–80 ms | **Parallel — hidden** |
| LLM prefill (cached prompt) | 100–300 ms | Cache is doing heavy lifting here |
| First token | ~50 ms | |
| Tokens for first TTS clause (~15 @ 40–60 tok/s) | 250–400 ms | |
| TTS first audio (Kokoro) | 100–200 ms | |
| **Total time-to-first-audio** | **≈ 700 ms – 1.2 s** | ✅ Feels responsive |

With web search: **2.5–4 s** → mandatory verbal acknowledgment mask (§14).

Text-only chat: **300–600 ms** to first token.

**Benchmark: human conversational gaps average ~200ms.** Sub-1s reads as attentive. 1–2s reads as thoughtful. >2.5s reads as broken. Your target is to keep the common case under 1s and *narrate* everything slower.

---

## 20. Biggest limitations and failure points (Q20)

Ranked by expected pain:

1. **⚠️ Multi-turn degradation.** The 39% figure, worse at 4B. *Mitigation:* rolling summarization, explicit goal slot outside the model, periodic re-grounding, and a "let me make sure I've got this right" recap behavior trained in.
2. **⚠️ Catastrophic forgetting from fine-tuning.** Documented 85%→45% IF-eval collapse; replay mixing insufficient. *Mitigation:* on-policy distillation repair; IFEval as a hard gate on every run.
3. **⚠️ Evaluation blindness.** You will not be able to tell whether you improved. Vibes are unreliable and you are maximally biased toward your own work. *This kills more projects than any technical issue.* See §21.
4. **Tool-gating errors.** Both directions. *Mitigation:* the layered router (§14).
5. **Retrieval quality on a messy personal vault.** Stale and contradictory notes surfaced confidently. *Mitigation:* recency signals, contradiction flagging, hybrid retrieval.
6. **Persona collapse / synthetic style attractor.** Everything sounds the same after SFT. *Mitigation:* multi-teacher generation, diversity measurement *before* training, tic blacklists.
7. **Endpointing errors in voice.** Interrupting the user. *Mitigation:* semantic endpointing, generous tuning time.
8. **Humor falling flat.** *Mitigation:* aim for lightness and callbacks (§9).

---

## 21. Evaluation strategy — the part that decides whether this works

**Build this before you train anything.** Not after. This is the most-skipped and most-important component.

### Frozen scenario set
150–200 held-out conversation scenarios, versioned in git, covering every axis: topic change, mid-conversation correction, incomplete sentence, ambiguity requiring a clarifying question, emotional turn, needs-Obsidian, needs-web, needs-abstention, needs-brevity, needs-depth. **Write these by hand.** It's a weekend. It's the highest-value weekend of the project.

### Automated
- **Pairwise LLM-as-judge** against the previous checkpoint AND against the un-finetuned base with the same system prompt. **Position-swapped** to control for order bias. Never absolute 1–10 scoring — it's noise.
- **Programmatic metrics:** response-length distribution, question rate, tool-call precision/recall, groundedness (NLI entailment vs. retrieved context), abstention rate on deliberately-unanswerable queries, n-gram diversity.
- ⭐ **Multi-turn health metric:** adopt the sharded-instruction methodology from the multi-turn paper — take a task, split its information across N turns, compare against the concatenated single-turn version. **That gap is your single best number.** Track it every run.

### Guardrails (hard gates, every run)
- **IFEval** — catches instruction-following collapse
- **A small MMLU slice** — catches knowledge damage
- If either regresses >5 points, the run is rejected regardless of how good the vibes are.

### Human
Blind A/B, 30 real conversations minimum, before and after every training stage. You talk to two systems without knowing which is which and pick. There is no substitute.

---

## 22. Is there a better architecture? (Q22) — Yes

### The two-speed architecture

```
                    ┌──────────────────────────────┐
   Voice ──▶ VAD ──▶│  STT (Parakeet TDT 0.6B)     │
                    └──────────────┬───────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │  ORCHESTRATOR (plain code)   │
                    │  • conversation state        │
                    │  • mode: chat | answer       │
                    │  • deterministic pre-checks  │
                    └──┬────────────┬──────────────┘
       always, parallel│            │
                       ▼            ▼
        ┌──────────────────┐   ┌─────────────────────────────┐
        │ Obsidian search  │   │  FAST PATH                  │
        │ (hybrid, ~30ms)  │──▶│  Conversational 4B (tuned)  │──▶ speaks
        │ inject if score  │   │  owns tone, flow, gating    │    immediately
        │ > threshold      │   └────────────┬────────────────┘
        └──────────────────┘                │ escalate if hard
        ┌──────────────────┐                ▼
        │ Personal memory  │   ┌─────────────────────────────┐
        │ (SQLite)         │──▶│  SLOW PATH                  │
        └──────────────────┘   │  8–14B local, or cloud API  │
        ┌──────────────────┐   │  masked by verbal ack       │
        │ Web search       │──▶└────────────┬────────────────┘
        │ (gated, 1–3s)    │                │
        └──────────────────┘                ▼
                                 TTS (Kokoro/Chatterbox)
                                 streamed at clause boundaries
```

**Why this is better than your original design:**

| Your design | This design |
|---|---|
| One model decides everything | Deterministic code decides what code can decide |
| Retrieval on the critical path | Obsidian retrieval parallel and hidden |
| Model gates Obsidian access | Score threshold gates it — removes an unreliable decision |
| Uniform latency | Bimodal latency matched to question difficulty |
| Silence during retrieval | Verbal acknowledgment masks it |
| No personal memory | Explicit memory store |
| Model must be smart enough for hardest turn | Model must be *pleasant* enough for the common turn |

⭐ **The core principle: the small model's job is to be a great conversationalist, not a great decision-maker.** Every decision you can move into deterministic code or a threshold, you should.

---

## 23. In the model vs. outside the model

### Inside the LLM (trained in)
- Conversational style, register, warmth, personality
- Length/verbosity policy
- Turn-taking behavior and follow-up question policy
- Tool-*call* formatting and gating priors
- Abstention behavior and calibrated hedging
- Grounded-answering behavior (using retrieved context naturally, citing)
- Repair behavior (handling corrections, topic shifts)
- Basic world knowledge as conversational priors — **inherited, never trained**

### Outside the LLM (tools, code, storage)
- **All** factual/project/personal knowledge → Obsidian index
- **All** current information → web search
- Conversation state, rolling summaries, current-goal slot
- Personal memory store
- The routing thresholds and deterministic pre-checks
- STT, VAD, endpointing, TTS
- Groundedness verification (NLI)
- Prompt cache, speculative decoder
- The system prompt ⭐ **version this in git — it is a training artifact, not a config string**

**Rule of thumb: if it changes when facts change, it belongs outside. If it changes when you want a different personality, it belongs inside.**

---

## 24. Development phases

### Phase 0 — Baseline (weekend) — **do not skip**
Stock Gemma 4 E4B + a carefully written system prompt + naive Obsidian RAG + Kokoro TTS + Parakeet STT. No training.
**Deliverable:** a working voice assistant, and an honest measurement of how far prompting alone gets you.
*Most people who skip this end up training a model that's worse than this baseline and never find out.*

### Phase 1 — Evaluation harness + data pipeline (1–2 weeks)
Frozen scenario set. Judge harness. Synthetic generation pipeline with the messy-user persona. Conversation logging from day one.
**Deliverable:** you can now *measure* change.

### Phase 2 — MVP (2–4 weeks)
- 8–10k synthetic conversations + your logged real ones
- LoRA SFT on Gemma 4 E4B *and* Qwen3.5-4B; blind A/B; pick a winner
- DPO on rejection-sampling pairs
- Hybrid Obsidian retrieval with heading breadcrumbs + wikilink expansion
- Layered router; retrieve-always-inject-sometimes
- imatrix Q4_K_M quantization on your own data
- **Gates:** IFEval within 5 pts of base; multi-turn gap measured; blind A/B win rate >60% vs. Phase 0

### Phase 3 — Advanced (4–8 weeks)
- Character training (Constitutional AI recipe)
- On-policy distillation from Qwen3.6-27B to repair forgetting
- Personal memory layer + session summarization
- Slow-path escalation to a local 8–9B or cloud API
- Speculative decoding, prompt caching, KV quantization
- Semantic endpointing; Chatterbox Turbo with a cloned voice
- NLI groundedness verification

### Phase 4 — Ideal (ongoing)
- GRPO with programmatic rewards (tool-call correctness, abstention accuracy, length adherence)
- Continuous learning from your own logged corrections
- Contradiction detection across the vault
- Revisit full-duplex speech when open models close the content gap

---

## 25. Final recommendation

> **If I were building this today on a realistic personal/laptop budget, this is exactly how I would build it:**

1. **Base:** Gemma 4 E4B (4.5B, Apache 2.0, 128K context, native audio). Fine-tune Qwen3.5-4B in parallel and pick by blind A/B. Never guess this.

2. **Never pretrain. Never continue-pretrain.** Post-training only.

3. **Spend the first two weeks on the evaluation harness and data pipeline, not on training.** Build the frozen 150-scenario set by hand. This decides whether the project succeeds.

4. **Build the Phase 0 prompt-only baseline first** and measure it honestly. It will be better than you expect, and it is the bar every trained checkpoint must clear.

5. **Training ladder:** LoRA SFT (10k conversations) → DPO (from rejection-sampling pairs) → Character training (Constitutional AI) → On-policy distillation repair from Qwen3.6-27B. ~$300 rented compute. Gate every stage on IFEval and the multi-turn gap.

6. **Data:** 10k synthetic conversations, generated as two-agent self-chat with a **deliberately messy user persona**, plus every real conversation you have with it from day one. Weight abstention, repair, and tool-gating far higher than feels natural.

7. **Keep all the knowledge in the model.** Train the three-way epistemic policy instead — priors / personal / volatile.

8. **Obsidian: hybrid BM25 + dense, heading-breadcrumb chunks, 1-hop wikilink expansion, sqlite-vec.** Retrieve on every turn in parallel; a score threshold decides injection, not the model.

9. **Web search: trained tool call + entropy-based uncertainty gate + always speak an acknowledgment before the wait.**

10. **Add the personal memory layer you didn't ask about.** It's cheap and it's the biggest "knows me" win available.

11. **Two-speed architecture.** 4B fast path speaks immediately; an 8–14B or cloud slow path handles hard turns behind a verbal mask.

12. **Voice: Parakeet TDT 0.6B (transducer — won't hallucinate on silence) → Kokoro-82M, streaming at clause boundaries, with real time budgeted for endpointing tuning.** Target sub-1s time-to-first-audio.

13. **Quantize with imatrix calibrated on your own conversation data.** Prompt-cache the system header. Speculative-decode with a 0.8B draft.

14. **Optimize time-to-first-audio, not decode tokens/sec.** It is the number that determines whether this feels conversational.

### The honest bottom line

**Your idea is sound, your architecture needs restructuring, and your effort allocation is inverted.**

You framed this as a model-training project with some plumbing attached. It is a **systems project with some model-training attached**. The fine-tune is real and worth doing — it's the difference between "a small model with a personality prompt" and "an assistant with a character" — but it's roughly 20% of the outcome, and it's the 20% you should do *last*, after you can measure it.

Do it in the order above and you will end up with something genuinely good. Start with the fine-tune and you will spend three months producing a model you cannot prove is better than the one you could have downloaded on day one.

---

## Sources

- [LLMs Get Lost In Multi-Turn Conversation](https://arxiv.org/abs/2505.06120) — 39% average multi-turn degradation; aptitude vs. unreliability decomposition
- [TurnWise: The Gap between Single- and Multi-turn Language Model Capabilities](https://arxiv.org/pdf/2603.16759)
- [Physics of Language Models: Part 3.3, Knowledge Capacity Scaling Laws](https://arxiv.org/abs/2404.05405) — 2 bits/parameter
- [Open Character Training: Shaping the Persona of AI Assistants through Constitutional AI](https://arxiv.org/abs/2511.01689)
- [On-Policy Distillation — Thinking Machines Lab](https://thinkingmachines.ai/blog/on-policy-distillation/) — 9–30× compute reduction; catastrophic forgetting repair
- [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4)
- [Qwen3.5 / 3.6 / 3.8 release history](https://github.com/QwenLM/Qwen3.8)
- [Retrieval as a Decision: Training-Free Adaptive Gating for Efficient RAG (TARG)](https://arxiv.org/pdf/2511.09803)
- [PersonaPlex: Voice and Role Control for Full Duplex Conversational Speech Models](https://research.nvidia.com/labs/adlr/files/personaplex/personaplex_preprint.pdf)
- [Best open source speech-to-text models 2026 — benchmarks](https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks)
- [Best open source TTS models 2026](https://www.tryspeakeasy.io/blog/open-source-text-to-speech-2026)
- [MLX vs llama.cpp on Apple Silicon — 2026 benchmarks](https://www.compute-market.com/blog/mlx-vs-llama-cpp-apple-silicon-2026)
- [OpenCharacter: Training Customizable Role-Playing LLMs with Large-Scale Synthetic Personas](https://arxiv.org/abs/2501.15427)
- [PIPPA: A Partially Synthetic Conversational Dataset](https://arxiv.org/pdf/2308.05884)
