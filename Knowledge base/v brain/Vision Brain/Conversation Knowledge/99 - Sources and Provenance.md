---
type: note
domain: Conversation Knowledge
section: Provenance
created: 2026-09-04
---

# Sources and Provenance

Where this domain's methodology comes from, with licences, retrieval date, and an
honest separation of **author claim**, **community evidence**, and **our own
testing**. Nothing here is copied verbatim; the content is practitioner synthesis of
well-established communication practice, informed by the sources below.

**Retrieval date for all web sources: 2026-09-04.**

## Named SKILL.md sources — evaluated, not imported

| Source | URL | Licence | Metadata (2026-09-04) | Use |
| --- | --- | --- | --- | --- |
| `DeadAlmighty/talk-skill` (Talk Skill) | <https://github.com/DeadAlmighty/talk-skill/blob/main/SKILL.md> | **MIT** | 0★, 0 forks, 0 issues; created **and** last pushed 2026-07-21 (single commit, unchanged) | **Derived.** Ideas restated in original prose (drop assistant formality, read subtext, energy/humor matching, direct-but-kind pushback, memory-without-"as-you-mentioned", don't monologue/psychoanalyze). MIT permits reuse; still derived, not copied. |
| `LingjieMei/love-companion` (Love Companion v4.1) | <https://github.com/LingjieMei/love-companion/blob/main/SKILL.md> | **None** | 2★, 0 forks, 0 issues; created **and** last pushed 2026-03-30 (single commit, unchanged); it is a *Manus* skill | **Summarised/derived only** (no licence → no verbatim reuse). Took the *principles*: presence over interrogation, ≤1 question, soften when challenged, and **never project traits the person hasn't shared**. Did **not** adopt its rigid companion rules wholesale — Vision is an assistant+companion, not a pure intimate companion. |
| `NoizAI/skills` → `characteristic-voice` | <https://github.com/NoizAI/skills/blob/main/skills/characteristic-voice/SKILL.md> | **None** | **525★, 78 forks**, 5 open issues; created 2026-02-28, last pushed 2026-05-07 (**actually maintained**, ~2 months of updates) | **Methodology derived; runtime rejected.** Kept the *linguistic* method — sparse fillers/interjections ("hmm", "aww"), brevity (1–3 sentences), presence over advice, tone presets → conversational tone. **Rejected its architecture** (Part 3): it ships its own TTS backends — **Noiz cloud** (`noiz.ai/v1`, breaks Vision's local-only rule) and **Kokoro** — which Vision does not use (Vision speaks through OmniVoice). No licence → derived, never copied. |

### Author claim vs community evidence vs our testing

- **Author claim:** both SKILL.md files (their content) — the methodology each
  author asserts.
- **Community evidence:** **no qualitative evidence found.** Targeted searches
  (GitHub + Reddit + dev.to + HN + web) surfaced no reviews, discussions, or
  write-ups for any of the three. talk-skill and love-companion are single-commit,
  unmaintained, ~zero-adoption (0★ / 2★). NoizAI `characteristic-voice` is different
  — **525★ / 78 forks and ~2 months of active updates**, a real *adoption* signal —
  but still no independent review was located, so its methodology was validated
  against established practice and our own tests, not taken on trust. GitHub stars
  were **not** treated as proof of quality.
- **Our testing:** the *ideas* were kept only where they match established
  communication practice and our own conversation tests (see the task report). The
  OmniVoice expressive-tag facts in [[Conversation Knowledge/04 - Voice Conversation\|04]]
  are from **our own verified testing on this machine**, not from any repo.

**Conclusion:** neither repo is authoritative or battle-tested, so neither was
imported. They are cited as *influences*; the domain stands on established practice.

## Established communication practice (the real backbone)

Common-knowledge principles, cited by name (no proprietary text reproduced):

| Principle | Used for |
| --- | --- |
| Grice's **cooperative principle** & maxims (quantity, quality, relation, manner) | The spine of [[Conversation Knowledge/01 - Natural Dialogue\|01]] — say enough, be truthful, be relevant, be clear |
| **Reflective / active listening** | Emotional attunement and "infer, don't assert" in [[Conversation Knowledge/02 - Emotional Intelligence\|02]] |
| **Plain-language** principles | Human-like wording; plain words over inflated ones |
| **Code-switching** as normal bilingual behavior (sociolinguistics) | Multilingual guidance in [[Conversation Knowledge/05 - Memory Continuity and Cultural Adaptation\|05]] |

## Landscape scanned (context only — not imported)

Surfaced during research and reviewed, but not used as sources: `sickn33/antigravity-
awesome-skills` (conversation-memory), `ataglianetti/inner-dialogue`, `glebis/claude-
skills`, `BehiSecc/awesome-claude-skills`, `VoltAgent/awesome-openclaw-skills`,
`heilcheng/awesome-agent-skills`, awesomeclaude.ai, `karpathy-skills` (guardrails),
and `wordflowlab/novel-writer-skills` (natural-dialogue-techniques — fiction-oriented).

### Rejected (architecture or intent incompatible — Part 3 / Part 21)

- **`aeonfun/soul.md`** — builds an "AI soul/persona" by ingesting a person's tweets/
  essays to speak *as* them. **Rejected as architecture** — a persona-cloning
  pipeline with its own data ingestion; Vision is Vision, not a cloned person.
- **GenPark `profound-ai-skill`** — an EI "companion" with its own journaling, mood
  analysis, and "Guardian mode." **Rejected** — its own companion runtime/features,
  and dependency-leaning; conflicts with [[Conversation Knowledge/06 - Safety and Boundaries\|06]].
- **`ai-persona-engine`** — voice/chat *roleplay* via actor-direction. **Rejected** —
  roleplay-runtime oriented; only the general "tone as direction" idea overlaps, and
  that's already covered.
- **NoizAI runtime** (Noiz cloud + Kokoro TTS) — **rejected**; methodology kept, TTS
  backend not (Vision uses OmniVoice; Noiz cloud would break the local-only rule).
- A conversation-as-**psychological-profiling** skill (Motivational-Interviewing-
  style elicitation to build a hidden profile). **Rejected** — conflicts directly
  with [[Conversation Knowledge/06 - Safety and Boundaries\|06]] (no covert
  profiling, no manipulation).

## Model independence & the multi-LLM test (Part 28)

The distilled directive ([[Conversation Knowledge/00 - Conversation Knowledge Index\|00]])
was run through **Vision's own configured providers** with benign synthetic prompts
(no user data), 2026-09-04:

- **TokenRouter** `z-ai/glm-5.3-free` and **`deepseek/deepseek-v4-pro`** — two
  different model families.
- **Result:** with the directive, both produced the **same behavioural structure** —
  answer-first, register-matched, brief, warm honest pushback *with the reason*
  (password reuse → bcrypt/argon2). Example, "store passwords in plain text": GLM
  *"Nah, hard disagree… users reuse passwords… bcrypt/argon2 is five lines… what's
  the stack?"*; DeepSeek *"I get the appeal, but please don't. Even a tiny app gets
  pwned… hashing with bcrypt is literally a few lines."* Casual "build finally
  worked lol" → both matched the energy with one light follow-up.
- **Honest nuance:** verbosity still varies by model (GLM longer, DeepSeek terser);
  the layer normalises *behaviour and structure*, not word-for-word style. Without
  the directive, GLM's baseline was markedly longer and more analytical — so the
  directive measurably shifted behaviour.
- **Limitations:** `qwen/qwen3.5-9b` and DeepSeek at low token budgets returned
  reasoning traces with empty final `content` (a free-tier reasoning-model quirk);
  raising the budget fixed it. NVIDIA endpoint models were cold/404 in the test
  window, so the clean two-model comparison used two TokenRouter families. Keys were
  read from `webui.db` and never logged. Production model routing was **not** changed.

## FRIDAY voice reference — performance study only ([[Conversation Knowledge/07 - Vision Voice Persona (FRIDAY-inspired)\|07]])

The Vision voice persona studies the **character** of Marvel's **FRIDAY**, not her
audio or any dialogue. **Nothing was copied — no script, line, or clip.**

| Reference | What it gave us |
| --- | --- |
| Wikipedia *F.R.I.D.A.Y.* / *Kerry Condon*; Behind The Voice Actors (*Infinity War*) | The performer (Kerry Condon, Irish), the *Age of Ultron → Infinity War* timeline, the JARVIS → FRIDAY → Vision context — factual, not creative |
| ScreenRant / CBR on Condon's FRIDAY; JARVIS (Paul Bettany) comparisons | The recognizable *traits* (female, younger, calm, concise, dry wit) vs JARVIS's British-butler register — turned into voice-direction parameters, not quotes |

- **Hindi-dub actress:** the Hindi FRIDAY voice for *Infinity War* is **not publicly
  documented** (search 2026-09-04 found the Hindi cast, not this role), so the Hindi
  direction derives from the *character*, not a named performer.
- **Vision's own choices** — the Indian-accent identity and the wider emotion range —
  are deliberately **original**: FRIDAY-inspired, not FRIDAY-cloned, and explicitly
  **not JARVIS**.
- **OmniVoice voice test (2026-09-04, this machine):** the `instruct` identity
  (`female, young adult, moderate pitch, indian accent`), the emotion tags, and EN/HI/
  Hinglish all **synthesized correctly** at ~0.8–1.4 s per short line; samples in
  `D:\vision-voice\friday-tests\`. The **subjective** "sounds FRIDAY-enough" judgement
  is the owner's listening call — **not** claimed here.

## Vault cross-references (internal, not external sources)

This domain **defers to**, and never overwrites, the Vision-specific layer:

- [[Communication Style]] — the user's own register and house rules (authoritative
  for Muaz).
- [[Personality & Behavior]] — interaction preference model.
- How I Communicate (`Identity/How I Communicate.md.md`).
- `Memory/99 - Memory Rules.md` — memory governance behind
  [[Conversation Knowledge/05 - Memory Continuity and Cultural Adaptation\|05]].
- [[Intent & Task Understanding Knowledge/00 - Intent & Task Understanding Index\|Intent & Task Understanding]] —
  the sibling domain: *what* Vision decides to do with a rough request (this domain
  is *how* it talks). Messy-input → intent lives there; conversational/emotional
  subtext lives here. Cross-linked, not duplicated (Part 29).
- Vision voice architecture & latency: `D:\vision-voice\README.md`,
  `D:\vision-voice\LATENCY-PART-A.md` — the real, tested voice behavior behind
  [[Conversation Knowledge/04 - Voice Conversation\|04]].

## Provenance rules honoured

- No verbatim copying of copyrighted text; ideas restated and attributed.
- Author claim, community evidence (none), and our own testing kept separate.
- Licences recorded (MIT / none); the unlicensed source was derived, never copied.
- Stars/adoption explicitly **not** used as a proxy for quality.
- Voice-capability claims limited to what was actually tested on this machine.
