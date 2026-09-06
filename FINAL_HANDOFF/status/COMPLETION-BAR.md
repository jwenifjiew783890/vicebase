<!-- Extracted verbatim from reports/01-FINAL-REPORT-R3.md.
     Do not edit here; edit the report and re-extract. -->

# Acceptance criteria — did each one pass?

Two scorecards. The first is the 32-point completion bar from brief 5.
The second scores the original 22 R&D questions from brief 1.

**Both are reproduced verbatim from the final report.**

---

## 32. The completion bar, item by item

Thirty-two requirements. Each row carries the evidence, not an opinion.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Runtime implemented | **YES** | 14 modules, 386 tests, real llama.cpp inference |
| 2 | Model selected + justified | **YES** | §4; the Gemma → Qwen reversal is documented with its reason |
| 3 | Memory works | **YES** | Four tiers; bitemporal supersession; and since round 4 it learns facts from conversation rather than from an API call. §23 runs the whole chain with the real model |
| 4 | Learning loop works | **YES** | §12, end to end, 45w → 30w on a fresh session — and only because the rule is enforced as a token cap |
| 5 | Personal adaptation works | **YES** | Durable rules across sessions + in-session corrections (F30), which is the half that was missing |
| 6 | Obsidian retrieval works | **YES** | §25; hybrid, threshold-gated; V1/V2 probe both directions |
| 7 | Web fallback works | **YES** | And it was **not** working before round 3 — see §3.3. W1/W2 probe both empty and successful searches |
| 8 | Tool/agent orchestration | **YES** | And it was **not** working before round 3 — 0/12 → 11/12 reaching the gateway (§3.1) |
| 9 | OpenCode ready | **PARTIAL** | Client tested against a real HTTP server; deterministic briefs refuse to guess. OpenCode itself is **NOT installed** here |
| 10 | Voice: works or gaps identified | **PARTIAL** | Policy fully tested including the confirmation rule; every audio model **NOT TESTED** (§11) |
| 11 | English fluent | **YES** | 68 conversations, zero assistant tells |
| 12 | Hindi natural | **YES** | The strongest result in the project; no fine-tuning |
| 13 | Hinglish natural enough | **YES** | Mirrors the mix including the switch point mid-sentence |
| 14 | Adapts to style | **YES** | §12; and F30 fixed the case where the adaptation was too slow to be visible |
| 15 | Not sycophantic | **YES** | A05: held twice under direct contradiction, with vault evidence |
| 16 | Disagrees naturally | **YES** | *"No, you didn't."* — then explained, without being rude |
| 17 | Says it doesn't know | **YES** | M07, W1, B1, X1 — including under recall pressure (§23) |
| 18 | No hallucination when retrieval fails | **YES** | And it was **not** true before round 3 (§3.3). Four guards now, one per phrasing that got past the previous one -- the last of them caught live in round 4b |
| 19 | Simple conversation fast | **UNVERIFIED on GPU** | Everything outside the model is sub-20 ms. Model latency is CPU-only here |
| 20 | Slow ops masked | **YES** | And the acknowledgement no longer lies about what it is masking (F19) |
| 21 | Tool execution secure | **YES** | §9; and the gateway is now actually reachable, which it was not |
| 22 | Injection tested | **YES** | Corpus + normalisation + taint; DENY on every payload through three capabilities |
| 23 | Dangerous voice actions confirmed | **YES** | `git.push`/`file.delete` → CONFIRM_TYPED by voice, measured live. This was a **false green** until round 3 (§3.2) |
| 24 | Memory contradictions handled | **YES** | Supersession, not overwrite; history stays queryable |
| 25 | Preferences superseded | **YES** | `valid_to` / `superseded_by`; the prompt carries only the current value |
| 26 | T3 bounded | **YES** | Peak 10 of a cap of 40 over a simulated 180 days; protected rules exempt |
| 27 | Regression passes | **YES** | 386 tests + 183 scenarios + 94 mutations |
| 28 | Real conversational tests | **YES** | 110 transcripts, 373 user turns, four rounds plus a verification pass, all committed |
| 29 | Transcripts reviewed | **YES** | Every failure in `docs/CONVERSATION-FAILURES.md` is quoted from one |
| 30 | Every major failure repaired + retested | **YES** | 46 documented, 46 addressed, each with a regression test and a mutation. Five of them were found by the rounds that verified the previous ones, and the last (F46) by a check on a measurement rather than on the system |
| 31 | Independent adversarial tests | **YES** | 8 defence probes, the mutation audit, the planner-reliability harness, the before/after replay, and `eval/extractor_sweep.py` over all 373 real turns |
| 32 | Better than the baseline | **YES** | Measured on register, brevity, tells, variety, honesty and safety reachability |

**28 YES · 3 PARTIAL/UNVERIFIED · 0 NO.**

The three that are not YES are all **hardware**: OpenCode is not installed,
there is no audio device, and there is no GPU. None of them can be resolved
by more work in this environment, and none of them is a design question.

### Three of these were YES before they were true

Rows 8, 18 and 23 were marked YES in an earlier version of this report, on
the strength of unit tests that passed. All three components were
unreachable at runtime. They are YES now because a real conversation
reached them and the transcript shows it — which is a different and much
stronger claim than the one I made before.

---

---

## 33. Honest scorecard against the original 22 questions

You asked 22 questions at the start. Short answers, with the evidence
behind each.

| # | Question | Answer |
|---|---|---|
| 1 | Is a conversation-first small LLM feasible? | **Yes, but not as a model project.** The conversational quality was there at 4B on day one; everything that needed building was around it. |
| 2 | What architecture? | Dense decoder, 4B, instruction-tuned. Nothing exotic was needed or would have helped. |
| 3 | What size? | 4B is the floor for natural Hindi and the ceiling for 6 GB with STT alongside. |
| 4 | Which base model? | Qwen3.5-4B. Reversed an earlier Gemma lean on Indic evidence. |
| 5 | Train, fine-tune or distil? | **None of the three, yet.** 34 of 39 failures were outside the weights. |
| 6 | What data? | Not needed for what was actually broken. If it becomes needed, it is brevity and register data, not knowledge. |
| 7 | Synthetic data? | Deferred for the same reason. |
| 8 | How do frontier assistants feel conversational? | Post-training and restraint, not scale. This project reproduces the restraint part in code. |
| 9 | Internal vs external knowledge? | Definitional questions internal; anything personal, current or verifiable retrieved. Enforced by the router, not by the model. |
| 10 | Obsidian RAG? | Yes — heading-aware chunks, hybrid retrieval, threshold-gated injection. |
| 11 | Web fallback? | Yes, and it now actually runs (§3.3). |
| 12 | Who decides to search? | The router, deterministically. Never the model. |
| 13 | Hallucination prevention? | Threshold gating, a categorical empty-retrieval directive, and **three** enforced guards -- one per phrasing of the lie that got past the previous one. |
| 14 | STT/TTS? | Designed, policy-tested, models NOT TESTED. |
| 15 | Hardware? | Fits 6 GB with ~1.9 GB headroom (§30, arithmetic). |
| 16 | Quantisation? | Q4_K_M. Q5 would fit but leaves no room for STT. |
| 17 | Latency? | Sub-20 ms outside the model. Model latency NOT TESTED on GPU. |
| 18 | Limitations? | §15, nine of them, ordered by how much they would bother you in daily use. |
| 19 | Would it feel more conversational? | **Yes** — measured on register, brevity, tells and variety. |
| 20 | Better architecture? | Yes: the one in §1, which is not a model. |
| 21 | A small conversational LLM, or a personal AI around one? | **The second**, and the evidence is 34/39. |
| 22 | Challenge my assumptions | §16. |

---

---

## 34. Verdict

**What was asked for and delivered:** a personal AI that is conversational
first, works in English, Hindi and Hinglish, remembers across sessions —
including things you only *said*, not things you filed — learns how you
like to be spoken to, reaches your notes and the web, can drive tools
behind a permission gate, and fits on a 6 GB laptop GPU. All of it is
implemented, wired and tested, and every claim in this report carries its
evidence label.

**What is genuinely good:** the Hindi. It required no fine-tuning and it is
the thing that would make this feel like yours rather than like a product.
Close behind: the model does not fold under pressure when the vault
disagrees with you, and it says it does not know.

**What is genuinely not proven:** anything that needs the GPU or a
microphone. Not "probably fine" — unknown.

**The finding I would want you to take away** is not in any of the code.
It is that three defences in this system were unit-tested, green, and
never once reached at runtime, and that the only thing that found them was
running the whole thing and reading what it said. The permission system had
never seen a permission request. The web path had never made a request. The
scenario written to test dangerous voice actions tested nothing at all.

You insisted on that phase over my inclination to write it up. You were
right, and the report you are reading is a different and much more honest
document because of it.

**And the second finding, which is the same one seen from the other side:**
six of the forty-six failures were self-inflicted — introduced by a fix
for an earlier failure, or by the tooling. One of them, the marker list
that made *"push this to main"* read as Hinglish, was found by inspection
rather than by a test I had already written. Three more were defences whose
tests another defence also satisfied, so disabling any one of them changed
nothing; the mutation audit found those and a green suite never could.

Every defence in this system now has a test that fails when **that defence
alone** is removed. That is a stronger and much less comfortable standard
than "every defence has a test", and the difference between them is the
difference between a suite that measures your code and one that flatters
it.

**What I would not claim:** that it is finished. Round 4b found nothing
new, and it ran four conversations chosen because they had already failed.
A fifth full round would find more. The rate at which it finds them is
falling slowly; what has fallen fast is what they cost — from a permission
system that had never seen a permission request, to a reply that said
"Project Shield" instead of "Thornbury".
