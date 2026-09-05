---
type: stable
category: preferences
last_verified: 2026-09-03
confidence: high
---

# 04 — Preferences

Stable preferences. Consolidates [[User Preferences]], [Product Preferences](Preferences/Product%20Preferences.md.md)
and [Development Preferences](Preferences/Development%20Preferences.md.md) with the user's 2026-09-03 statement; those
legacy notes remain valid and are not superseded.

## Technical

- Reuse mature software; avoid duplicate systems.
- Modular architecture — specialised external systems stay **external**.
- Minimal customisation of upstream code where possible.
- **Test real behaviour instead of assuming.**
- Local-first where practical.
- Support both local and cloud/API models.
- Preserve future scalability.

`[user 2026-09-03]` `[vault]`

## Product

Vision should feel: **premium, minimal, futuristic, professional,
desktop-first, polished**, with a strong visual identity.

It must **not** feel like:

- an Ollama wrapper
- an admin or developer dashboard
- a collection of unrelated tools
- a VS Code clone

`[user 2026-09-03]` `[vault]` — see [Product Preferences](Preferences/Product%20Preferences.md.md) for the fuller
treatment (chat/code experience, motion, accessibility, performance).

## Engineering process

```
inspect first
→ reuse before rebuilding
→ implement the minimum necessary code
→ test
→ fix real problems
→ stop when complete
```

`[user 2026-09-03]`

Note the final step: **stop when complete.** Do not continue expanding scope
past the finished task.

## Debugging

Root-cause diagnosis over speculative fixes: reproduce → isolate → identify
cause → fix cause → test fix → test regressions. `[vault]` ([How I Work](Identity/How%20I%20Work.md.md))

## Scope control

Future ideas are recorded, not implemented early. A later-phase feature must
not destabilise the current phase. `[vault]` ([Lessons Learned](Memories/Lessons%20Learned.md.md) #8)
