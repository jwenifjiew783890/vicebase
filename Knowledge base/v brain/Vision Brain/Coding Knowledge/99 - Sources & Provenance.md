---
type: note
domain: Coding Knowledge
section: root
created: 2026-09-03
---

# Sources & Provenance

Where this domain's material comes from, what licence each source carries, and the rules that keep the corpus redistributable.

## How these notes were produced

Every note is **original prose written for this vault**. No source text was scraped, pasted or
bulk-imported. What is reused is factual and methodological - how a protocol behaves, what a
flag does, what a documented practice recommends - which is not itself copyrightable. Where a
specific formulation belongs to a source, it is attributed inline and kept short.

This matters practically as well as legally: an agent reading these notes needs the operative
rule and its failure modes, not a chapter.

## Policy by licence class

Every source falls into one of three classes, and each has a different rule. **The class is
decided before writing, not after.**

| Class | Examples | What we may do |
| --- | --- | --- |
| **Permissive with attribution** (CC BY, MIT, PSF, PostgreSQL) | Google Engineering Practices, MCP spec, Twelve-Factor, Rust Book | Short attributed quotation permitted; synthesis preferred |
| **ShareAlike** (CC BY-SA) | OWASP, MDN | **Cite and synthesise only.** ShareAlike makes verbatim reuse contagious to the whole corpus, so we never copy |
| **No reuse licence** | Google SRE books, *Release It!*, Zeller, Ousterhout, Kernighan & Pike, Feathers, Kleppmann, Agans, Dekker, company postmortems | **Extract concepts, write original prose, reproduce nothing.** No text, table, figure, or characteristic list |

The third class is the one that needs a method rather than a rule, and it has one.

## Extraction method for sources with no reuse licence

Facts, methods and engineering concepts are not copyrightable; a particular expression of them
is. So the material is taken as **understanding, never as text**:

1. **Read for the concept**, then write the note without the source open. What survives that gap
   is the idea, which is what an agent needs anyway.
2. **Reproduce nothing** — not a sentence, not a table, not a figure, not a defining list in its
   original wording or order.
3. **Keep the standard vocabulary.** Technical terms of art — *error budget*, *toil*,
   *integration point*, *delta debugging* — are the industry's shared names and are used as
   names, with the source credited. Naming a concept is not reproducing a work.
4. **Attribute at the point of use**, not only in a bibliography.
5. **Separate source from synthesis explicitly** — see the convention below.
6. **Add what the source cannot**: how it applies to this stack, what was measured here, and the
   failure modes we have actually hit.
7. **Never imply endorsement.** These notes are our reading of the source, not the source's
   position.

## Labelling convention

Notes derived from a no-reuse-licence source carry a provenance callout near the top:

```markdown
> [!info] Provenance
> <Which concepts come from the source>, restated in our own words.
> <Which sections, examples, tables and failure modes> are our synthesis.
```

Then, within the note:

- **Unmarked prose** is our synthesis.
- A concept credited to the source says so where it appears.
- **"*(our synthesis)*"** marks a section that is entirely ours — usually the *Applying it here*
  section and the failure modes.
- **"*(measured)*"** or *Measured in this project* marks something observed on this machine, with
  the date in the Sources block.

Section [[Coding Knowledge/12 - Reliability Engineering/00 - Reliability Engineering|12 —
Reliability Engineering]] is the fullest worked example: almost all of its concepts come from
sources in the third class, and every note states which parts are theirs and which are ours.

## Audit

Checked 2026-09-03 across the whole domain: every quoted passage of 25 characters or more was
enumerated and inspected. The only direct quotation from a source is the phrase
*"improves the overall health of the codebase"* from Google's Engineering Practices, which is
**CC BY 3.0** and attributed at the point of use. Everything else in quotation marks is our own
phrasing, a real error message, a command, or the title of a cited paper.

## Licence positions

Verified 2026-09-03 by fetching the source.

| Source | Licence | What we do with it |
| --- | --- | --- |
| Google *Engineering Practices* - <https://google.github.io/eng-practices/> | **CC BY 3.0** (verified) | Short attributed quotation permitted; used for the review standard |
| OWASP Cheat Sheet Series - <https://cheatsheetseries.owasp.org/> | **CC BY-SA 4.0** (verified) | Cite and synthesise; ShareAlike makes verbatim reuse contagious, so we do not copy |
| Model Context Protocol spec - <https://github.com/modelcontextprotocol/modelcontextprotocol> | **MIT** (verified) | Cite freely |
| addyosmani/agent-skills - <https://github.com/addyosmani/agent-skills> | **MIT** (verified 2026-09-04) | Cite and synthesise; concepts extracted into [[Coding Knowledge/09 - Engineering Practices/Spec-Driven Development & Task Breakdown\|Spec-Driven Development & Task Breakdown]], nothing copied verbatim |
| The Twelve-Factor App - <https://github.com/twelve-factor/twelve-factor> | **CC BY 4.0** (verified; site itself (c) Salesforce) | Cite and synthesise |
| Google *SRE* books - <https://sre.google/books/> | **No reuse licence stated** | Free to read online; cite only, never reproduce |
| danluu/post-mortems - <https://github.com/danluu/post-mortems> | No licence stated | Used as an index to companies' own public postmortems; those are cited directly |
| Published incident reports (Cloudflare, GitHub, AWS, GitLab, Google) | (c) each company | Cite by URL; summarise the lesson in our own words |
| Official project documentation (Python, MDN, Rust, PostgreSQL, Docker, n8n, Open WebUI, OpenCode) | Various open licences | Cite; facts restated, text not copied |
| Books - Nygard *Release It!*, Zeller *Why Programs Fail*, Ousterhout *A Philosophy of Software Design*, Kernighan & Pike, Agans, Feathers, Kleppmann, Fowler, Humble & Farley, Dekker | (c) each publisher, **no reuse licence** | **Concepts extracted, original prose written.** No text, tables, figures or defining lists reproduced |

### Where each no-licence source was extracted

| Source | Extracted into | Nothing reproduced |
| --- | --- | --- |
| Google *SRE* / *SRE Workbook* | All of [[Coding Knowledge/12 - Reliability Engineering/00 - Reliability Engineering\|section 12]]; plus golden signals in [[Coding Knowledge/01 - Software Engineering/Observability\|Observability]] and [[Coding Knowledge/06 - DevOps & Infrastructure/Monitoring\|Monitoring]] | ✅ |
| Nygard, *Release It!* | [[Coding Knowledge/12 - Reliability Engineering/Stability Antipatterns\|Stability Antipatterns]]; stability patterns in [[Coding Knowledge/01 - Software Engineering/Design Patterns\|Design Patterns]] and [[Coding Knowledge/01 - Software Engineering/Reliability\|Reliability]] | ✅ |
| Zeller, *Why Programs Fail* | [[Coding Knowledge/07 - Debugging & Problem Solving/Systematic Debugging\|Systematic Debugging]], [[Coding Knowledge/07 - Debugging & Problem Solving/Reproducible Debugging\|Reproducible Debugging]] | ✅ |
| Agans, Kernighan & Pike | [[Coding Knowledge/02 - Debugging Method\|Debugging Method]] - our own formulation of a method these share | ✅ |
| Ousterhout, *A Philosophy of Software Design* | [[Coding Knowledge/01 - Software Engineering/Modularity & Abstraction\|Modularity & Abstraction]], [[Coding Knowledge/01 - Software Engineering/Maintainability\|Maintainability]] | ✅ |
| Feathers, *Working Effectively with Legacy Code* | [[Coding Knowledge/10 - Engineering Experience/Safe Refactoring\|Safe Refactoring]] | ✅ |
| Kleppmann, *DDIA* | [[Coding Knowledge/05 - Web & Application Engineering/Databases\|Databases]], [[Coding Knowledge/01 - Software Engineering/Scalability\|Scalability]] | ✅ |
| Fowler, *Refactoring* | [[Coding Knowledge/08 - Code Quality & Review/Refactoring\|Refactoring]] | ✅ |
| Humble & Farley, *Continuous Delivery* | [[Coding Knowledge/01 - Software Engineering/CI-CD\|CI/CD]], [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment\|Deployment]] | ✅ |
| Company postmortems (Cloudflare, AWS, GitLab, Meta) | [[Coding Knowledge/10 - Engineering Experience/Production Incident Lessons\|Production Incident Lessons]] - lessons summarised in our words, each linked to the original | ✅ |

## Evidence grades used in this domain

Notes are explicit about how strongly a claim is supported.

| Grade | Means | Example |
| --- | --- | --- |
| **Documented** | Stated in an authoritative specification or official documentation | "MCP transports are stdio and Streamable HTTP" |
| **Measured here** | Observed on this machine, with the measurement recorded | "One unbounded NVIDIA call hung for 302 s" |
| **Practitioner judgement** | Widely-held engineering experience; useful, not authoritative | "Wait for the third duplication before abstracting" |
| **Opinion** | A defensible position others reasonably reject | Style preferences |

Section 10 is largely *practitioner judgement* by construction. Section 11 is largely
*measured here*, and expires when the stack changes. Sections 01-09 mix *documented* and
*practitioner judgement*, and say which where it matters.

## Rules for future additions

1. Name the source and its licence before importing anything substantial.
2. Never paste more than a short attributed quotation, and never from a source without a
   permissive licence.
3. Prefer primary sources: the specification over a blog post about the specification.
4. When a version matters, record it. "Docker behaves like X" is worthless without a version.
5. If a claim cannot be sourced or reproduced, mark it as judgement rather than dressing it as
   fact.
6. Record the retrieval date for anything fetched from the web.

## Sources

- Licence statements fetched and verified 2026-09-03 from each URL listed above.
