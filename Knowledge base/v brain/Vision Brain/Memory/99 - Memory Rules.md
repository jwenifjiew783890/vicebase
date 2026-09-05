---
type: memory-rules
last_updated: 2026-09-03
---

# 99 — Memory Rules

Rules governing everything under `Memory/`. Read this before writing memory.

## The one rule that matters

**Do not fabricate.** Only record what is:

1. explicitly stated by the user,
2. clearly established through repeated interaction,
3. present in a trusted project file or vault note, or
4. clearly marked as an inference.

A guess never becomes a fact. When something is not known, write `UNKNOWN`
rather than filling the gap.

## Source tags

Every non-trivial claim carries a source:

| Tag | Meaning |
| --- | --- |
| `[user]` | Explicitly stated by the user, with date |
| `[vault]` | From an existing vault note, linked |
| `[verified]` | Directly observed on the machine, with date |
| `[inferred]` | Derived from behaviour — **must** carry a confidence level |

Inferences are written as:

> `[inferred — CONFIDENCE: HIGH/MEDIUM/LOW]`

## Memory types

- **Stable** — useful for months or years (communication style, principles,
  architecture). Lives in its category note.
- **Episodic** — a thing that happened at a time. Lives in
  [[Memory/15 - Important Events/Timeline|15 — Timeline]].
- **Working context** — true now, expected to go stale (current phase,
  current provider). Marked `WORKING CONTEXT` with a date.
- **Inferred** — behavioural patterns, always tagged as above.

## Conflicts

When new information contradicts old:

1. The newer explicit user statement wins.
2. The old memory is marked historical — **not deleted**.
3. Contradictions are never silently merged.
4. Anything unresolved goes in
   [[Memory/98 - Conflicts & Review Queue|98 — Conflicts & Review Queue]].

## Never store here

- passwords, API keys, tokens, authentication secrets
- anything that belongs in a credential store
- conversational filler or one-off noise
- guesses presented as facts

Credentials live in the application's own configuration store, never in this
vault.

## When to write memory

Strong signals to record something permanently: *"remember this"*, *"from now
on"*, *"I prefer"*, *"always do X"*, *"never do Y"*.

A thing said once, in passing, that looks situational is **not** a permanent
preference. Leave it out or mark it low confidence.

## Using memory

Use it silently. Prefer *"given your usual preference for…"* over *"according
to my memory…"*. Mention memory explicitly only when it explains a decision.

## Quality bar

Accuracy > quantity. Useful > voluminous. Explicit > guessed. Current >
outdated. Do not create a note for a trivial fact.

---

## Temporal memory (added 2026-09-03)

Curated category notes (01-15) are hand-written and do **not** decay. Alongside
them, Vision now captures **atomic memories** automatically: one note per fact,
marked `memory: true` in frontmatter, filed into the matching category folder.
Only those decay.

### Strength is derived, never stored-and-updated

Nothing runs on a timer. `memory_strength` is recomputed from the timestamps
every time a memory is read:

```
decay_factor   = 0.5 ^ (days_since_reinforced / effective_half_life)
effective_half_life = base_half_life          (from retention_class)
                    x (1 + 0.5 x reinforcements)
                    x (0.5 + importance)
memory_strength = importance x decay_factor      <- ranks retrieval
lifecycle       = bands on decay_factor          <- fresh/active/fading/weak/archived
```

Strength ranks retrieval; the lifecycle band is measured on time-decay alone,
so a low-importance memory is not born already "fading".

### Retention classes

| Class | Base half-life | Reaches archived (importance 0.5) |
| --- | --- | --- |
| `permanent` | never decays | never |
| `long_term` | 730 d | ~2233 d |
| `episodic` | 180 d | ~551 d |
| `temporary` | 14 d | ~43 d |
| `ephemeral` | 2 d | ~7 d |

### Rules that still apply

- **Fading is not deleting.** A weak memory is moved to `Memory/Archive/` and
  remains findable when explicitly asked for.
- **Reinforcement beats duplication.** Mentioning something again resets its
  clock and lengthens its half-life; it never creates a second note.
- **Corrections keep history.** A superseding statement is appended under a
  `### Correction` heading and flags `needs_review: true`; the old wording stays.
- **Permanent deletion is only ever explicit.** Automatic maintenance archives,
  it never deletes.
- Credentials still never enter this vault. See the "Never store here" rule above.

To override any of this by hand: edit the note's frontmatter. `retention_class:
permanent` freezes it, `importance` scales its lifespan, and deleting the
`memory: true` line removes it from the temporal system entirely while leaving
the note in place.
