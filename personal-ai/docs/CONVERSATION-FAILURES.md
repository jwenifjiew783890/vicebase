# Conversational failure log

Every entry was found by reading an actual transcript from a real
Qwen3.5-4B-Q4_K_M running locally. Test IDs refer to
`eval/transcripts/v1/*.txt`.

Status legend: **FIXED** = change made and regression-tested ·
**PROMPT** = addressed in persona v2, awaiting round-2 retest ·
**OPEN** = not yet addressed.

---

## F1 — Confabulated a personal memory  ·  test 001, turn 4  ·  PROMPT

```
USER: i'm bored honestly
AI:   bored? try watching that new thriller Muaz mentioned, or just scroll
      through the news for 5 mins before lying down.
```

There is no thriller in the vault, in memory, or anywhere in the prompt.
The model invented a personal detail to sound close to the user. It also
referred to him in the third person while talking to him.

**Root cause.** The v1 persona said "You are Muaz's personal assistant" —
third person — and supplied a memory block. With an empty memory block the
model still pattern-matched to producing personal-sounding specifics.

**Why it matters most.** This is the exact behaviour the whole architecture
exists to prevent. Retrieval, grounding and abstention are all defeated if
the model manufactures the *premise* rather than the answer.

**Fix.** Persona v2: address the user as "you"; an explicit NEVER INVENT HIS
LIFE clause naming the memory block and retrieved context as the only
admissible sources of personal detail.

---

## F2 — Web search triggered by an emotional statement  ·  test 002, turn 4  ·  FIXED

```
USER: aaj bahut thak gaya hoon        ("I'm very tired today")
AI:   [route=web  ack='ek sec, let me check']
```

The user said he was tired. The assistant went to search the web.

**Root cause.** `VOLATILE` matched the token `aaj` ("today"). A temporal
word was treated as evidence that the turn wanted current information.

**Fix, and a fix to the fix.** First attempt required an explicit
interrogative, which over-corrected and broke noun-phrase queries
("current price of bitcoin", "latest release notes for llama.cpp") — real
things people say with no question mark and no wh-word. Final logic inverts
it: a volatile marker counts *unless* the turn is the user describing
themselves (`SELF_STATE`, or first-person with no request verb).

**Regression cover.** 10 new frozen scenarios (`volstate_*`, `volquery_*`).
`volstate_02/03` assert `not_path="web"` rather than an exact path, because
they also trip a spurious vault match under the stand-in embedder — the
invariant under test is "never search the web for this", not the artifact.

---

## F3 — Common Hinglish classified as English  ·  test 002, turn 3  ·  FIXED

```
USER: bas timepass
AI:   [lang=en]   (correct: hi / hinglish)
```

**Root cause.** `bas` sits in the deliberately-neutral ambiguous bucket and
`timepass` was unknown, so it fell through to the English default. In a
voice deployment this routes the reply to the wrong TTS voice.

**Fix.** ~30 everyday Hinglish nouns added to the marker set (timepass,
badhiya, mast, jugaad, tension, haal, kaam, ghar, office …).

---

## F4 — Ends every turn with a question  ·  test 002  ·  PROMPT

Question rate **100%** across the conversation: "Kya haal hai?" / "Thoda
break chahiye?" / "ya sirf chillana hai?". A question every single turn is a
tic, and the user named it explicitly ("whether it asks unnecessary
questions").

**Fix.** Persona v2 QUESTIONS clause: ask only when the answer is needed,
and it is fine to respond and stop.

---

## F5 — Verbosity escalates across turns  ·  test 003  ·  PROMPT

Reply length grew **16 → 31 → 79 words** over three turns, with the longest
reply given to the shortest prompt ("hmm, tu kya sochta hai").

**Root cause.** The v1 persona said "match his length" but nothing stopped
the growth ratchet as context accumulated.

**Fix.** Persona v2 LENGTH clause states the default explicitly (one or two
sentences) and forbids growth over a conversation.

---

## F6 — Invented a citation  ·  test 003, turn 3  ·  PROMPT

```
AI: ... toh user experience "broken" lagta hai (Source: General UX principles).
```

**Root cause — and this one is self-inflicted.** The protected rule
`honesty.grounded` says "when answering from retrieved material, state
where it came from." Nothing was retrieved on this turn. The model applied
the citation habit anyway and fabricated a source label.

An honesty rule produced a dishonesty artifact. Rules written for the
grounded case need an explicit statement of what to do in the ungrounded
case, or the model will generalise the wrong way.

**Fix.** Persona v2 SOURCES clause: cite only actual retrieved notes or
pages; when answering from own knowledge, add no source line at all; a
made-up citation is worse than none.

---

## F10 — An explicit in-conversation correction was ignored  ·  test 004  ·  PROMPT + ARCHITECTURE

Persona v1, measured: `mean_words = 95.0  max = 122  question_rate = 0%`

Conversation 004 is the brevity test:

```
USER: explain what an API is
AI:   [long answer]
USER: arre nahi, itna bada answer mat do. simple bol.
      ("no, don't give such a big answer. keep it simple.")
AI:   ...
USER: ok now explain what a database index is
AI:   [still ~95 words]
USER: and what's a cache
AI:   [still ~95 words]
```

The user gave an unambiguous instruction in his own words and the model
carried on at the same length for the rest of the conversation.

**Why this is the most important failure in the set.** Everything else is a
polish problem. This one goes to the premise of the product -- *"the AI
should get better at talking to me."* If a direct correction does not
survive to the next turn, nothing downstream matters.

**Two distinct failures needing different fixes.**

1. *Within the conversation.* The model should have shortened immediately.
   That is a prompt and post-training problem. Persona v2's LENGTH clause
   is the first attempt; if prompting proves insufficient, this is exactly
   what the SFT brevity data exists for.

2. *Across conversations.* Even a model that obeys perfectly in-session
   forgets at the next session boundary. That is what T3 procedural memory
   is for, and it is why the learning loop is architecture rather than a
   nice-to-have. `eval/learning_e2e.py` tests precisely this chain.

The architecture already anticipated (2). Round 1 shows (1) is real too, and
that the two are independent -- a promoted rule does not help if the model
ignores instructions inside a single conversation.

---

## F7 — Reasoning trace leaked to the user  ·  found by inspection  ·  FIXED

`_strip_thinking` removed well-formed `<think>...</think>` blocks, but on an
**unterminated** block — what happens when the model hits its token budget
mid-thought — it split on the tag and returned the last fragment, which is
the reasoning itself.

```python
_strip_thinking("<think>I should say hi but first")
# returned: "I should say hi but first"     <- the model's private notes
```

In a voice deployment that is spoken aloud. Anything after an unclosed
`<think>` is now dropped entirely; the caller gets an empty string and can
retry or fall back. 18 adapter tests added.

**How it was found.** Not from a transcript — from writing tests for the
adapter layer separately from inference. Worth noting because it is the kind
of defect conversation testing alone would have missed until it fired.

---

## F8 — Engineering notes were being sent to the model  ·  found by inspection  ·  FIXED

Persona v2 was written with provenance markers so the reasons for each
clause stayed attached:

```
Never let your replies get longer as a conversation goes on.
[test 003: replies grew 16 -> 31 -> 79 words across three turns]
```

Those markers shipped **inside the system prompt**, on every turn. They are
notes for the engineer. They cost context and hand a 4B model stray tokens
to misread. Moved to a Python comment; prompt shrank 2237 → 2006 chars.

**How it was found.** By printing the assembled system prompt and reading
what the model actually receives, rather than reading the source. Worth
doing at least once for any prompt that is built from parts.

---

## F9 — Mixed grammatical person in one system prompt  ·  FIXED

The persona addresses Muaz as "you"; stored rules are third person ("the
user"), because that is how they read in the review queue and audit log.
Both landed in the same prompt.

The first fix was a naive replace and produced:

```
- Disagree when you is wrong, and say why.
```

Final version is an ordered longest-first table that handles verb agreement
("the user is" → "you are", "the user's" → "your", …).

---

## F11 — Persona instructions regress toward the mean at 4B  ·  A/B  ·  ARCHITECTURAL

The most consequential finding, and it is about the *fix strategy* rather
than the model's manners.

Persona v2 (1583 chars, 284 words, a dedicated clause per defect) vs v1
(480 chars), identical inputs, fixed seed:

| case | metric | v1 | v2 | |
|---|---|---|---|---|
| 001 casual EN | mean words | 7.8 | 13.0 | **worse** |
| 001 | question rate | 50% | 75% | **worse** |
| 002 casual HI | mean words | 15.2 | 14.5 | marginal |
| 002 | question rate | 100% | 100% | **no change** |
| 003 Hinglish | mean words | 42.0 | **23.0** | **better** |
| 003 | max words | 79 | **33** | **better** |
| 003 | question rate | 67% | **33%** | **better** |

**My first reading was wrong and worth recording as wrong.** After two
cases I logged this as "prompt instructions are a weak lever". Case 003
then showed a large, clean win — the verbosity escalation (F5) is fixed,
79 → 33 max words.

**The actual pattern is regression toward the mean.** The LENGTH clause
says "default to one or two sentences". That *lengthens* a one-word reply
("hey" → a sentence) and *shortens* a 79-word one. v2 pulls both tails
toward the same middle. It is doing exactly what it was told; the
instruction was simply not the right shape for a behaviour that should
depend on context.

What the correction should have said is closer to "match his length" —
a *relative* rule, not an absolute one. v1 actually said that and got
7.8 words on casual turns; it just had no brake on growth.

**What did not move at all:** the question rate on case 002, at 100% under
both personas despite v2 stating plainly "Do not end every message with a
question." A direct, unambiguous negative instruction had zero measured
effect. That specific failure does look like a lever the prompt cannot
pull, and it is the clearest single argument in this whole exercise for
post-training over prompting.

**The asymmetry that matters for the architecture.** Every fix made in
deterministic code held: routing (F2), language ID (F3), reasoning leak
(F7), prompt assembly (F8/F9), tool honesty. Every fix attempted by
instruction was partial or reversed. That asymmetry is the practical
argument for keeping as much behaviour as possible outside the model.

**Consequent action.** Persona v3 (318 chars) tests the counter-hypothesis:
fewer, positively-phrased, *relative* constraints. Untested — it is a
hypothesis, not a conclusion, and it should get its own A/B before anyone
believes it.

---

## Cross-cutting observations (round 1)

**What was already good, unprompted, at 4B:**
- Genuinely natural spoken Hindi — *"Bhai, sab badhiya. Tu?"*
- Correct register mirroring on Hinglish input
- Zero generic-assistant tells across 11 measured turns (no "Great
  question", no "I'd be happy to")
- Clean short openers on casual turns ("hey" → "hey")
- 100% opener variety; cross-turn repetition 0.00–0.04

**The pattern in the failures:** none of them are the model failing to be
fluent. All six are the model failing to be *disciplined* — inventing
detail, over-asking, over-growing, over-citing. That is consistent with the
prior that conversational polish at 4B is a post-training and
prompt-discipline problem, not a capacity problem.
