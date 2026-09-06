# The instructions this project was built under

## Provenance warning — read this first

**This file is a RECONSTRUCTION, not a transcript.** The original briefs
were given in a chat session that is not part of this repository. What
follows is a summary of the five successive instructions as the developing
agent understood and acted on them, written after the fact.

Where a phrase is quoted, it is a phrase the agent acted on directly and
that is reflected verbatim in the committed reports (for example the
32-point completion bar, which exists in the repository as §32 of the final
report). Do not treat any sentence here as certified verbatim user text.

The **verifiable** record of what was asked for is structural, and it is in
the repository:

- §32 of the final report — the 32-point completion bar, item by item
- §33 of the final report — the original 22 R&D questions, scored honestly
- §0 of the final report — the evidence-labelling rules the briefs imposed
- §16 of the final report — where the agent disagreed with the brief

Those four sections are primary evidence. This file is context.

---

## Brief 1 — R&D evaluation

Evaluate the feasibility of a small local LLM **specialised for
conversation rather than knowledge**, across 22 sub-questions.

The instruction that shaped everything after it: *challenge my assumptions;
be technically honest; don't oversell the idea.*

**Deliverable:** `reports/03-RD-EVALUATION-conversational-llm.md`.

**The answer was partly "no".** The central premise — that you can trade
knowledge away to buy conversational capacity — was rejected with reasons.
That trade does not exist; knowledge is the substrate pragmatic
understanding runs on. See §0 of that report.

## Brief 2 — personal AI refinement

Extend the evaluation to continuous learning, four-tier memory
(T0 working / T1 episodic / T2 semantic / T3 procedural), and tool/agent
orchestration. Explicitly: *challenge whether this is "a small
conversational LLM" or "a personal AI system built around a small
conversational LLM."*

**Deliverable:** `reports/04-DESIGN-personal-ai-architecture.md`.

**The answer rejected both framings.** Neither "a conversational LLM" nor
"a system built around one" is right; the accurate description is a
deterministic personal-agent runtime in which a small LLM is the language
interface and the component trusted *least*. That reframing is the
architectural decision the entire codebase implements.

## Brief 3 — autonomous engineering mandate

Build it. Target hardware **RTX 4050 Laptop (6 GB VRAM), 16 GB RAM,
Core i7**. Languages **English + Hindi + Hinglish**, with Hindi as natural
spoken Hindi rather than textbook Hindi.

Explicitly: *do not ask technical questions — you are the technical
engineer.* Every design decision in this repository was therefore made by
the agent, not delegated back.

## Brief 4 — mandatory conversational testing

Actually run the model. Preserve transcripts. Run an autonomous repair
loop. **Label every claim** with one of:

> **MEASURED** · **RESEARCHED** · **SIMULATED** · **NOT ACTUALLY TESTED**

That labelling requirement is why the reports read the way they do, and why
§10, §11 and §15 spend more space on what was *not* established than on
what was.

## Brief 5 — final autonomous objective

The most demanding instruction, and the one that produced most of what is
in this handoff:

1. A **32-point completion bar** (now §32 of the final report)
2. **30 mandatory conversation questions**
3. *"NO FALSE GREEN TESTS — if a test passes because the failure path was
   never triggered: MARK IT AS INVALID"*
4. Invent **independent adversarial tests**
5. Every repair must trigger **retesting and regression**
6. *"DO NOT TELL ME THAT THE SYSTEM SHOULD WORK. PROVE THAT IT WORKS."*
7. One comprehensive final report

### Item 3 is the reason this project has a mutation audit

"A test that passes because the failure path was never triggered" is
exactly what a mutation audit detects: disable a defence, and if no test
fails, that test never depended on the defence. The audit
(`eval/mutation_audit.py`, 88 mutations) exists specifically to satisfy
this instruction, and it repeatedly caught real false greens — including
three occasions where two defences each satisfied the other's only test
(F18, F40, F44).

### Item 6 is the reason claims are labelled and evidence is committed

The raw output of the mutation audit, all 110 transcripts, and the fresh
test-suite output are committed rather than summarised, so that every
number can be checked against the run that produced it.

---

## Standing constraints (from the operating environment, not the user)

- Development on branch `claude/conversational-llm-architecture-a13xti`
- No pull request unless explicitly requested
- GitHub access scoped to this repository only
