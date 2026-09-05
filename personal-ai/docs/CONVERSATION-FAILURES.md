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
