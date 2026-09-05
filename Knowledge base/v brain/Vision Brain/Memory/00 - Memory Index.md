---
type: index
last_memory_audit: 2026-09-03
last_updated: 2026-09-03
---

# 00 — Memory Index

Vision's long-term memory about its user. Structured, sourced, and honest
about what it does not know.

**Rules first:** [[Memory/99 - Memory Rules|99 — Memory Rules]] — no
fabrication, every claim carries a source, `UNKNOWN` beats a guess.

---

## Categories

| # | Note | Holds | State |
| --- | --- | --- | --- |
| 01 | [[Memory/01 - User Profile/User Profile\|User Profile]] | Canonical who-they-are and working style | Populated |
| 02 | [[Memory/02 - Communication Style/Communication Style\|Communication Style]] | How to talk to them — **read this one** | Populated |
| 03 | [[Memory/03 - Personality & Behavior/Personality & Behavior\|Personality & Behavior]] | Interaction preference model | Populated |
| 04 | [[Memory/04 - Preferences/Preferences\|Preferences]] | Technical, product, engineering | Populated |
| 05 | [[Memory/05 - Personal Life/Personal Life\|Personal Life]] | Routines, milestones, personal context | **Empty by design** |
| 06 | [[Memory/06 - Relationships & People/People\|People]] | Important people | **Empty by design** |
| 07 | [[Memory/07 - Travel & Experiences/Travel & Experiences\|Travel & Experiences]] | Trips and experiences | **Empty by design** |
| 08 | [[Memory/08 - Business/Business Context\|Business Context]] | Business direction | Sparse |
| 09 | [[Memory/09 - Projects/Vision\|Vision]] | The active project — canonical | Populated |
| 09 | [[Memory/09 - Projects/Vision - Abandoned Electron Build\|Vision (Electron)]] | Abandoned build, kept for its reasoning | Historical |
| 10 | [[Memory/10 - Technical Environment/Technical Environment\|Technical Environment]] | Machine, services, provider | Populated (working context) |
| 11 | [[Memory/11 - AI & Model Preferences/AI & Model Preferences\|AI & Model Preferences]] | Model strategy, observed behaviour | Populated |
| 12 | [[Memory/12 - Interests & Hobbies/Interests & Hobbies\|Interests & Hobbies]] | Interests, with confidence split | Populated (mixed confidence) |
| 13 | [[Memory/13 - Goals & Plans/Goals & Plans\|Goals & Plans]] | Long-term direction | Populated |
| 14 | [[Memory/14 - Decisions & Principles/Decision Log\|Decision Log]] | Architectural decisions + reasons | Populated |
| 15 | [[Memory/15 - Important Events/Timeline\|Timeline]] | Episodic — what happened when | Populated |
| 16 | [[Memory/16 - Captured Memories/README\|Captured Memories]] | Auto-captured atomic memories that did not fit a category | Populated on use |
| -- | [[Memory/Archive/README\|Archive]] | Decayed or explicitly forgotten memories, still searchable | Populated on use |
| 98 | [[Memory/98 - Conflicts & Review Queue\|Conflicts & Review Queue]] | Contradictions and open questions | **7 open items** |
| 99 | [[Memory/99 - Memory Rules\|Memory Rules]] | How this system works | Populated |

---

## The three things that matter most

1. **Open WebUI *is* Vision** — not Vision plus Open WebUI. The old Electron
   build is abandoned. → [[Memory/09 - Projects/Vision|09]]
2. **Talk straight.** Casual is fine, hedging and corporate register are not,
   and never claim something works untested. →
   [[Memory/02 - Communication Style/Communication Style|02]]
3. **Specialised software does specialised jobs.** Obsidian and n8n stay
   external; Vision unifies the experience. →
   [[Memory/14 - Decisions & Principles/Decision Log|14]]

---

## Audit

| | |
| --- | --- |
| Last memory audit | **2026-09-03** |
| Last updated | **2026-09-03** |
| Overall confidence | **High** for project, technical, communication and preferences. **Low/none** for personal life, people, travel, business specifics. |
| Sources used | Existing vault notes · user's memory-initialisation brief (2026-09-03) · direct machine verification (2026-09-03) |
| Sources **not** available | No chat history export was supplied |

### Missing information

- All personal life, relationships and travel — nothing established
- Business specifics — direction only, no names/metrics/whether a business exists
- Why the Electron build was abandoned — inferred, unconfirmed (C-02)
- Timeline or priority for remaining Phase 2 integrations
- Demographics of any kind — deliberately not inferred

### Temporal memory

Since 2026-09-03 Vision also captures **atomic memories** automatically - one note
per fact, marked `memory: true`, which age and can be archived. The curated notes
01-15 above are hand-written and never decay. The decay policy, retention classes
and manual-override instructions are in
[[Memory/99 - Memory Rules|99 - Memory Rules]].

### Islamic Knowledge is a separate domain

Religious sources live in [[Islamic Knowledge/00 - Index|Islamic Knowledge]], **not here**, and
are governed by their own
[[Islamic Knowledge/99 - Source & Authenticity Rules|Source & Authenticity Rules]] — including
a permanent acquisition and retrieval policy.

The separation is deliberate: a memory such as *"the user follows Ahl al-Hadith methodology"*
tells Vision **how to prioritise sources**. It is **not itself evidence for a ruling**. See
§20 of those rules.

### Relationship to the rest of the vault

`Memory/` is the **canonical current** layer. The older folders — `Identity/`,
`Memories/`, `Preferences/`, `Projects/`, `Decisions/`, `Agents/`,
`Integrations/` — are kept intact as source material and are linked from here
rather than copied. Where they contradict `Memory/`, `Memory/` wins and the
contradiction is logged in
[[Memory/98 - Conflicts & Review Queue|98]].

Nothing in the pre-existing vault was modified, moved or deleted.
