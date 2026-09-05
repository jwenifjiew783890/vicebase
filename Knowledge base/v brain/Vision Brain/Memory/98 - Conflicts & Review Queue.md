---
type: maintenance
category: conflicts
last_updated: 2026-09-03
---

# 98 — Conflicts & Review Queue

Open items needing the user's confirmation, and contradictions recorded rather
than silently resolved. Per
[[Memory/99 - Memory Rules|99 — Memory Rules]], nothing here has been deleted
or merged away.

---

## C-01 — Vault notes describe the abandoned Electron build as current

**Severity: high — this is the biggest accuracy problem in the vault.**

These notes are written in the present tense about an architecture that no
longer exists:

| Note | What it still claims |
| --- | --- |
| [Vision Technical Stack](Projects/Vision/Vision%20Technical%20Stack.md.md) | Electron/React/TS/Vite/Zustand is the stack |
| [Vision Current Status](Projects/Vision/Vision%20Current%20Status.md.md) | "Steps 1–6 complete, next step: Vision Orb" |
| [Vision Roadmap](Projects/Vision/Vision%20Roadmap.md.md) | Phase 1 Electron foundation ✅, Phase 2 Orb |
| [Vision Development Timeline](Projects/Vision/Vision%20Development%20Timeline.md.md) | Electron-based throughout |
| [[Important Memories]] | "Completed foundation: Electron, IPC, 3D Orb" |
| [Things Vision Should Remember](Memories/Things%20Vision%20Should%20Remember.md.md) | final section, same |
| [Active Context](Memories/Active%20Context.md.md) | "Obsidian is being prepared… will eventually connect" |

**Resolution applied:** current truth recorded in
[[Memory/09 - Projects/Vision|09 — Vision]]; history preserved in
[[Memory/09 - Projects/Vision - Abandoned Electron Build|the historical note]].
Originals left untouched.

**Needs your decision:** should these legacy notes be moved to an `Archive/`
folder or given a "HISTORICAL" banner? I did not modify them unasked.

---

## C-02 — Why was the Electron build abandoned?

The vault records **no reason**. The inference — that Open WebUI already
provided what was being rebuilt, matching the user's own "reuse mature
infrastructure" principle — is marked
`[inferred — CONFIDENCE: MEDIUM]`.

**Needs confirmation.** A one-line answer would turn a guess into a fact and
belongs in [[Memory/14 - Decisions & Principles/Decision Log|DEC-2026-09-02-A]].

---

## C-03 — Obsidian status changed today

Multiple notes say Obsidian *"is being prepared"* / *"will eventually connect"*
/ *"is not yet connected to Vision"*. As of 2026-09-03 it **is** connected.

**Resolution applied:** current state in
[[Memory/09 - Projects/Vision|09 — Vision]] and
[[Memory/15 - Important Events/Timeline|15 — Timeline]]. Legacy wording left
in place as historical.

---

## C-04 — Twelve notes have a doubled `.md.md` extension

Files such as `Vision Architecture.md.md`, `How I Think.md.md`,
`Lessons Learned.md.md`. Consequence: Obsidian treats the basename as
`Vision Architecture.md`, so a normal `[Vision Architecture](Projects/Vision/Vision%20Architecture.md.md)` link **does not
resolve to them** — several are effectively orphaned from
[[Vision Brain|the hub note]].

**Not fixed** — renaming touches your files and could break existing links.
Say the word and I will rename them and repair the links.

---

## C-05 — Empty notes

`Knowledge/AI Knowledge.md`, `Knowledge/Programming Knowledge.md`,
`Knowledge/Tools & Infrastructure.md`, `Identity/User Profile.md.md`,
`Previous Projects.md` are all 0 bytes.

`Previous Projects.md` is linked from the hub but empty — the real content is
in [[Architecture Lessons]].

---

## C-06 — No chat history export was supplied

The brief anticipated a chat export as a supplementary source. **None was
provided.** Everything here comes from existing vault notes, the
memory-initialisation brief itself, and direct machine verification.

Categories left deliberately empty as a result:
[[Memory/05 - Personal Life/Personal Life|05 — Personal Life]],
[[Memory/06 - Relationships & People/People|06 — People]],
[[Memory/07 - Travel & Experiences/Travel & Experiences|07 — Travel]].

If you supply an export, these are the categories that would gain the most.

---

## C-07 — Low-confidence interests

Gaming, GTA and Discord/community building rest on a single mention in the
brief. Recorded, but flagged `CONFIDENCE: LOW` as *current active hobbies* in
[[Memory/12 - Interests & Hobbies/Interests & Hobbies|12 — Interests]].
