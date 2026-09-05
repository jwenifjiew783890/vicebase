---
type: note
domain: Coding Knowledge
section: 03 - AI Engineering
created: 2026-09-03
---

# Hallucination Reduction

Reducing confident invention. It cannot be eliminated, so the system must also detect it.

## Why it happens

The model predicts plausible continuations. A fabricated citation, a non-existent function and a
real one are all *plausible*; nothing in the mechanism distinguishes them. Calibration is weak,
so the model's confidence does not reliably track its correctness.

The three practical implications:

1. **Parametric knowledge is the risk surface.** Anything answered from training rather than
   from provided context is unverified.
2. **Specific details are the most dangerous output** - version numbers, API signatures, quotes,
   URLs, statistics, dates - because they are precise, checkable, and rarely checked.
3. **The fix is architectural, not linguistic.** "Don't hallucinate" in a prompt achieves very
   little.

## What actually works, in order of effect

**1. Ground it.** Provide the source material and instruct the model to answer only from it.
This is the single largest reduction available. See [[Coding Knowledge/03 - AI Engineering/RAG|RAG]].

**2. Require citations per claim.** Not a bibliography at the end - an attribution attached to
each assertion. Then **verify programmatically** that each cited source exists and contains
supporting text. An unverified citation is itself a common hallucination.

**3. Make "I don't know" a first-class, rewarded output.** Say explicitly that the correct
answer, when the material is insufficient, is to say so. Provide a place to put it: an `unknown`
enum value, a `confidence` field, a `missing_information` section. Without an escape hatch, the
model must produce *something*.

**4. Verify externally.** Compile the code. Run the test. Check the URL resolves. Query the
database. This converts a probabilistic claim into a deterministic fact, and it is the
difference between an assistant and a system.

**5. Constrain the output space.** Enums, schemas and closed sets remove the room to invent.

**6. Decompose.** Long multi-part answers drift. Several narrow questions each grounded in
retrieved material outperform one broad one.

**7. Lower the temperature** for factual work. Modest effect, but free.

**8. Ask for reasoning first, conclusion second.** Generated left to right, a conclusion stated
first will be defended rather than derived.

## Detection, because prevention is incomplete

- **Verify every reference**: does the file exist, does the function exist in the installed
  version, does the URL resolve, does the quoted text appear in the cited source?
- **Self-consistency**: sample the same question several times; disagreement across samples is a
  strong signal of invention.
- **Faithfulness check**: a second pass asking "is every claim in this answer supported by this
  source material?" catches a useful share of unsupported statements.
- **Watch for over-specificity.** A suspiciously precise number with no citation is a red flag.

## In coding work specifically

The dominant failure is a **plausible API that does not exist** - a function, flag, config key,
or parameter that fits the naming conventions perfectly and is not there, often because it
existed in a different major version.

Defences that work:
- Read the actual source or the installed package before calling into it.
- Check the version in use, and check the changelog when behaviour is surprising.
- Compile, type-check, and run - a real check beats any amount of confidence.
- **Report what was verified and what was not.** An honest "I did not run this" is worth more
  than a confident claim, because it tells the reader where to look.

---

## See also

- [[Coding Knowledge/03 - AI Engineering/RAG|RAG]]
- [[Coding Knowledge/03 - AI Engineering/Evaluation|Evaluation]]
- [[Coding Knowledge/03 - AI Engineering/Structured Outputs|Structured Outputs]]
- [[Coding Knowledge/10 - Engineering Experience/Approaches That Commonly Fail|Approaches That Commonly Fail]]

## Sources

- Ji et al., "Survey of Hallucination in Natural Language Generation" (2022) - <https://arxiv.org/abs/2202.03629>; Wang et al., "Self-Consistency" (2022) - <https://arxiv.org/abs/2203.11171>. Coding-specific observations are from this project.
