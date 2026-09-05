---
type: policy
scope: Islamic Knowledge
created: 2026-09-03
status: authoritative
---

# 99 — Source & Authenticity Rules

Governs everything under `Islamic Knowledge/`. Read before adding material.

> [!danger] The absolute rule
> **Nothing in this library may be invented.** Not a hadith, not a grading, not
> a scholar's words, not a reference, not a book title, not an audio title, not
> a URL. Where something is not known, the note says `UNKNOWN` or
> `NEEDS VERIFICATION`. An honest gap is always better than a plausible
> fabrication — in this subject a fabricated narration or misattributed grading
> can change how someone worships.

## Scope and separation

This is a **knowledge library**, not personal memory. It is deliberately
separate from `Memory/`, which holds facts about the user and is subject to
decay. Nothing here decays; nothing here carries `memory: true`.

Framework requested by the user: **Ahl al-Hadith / Salaf al-Salih / Salafi
manhaj**. The library is organised accordingly. That is an organising
principle, not a licence to mislabel — a source is always recorded as what it
actually is.

---

## 1. Source hierarchy

**Priority 1 — Primary sources.**
Qur'an: canonical Arabic text from a recognised authority.
Hadith: original Arabic, collection, book, chapter, number, and established
scholarly grading with the grader named.

**Priority 2 — Official scholar sources.**
The scholar's own foundation or authorised repository, e.g. `binbaz.org.sa`,
`binothaimeen.net`. Preferred over any third-party reproduction.

**Priority 3 — Reputable digital libraries.**
Only when Priority 1–2 are unavailable. The exact source URL is always
recorded.

A note must never present Priority 3 material as though it were Priority 1.

---

## 2. Category labelling

Every substantive note declares what kind of material it is:

`Qur'an` · `Hadith` · `Tafsir` · `Aqidah` · `Fiqh` · `Usul` · `Fatawa` ·
`Scholarly commentary` · `Biography` · `History` · `Contemporary lecture` ·
`Secondary analysis`

Rules that follow from this:

- Qur'anic text is never paraphrased and then labelled Qur'an.
- Qur'an text, translation, tafsir and commentary are stored as **separate,
  clearly-labelled things**, never merged.
- A scholar's own words are never blended with a later commentator's.
- Modern explanation of a classical text is labelled as modern explanation.

---

## 3. Hadith grading

The library distinguishes: **Sahih · Hasan · Da'if · Mawdu' · disputed ·
grading unavailable**.

### Where gradings come from

Gradings are recorded **only** as they appear in the source dataset, attributed
to the named grader. No grading is ever assigned by this library itself.

### Disagreement is preserved, never resolved

When graders differ, **all** gradings are stored side by side with the grader
named. The library does not pick a winner, and does not convert scholarly
disagreement into false certainty.

> Example actually present in this corpus (Sunan Abi Dawud 1):
> Al-Albani — *Hasan Sahih*; Muhammad Muhyi al-Din Abdul Hamid — *Hasan Sahih*;
> Shu'ayb al-Arna'ut — *Sahih Lighairihi*; Zubair Ali Zai — *Isnaad Hasan*.

### Sahih al-Bukhari and Sahih Muslim carry no per-hadith grading here

This is deliberate and must not be "fixed" by adding gradings.

The imported dataset contains **no external grading field** for these two
collections. The scholarly reason is that both compilers wrote to their own
stated conditions of authenticity, and the ummah has broadly received these two
collections as such — so per-hadith external grading is not how these
collections are normally annotated. Where a specific narration in them has been
discussed by later scholars, that discussion belongs in a **separate,
sourced note** — not silently stamped onto the hadith.

**Do not infer.** An empty grading field means *no grading was supplied by the
source*, and the note says exactly that.

### Al-Albani attributions

A grading is attributed to Shaykh al-Albani **only** where the source data
attributes it to him by name. The library never infers his opinion, never
generalises from one ruling to another, and never attaches his name to a
collection he did not grade.

---

## 4. Attribution

For scholarly material the actual author is preserved. Nothing is flattened
into "Qur'an" or "Hadith". A statement attributed to a scholar requires the
work, and where available the volume, page, recording and timestamp.

If attribution cannot be evidenced, the statement is **not added**.

---

## 5. Copyright and lawful use

Verified positions for the sources used in this library:

| Source | Status | What this library may do |
| --- | --- | --- |
| Tanzil Qur'an text | CC BY 3.0 | Redistribute **verbatim**, with attribution and a link to tanzil.net |
| `fawazahmed0/quran-api` | Public domain (Unlicense) | Free use |
| `fawazahmed0/hadith-api` | Public domain (Unlicense) | Free use |
| **sunnah.com** | **Scraping and mass reproduction prohibited** | **Link only.** Individual hadith may be cited for study; whole books/collections may not be copied |

Standing rules:

- Copyrighted audio is **not** downloaded merely because it is reachable.
  Prefer official downloads, explicitly authorised downloads, public-domain
  material, or an official streaming URL. Otherwise store **metadata plus the
  source link**.
- Copyrighted books are not copied from unauthorised sources. Where a full text
  is not lawfully distributable, store metadata, source link, table of contents
  if lawfully available, and notes — not the book.
- Sites are not scraped aggressively. Respect `robots.txt`, rate limits, terms
  of service.

---

## 6. Translations

Translations are always labelled as translations and **always name the
translator**. A translation is never presented as the Qur'an itself or as the
Arabic of a hadith.

Where original Arabic exists it is preserved alongside. Arabic is never
replaced by a paraphrase.

---

## 7. Uncertainty

| Marker | Meaning |
| --- | --- |
| `UNKNOWN` | The field genuinely has no known value |
| `NEEDS VERIFICATION` | Present but unconfirmed against a Priority 1–2 source |
| `grading unavailable` | The source supplied no grading — **not** an implied grading |

A note carrying `NEEDS VERIFICATION` must not be cited as settled.

---

## 8. Required frontmatter

Every substantive knowledge note carries:

```yaml
source:            # human-readable source name
original_url:      # exact URL
author:            # actual author/compiler
date:              # of the work, if known
collection:
edition:
language:
license_status:
retrieved_at:
```

Hadith notes add: `book`, `chapter`, `hadith_number`, `grading`,
`grading_scholar`.

Scholar-statement notes add: `scholar`, `work`, `volume`, `page`, `recording`,
`timestamp`.

---

## 9. Answering from this library

When Vision answers from this corpus it must cite the **exact source note**,
state the grading **with the grader's name**, and surface disagreement where it
exists. It must not present a da'if narration as established, nor secondary
analysis as primary text.

If the library does not contain something, the correct answer is that it does
not — not a reconstruction from memory.

---

## 10. This library is not a substitute for scholars

It is a study and reference aid. It does not issue rulings. Questions of
practice go to qualified scholars; this corpus points to what they actually
said, with the source attached.

---

# Part II — Acquisition & Retrieval Policy

*Added 2026-09-03. Permanent. Governs how Vision acquires new Islamic material and how it
answers Islamic questions.*

## 11. The framework is a filter, not a rubber stamp

Material is organised according to the user's requested **Ahl al-Hadith / Salaf al-Salih /
Salafi manhaj** framework.

> [!danger] "Salafi" on the label proves nothing
> A source is **not** acceptable merely because it carries that label, and not rejected merely
> because it does not. Every candidate is evaluated on: authenticity · attribution ·
> provenance · scholarly source · chain or reference where relevant · publication and edition ·
> grading · date · primary vs secondary · whether it is an authorised copy · licence and
> copyright · actual relevance.

Source material is never fabricated and never silently altered.

## 12. Source priority for acquisition

| Level | Source | Notes |
| ---: | --- | --- |
| **1** | Qur'an and established primary hadith collections | Highest authority |
| **2** | Primary works of recognised scholars within the framework | The scholar's own text |
| **3** | Official scholar sites, foundations, authorised recordings and publications | e.g. binbaz.org.sa |
| **4** | Reputable secondary sources | **Only** when Levels 1–3 are unavailable |

When sources disagree, the disagreement is **stored with each position attributed**. Positions
are never silently merged, and no position is quietly dropped.

## 13. Acquiring a book

1. Search reliable sources · 2. identify author and work · 3. verify edition and source ·
4. verify it can lawfully be acquired · 5. prefer authorised, public-domain or licensed copies ·
6. preserve original source metadata · 7. file it in the correct folder ·
8. check for duplicates first · 9. cross-link into the relevant topic and scholar indexes ·
10. record provenance and licence status.

If the full text is copyrighted and cannot lawfully be copied: **store metadata, the source
link, and how to access it legitimately.** Nothing is scraped or reproduced merely because it
is reachable.

## 14. Acquiring a lecture or bayan

Verify scholar attribution, source, recording title, date where available, and that the origin
is official or authorised. Store a transcript **only** where lawfully permitted; otherwise
metadata and a source link.

> **Never invent a lecture, a transcript, a title, or a scholar's statement.**

## 15. Acquiring hadith

Always preserve: collection · book · chapter · hadith number · Arabic · translation (if
authorised) · grading · grading scholar · source · URL · chain/reference information.

> [!warning] Presence in a collection is not a grading
> Never call a narration "authentic" merely because it appears in a collection. Where scholars
> differ on a grading, **both positions are preserved** with each grader named.

## 16. Retrieval rule for Islamic questions — Obsidian is not optional

When a question is substantially Islamic — fiqh, aqidah, hadith, Qur'an, fatwa, or "what does
Islam say about…" — Vision **must consult this corpus before formulating an answer.**

```
Islamic question
   → classify as Islamic
   → retrieve from Islamic Knowledge/
   → analyse the retrieved evidence
   → answer, citing the notes used
```

**Not**: answer from general model memory, then perhaps check Obsidian afterwards. The model's
pretrained knowledge must never silently override or replace this curated corpus.

Retrieval order (a hierarchy of preference, not a claim that every question resolves at one level):

**Qur'an → hadith → established scholarly works → fatwas → lectures/bayans → contextual analysis**

## 17. Fact-specific questions

For a real-life situation, do **not** produce a generic ruling. Extract the actual
circumstances first, then retrieve evidence against those circumstances, then analyse.

```
evidence → principles → circumstances → analysis
```

not

```
question → memorised generic ruling
```

Identify which circumstances would change the answer.

## 18. No false certainty — label every claim

Every substantive statement in an Islamic answer must be identifiable as one of:

| Label | Meaning |
| --- | --- |
| **A — Explicit textual evidence** | A verse or narration that directly addresses the matter |
| **B — Established scholarly ruling** | A named scholar's actual ruling, with its source |
| **C — Scholarly explanation** | A scholar explaining a text, with its source |
| **D — Application of principles** | Reasoning from evidence to the case — **inference, not fatwa** |
| **E — Area of disagreement** | Scholars genuinely differ; all positions named |
| **F — Not established by this corpus** | The corpus does not answer this |

An inference (D) is never presented as a fatwa (B). "Islam definitely says X" is only
permissible where the evidence and scholarly source actually support that certainty.

## 19. When the corpus is insufficient

This is the rule most likely to be violated under pressure to sound complete.

> [!danger] Do not fill a gap from general model memory and present it as corpus material.

Instead: **state the gap explicitly.** Then, if the user asks for research or acquisition,
search authorised sources per §12–15, verify, add or link the source, and only then answer from
verified material.

Where external research is used, clearly separate: **existing corpus · newly acquired source ·
external research · scholarly inference · model reasoning.**

## 20. Personal preference is not evidence

`Memory/` holds the user's beliefs, preferences and methodology. `Islamic Knowledge/` holds
religious sources.

The user following a given methodology tells Vision **how to organise and prioritise sources**.
It does **not** make the user's preference into evidence for a ruling. The two are never merged.

## 21. Traceability is mandatory

Vision must never confuse *"I know something about this"* with *"I found a verified source for
this."*

Every Islamic answer cites what it used: Qur'an surah:verse · hadith collection/book/number/
grading/grader · scholar work with volume and page or recording · fatwa with scholar, source
and URL.

**RETRIEVE → VERIFY → ATTRIBUTE → ANALYSE → CITE.**

---

## 22. Known model failure: unverified "verbatim" Arabic — and the mechanism that now catches it

*Recorded 2026-09-03 from actual tests, then partly corrected on the same day when the claims
here were re-checked mechanically. Both the failure and the correction are kept, because a
record that quietly drops its own errors is worth nothing.*

### What actually happened

Asked to quote Sahih Muslim 3258 "exactly as it appears in the note", the model produced:

> حَدَّثَنَا يَحْيَى بْنُ يَحْيَى، قَالَ قَرَأْتُ عَلَى مَالِكٍ … إِلاَّ مَعَهَا ذِي مَحْرَمٍ

The note actually contains:

> حَدَّثَنَا زُهَيْرُ بْنُ حَرْبٍ، وَمُحَمَّدُ بْنُ الْمُثَنَّى … إِلاَّ وَمَعَهَا ذُو مَحْرَمٍ

**A different isnad and a changed matn ending, presented as a quotation.** The collection,
number, book and grading line were all correct; only the Arabic was wrong. Mechanical checking
later established two further facts about it: the isnad the model gave is *genuine* — it is the
chain of **Sahih Muslim 1477** — and the matn ending it gave matches **Sahih al-Bukhari 1087**.
So the model did not invent Arabic out of nothing; it **blended two real narrations and filed
the result under a third reference**. That is not less serious, but it is a different fault
from invention, and naming it correctly matters.

### A claim previously recorded here that was WRONG

This section used to state that the model "cited Qur'an 24:60 with Arabic that is not in the
Qur'an". **That was a mistake in the audit, not a fault in the model.** The text it gave was
24:60 in **Imlaei** orthography:

> وَالْقَوَاعِدُ مِنَ النِّسَاءِ اللَّاتِي لَا يَرْجُونَ نِكَاحًا …

while this corpus stores the Qur'an in **Uthmani** script:

> وَٱلۡقَوَٰعِدُ مِنَ ٱلنِّسَآءِ ٱلَّٰتِي لَا يَرۡجُونَ نِكَاحࣰا …

The two differ in dagger alif and similar conventions. A naive byte comparison called it a
fabrication; it is the same verse. **Do not treat an orthographic difference as a fabrication** —
that is a false accusation against a correct quotation, and it is exactly the kind of unverified
claim the rest of this document forbids.

### What now checks this, instead of asking the model to be careful

Prompt instructions did not fix the underlying behaviour and were not going to. Two mechanisms
now do:

1. **`Vision Islamic Sources` tool** — `quran_ayah`, `hadith_get`, `fatwa_get`,
   `quran_search`, `hadith_search`, `fatwa_search`, `corpus_status`, and
   `verify_quotation`. Every function returns the corpus text verbatim, so the model can copy
   rather than recall. `verify_quotation(text, expected_source=...)` checks a quotation against
   the record it is being attributed to and answers **VERIFIED**, **RESPELLED** (same passage,
   other orthography), **ALTERED** (real passage, changed wording), **SOURCE MISMATCH** (real
   text, wrong reference) or **NOT IN CORPUS**.
2. **An automatic citation audit on every reply.** After Vision answers an Islamic question,
   every Qur'an reference, hadith reference, fatwa number and Arabic quotation in the reply is
   checked against the source index, and the findings are appended to the message. The audit is
   produced by the index, not by the model that wrote the answer, so it holds whether or not the
   model used the tools.

### What the audit actually catches, measured

Tested against planted defects, the audit reports correctly on all of:

| Planted defect | Reported as |
| --- | --- |
| A verse that does not exist (24:99) | "Qur'an 24:99 does not exist. Surah 24 has 64 verses." |
| A hadith number that does not exist | "not in this corpus - the reference could not be confirmed" |
| A fatwa number that does not exist | "not in this corpus" |
| **A real passage under the wrong reference** | "Quotation attributed to X is not its text (only n% of it appears there)" |
| A real passage with a word changed | "does not match the corpus wording (n% agreement)" |
| A real passage with the joining words changed | "altered at its edges - the corpus does contain ..." |
| Wholly invented Arabic | "NOT FOUND in the corpus" |
| The same verse in another orthography | *nothing* - correctly, this is not an error |
| "there is scholarly consensus" | "the corpus records individual scholars, not consensus" |
| A scholar the corpus does not hold, cited as support | "this is model memory, not corpus evidence. Label it (F)" |
| The same scholar named in order to exclude him | *nothing* - correctly, this is the right behaviour |
| A grading given without naming the grader | names the graders the corpus records, and whether they disagree |

### The limitation that remains

**Long Arabic passages degrade even when the exact text was retrieved.** Asked for
Qur'an 24:31 - a long verse - the model returned text at 91% agreement, having written
*أبناء بعولتهن* ("the **sons** of their husbands") where the verse reads
*ءاباء بعولتهن* ("the **fathers** of their husbands"), and dropped *أو أبنائهن*
altogether. It had the correct text in front of it from `quran_ayah`.

This is not fixed. It is now **detected**: the audit flagged it. Short quotations
(a matn, a fatwa sentence) come through verbatim; long ones drift. Treat a flagged
quotation as wrong and open the note.

### What this means in practice

| Element | Trustworthy? |
| --- | --- |
| Collection, hadith number, book | **Yes** — verified accurate in testing |
| Which note the material came from | **Yes** |
| Grading line, quoted as written | **Yes** |
| Fatwa numbers and titles | **Yes** — 6/6 correct across two tests |
| **Arabic presented as a quotation** | Only when the citation audit confirms it |

### Rule

**Arabic that Vision presents as a quotation counts as a quotation only if the citation audit
below the answer confirms it.** Where the audit flags a quotation, believe the audit. Vision has
always been reliable for *finding* and *naming* the right source; reproducing it is now checked
mechanically rather than trusted.

A related earlier failure: a **failed Arabic search is not evidence of absence** — the corpus
Arabic is fully diacritised, so undiacritised queries silently miss. Vision once declared "no
hadith exists" on women travelling without a mahram while Sahih al-Bukhari 1086 and Sahih
Muslim 3258 both carried it. The search tools now fold diacritics automatically, so an
undiacritised query matches; the
[[Islamic Knowledge/02 - Hadith/05 - Hadith Search Index/00 - Hadith Keyword Index|Hadith Keyword Index]]
remains available as a browsable cross-check.
