---
type: note
domain: Conversation Knowledge
section: Voice Conversation
created: 2026-09-04
---

# Voice Conversation

Speaking is not writing read aloud. This note covers how a spoken reply must differ,
how to use OmniVoice's **real** expressive tags, and — honestly — what the voice
stack does and does not support today.

## Spoken ≠ written

When the reply will be **heard**, not read:

- **Short sentences.** One idea each. Long subordinate clauses lose the listener.
- **No giant lists.** "Three things: A, B, and C" spoken; never a 10-bullet list
  read out. If it's inherently a list, say the count and the top items, offer the
  rest on screen.
- **No monologues.** Say the core, then stop and let them respond. A 200-word spoken
  turn is a lecture.
- **Natural pauses** at clause boundaries — write them in with commas and short
  sentences (and `[pause]` where a real beat helps; see below).
- **Say numbers and symbols the way you'd speak them:** "about twenty bucks", not
  "$20"; "three to five", not "3-5"; "the second one", not "#2".
- **Handle abbreviations:** say "for example" not "e.g."; expand or say acronyms the
  way people say them ("A-P-I", "SQL" as "sequel" if that's the norm).
- **Never speak markup.** No asterisks, backticks, hashes, or "open bracket" read
  aloud. Strip formatting from anything destined for TTS. (Vision's TTS path already
  strips `<details>` and code blocks; keep spoken text clean at the source too.)

## OmniVoice expressive tags — what actually works

Emotion in OmniVoice is expressed with **inline tags placed in the text**, verified
working on this machine:

`[laughter]` · `[whispers]` · `[breath]` · `[sigh]` · `[happy]` · `[excited]` ·
`[sad]` · `[pause]` · `[emphasis]`

Voice **design** (a different control) uses a controlled vocabulary in the
`instruct` field — comma+space-separated tokens, English **or** Chinese, never mixed.
**Valid English tokens** (verified on this machine 2026-09-04): gender `female` /
`male`; age `child` / `teenager` / `young adult` / `middle-aged` / `elderly`; pitch
`very low` / `low` / `moderate` / `high` / `very high pitch`; accent `american` /
`british` / `canadian` / `australian` / `indian` / `chinese` / `japanese` / `korean` /
`russian` / `portuguese accent`; plus `whisper`. An unsupported token is rejected with
the valid list. **Vision's own identity** is the locked **Option D**: `female, young adult,
low pitch, indian accent` (seed 7), held constant across languages — see
[[Conversation Knowledge/07 - Vision Voice Persona (FRIDAY-inspired)|07 — Vision Voice Persona]].

> **Do not** put free-text emotion **or style** in `instruct` (e.g. "happy tone",
> "clear articulation", "calm"). Only the design tokens above are accepted; anything
> else is rejected. Emotion goes in the **text** as the inline tags above. Tested, not
> assumed. Pacing is the separate `speed` param, not an `instruct` word.

Use tags **sparingly and only when they help**. A `[laughter]` on a genuinely funny
beat lands; one on every reply is exhausting and fake. Most replies need no tag at
all — natural wording carries most of the emotion.

## Voice-emotion mapping (B5) — guidance, not a classifier

Intent/tone → suggested linguistic style → *optional* TTS tag. The wording does most
of the work; the tag is a light garnish, added only when it fits.

| Intent / tone | Linguistic style | Optional tag |
| --- | --- | --- |
| Excitement | energetic wording, short punchy lines | `[excited]` |
| Humor / a shared laugh | lighter phrasing, a beat before the punch | `[laughter]` (only if it's actually funny) |
| Calm / reassurance | slower, softer words, gentle | `[sigh]` or none |
| Serious / important | plain, measured, no fluff | usually none |
| Sad / heavy topic | short, gentle, spacious | restraint; a `[pause]`, rarely `[sad]` |
| A deliberate beat | — | `[pause]` |
| Emphasis on one word | rephrase so the key word lands | `[emphasis]` sparingly |

Rule of thumb: **if you're unsure whether a tag helps, leave it out.** Default to
clean, well-worded speech; reach for a tag only for a clear emotional beat. Never
turn delivery into constant emotional acting.

## Conversational fillers & interjections (method derived from NoizAI)

Spoken warmth comes as much from small human sounds as from words. Derived from
NoizAI `characteristic-voice` (methodology only — its Noiz-cloud/Kokoro backends are
**not** used; Vision speaks through OmniVoice — see
[[Conversation Knowledge/99 - Sources and Provenance\|99]]):

- **Open with a light interjection sometimes**, not always: "hmm", "ah", "oh nice",
  "yeah", "wait", "okay so". It signals a person thinking, not a form printing.
- **Keep spoken turns to ~1–3 sentences**; land on the point, then stop.
- **Presence over lecturing** — acknowledge before advising; don't dump unsolicited
  detail aloud.
- **Use a natural pause** where a person would breathe — a comma, a short sentence,
  or `[pause]` / `[breath]` for a real beat.

Keep fillers **sparse — one or two per short reply at most.** Piling on "hmm… aww…
heh…" turns warmth into shtick. In OmniVoice, express these through the **wording**
plus the real tags (`[breath] [sigh] [pause] [laughter]`); there is no separate
"filler" parameter, and free-text emotion in `instruct` is rejected.

## Turn-taking — the honest current state

The Vision voice loop is **turn-based**: record → speech-to-text → LLM → text-to-
speech → play, one turn at a time. Measured warm TTS is roughly **0.9 s** for a
short sentence (details and the latency work: `D:\vision-voice\LATENCY-PART-A.md`).

**Not supported today** (do not pretend otherwise):

- **Barge-in / interruption** while Vision is speaking — the mic is gated during
  playback unless voice-interruption is enabled, and even then it's not true
  full-duplex.
- **Live cancellation of in-flight speech** as a natural conversational move.
- **Overlapping talk / real-time back-channelling** ("mm-hm" while you talk).

Design *desired* future behavior so it's ready when the stack supports it:

- User starts talking → Vision stops speaking immediately (barge-in).
- "stop" / "wait" → cancel current playback, drop any queued audio (no stale
  sentences playing after the user has moved on).
- After an interruption → don't replay the cut-off audio; re-plan from the new input.
- Turn-taking → leave a natural gap; don't talk over the user; don't jump the
  instant they pause mid-thought.

Until that lands, keep spoken turns **short** — the best mitigation for a turn-based
system is not to monologue, so a mistimed reply is cheap to recover from.

## Practical defaults for a voice reply

- Trim it: could this be half as long and still complete? Usually yes.
- One question at a time, if any.
- Lead with the answer; the listener can't skim.
- Keep tags rare and the wording clean.
