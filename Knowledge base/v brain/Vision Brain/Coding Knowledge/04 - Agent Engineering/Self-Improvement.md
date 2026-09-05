---
type: note
domain: Coding Knowledge
section: 04 - Agent Engineering
created: 2026-09-03
---

# Self-Improvement

Systems that change their own behaviour over time, and the safeguards that make that survivable.

## What can actually improve, ranked by safety

1. **Knowledge** - adding notes, standards and corrections to a store the agent reads. Safe,
   inspectable, reversible, and by far the highest value per unit of risk.
2. **Skills / procedures** - recording a working sequence so it can be reused. Safe if skills
   are data and are reviewed before use.
3. **Examples** - accumulating good input/output pairs for few-shot use. Safe, bounded, needs
   curation.
4. **Prompts** - adjusting instructions based on observed failures. Riskier; a prompt change can
   regress everything, so it must be gated on an evaluation set.
5. **Tools** - writing new tools. Dangerous. Every new tool is new capability and new attack
   surface.
6. **Its own permissions or code** - a system that can widen its own boundary has no boundary.
   Do not build this.

**The rule: improvement should flow into data the agent reads, not into the code the agent
runs.** That keeps every change inspectable, diffable and revertible.

## What a change must have

- **Provenance.** What triggered it, when, from which run.
- **A reason.** Not just "user corrected me" but what the correction implies.
- **Review before it takes effect**, at least for anything beyond adding a note.
- **A revert path**, and preferably version control.
- **Evaluation.** Nothing that alters behaviour ships without running the evaluation set - see
  [[Coding Knowledge/04 - Agent Engineering/Evaluation Loops|Evaluation Loops]].

## The correction pipeline

The valuable loop is simple and mostly manual:

```
failure observed -> what would have prevented it? -> write it as a durable note
                 -> add the case to the evaluation set -> verify it now passes
```

This is how a knowledge corpus earns its keep. Each real failure becomes a permanent note and a
permanent test. Note that the improvement is a **document**, not a code change - which is why it
is safe.

## Failure modes

- **Drift.** Small self-modifications compound into behaviour nobody chose. Version everything
  and periodically diff against a known-good baseline.
- **Learning from bad outcomes.** A user who did not complain is not a user who was satisfied.
  Weak signals become bad training.
- **Reinforcing its own mistakes.** An agent recording its own unverified conclusions as facts
  builds a corpus of confident errors. Only record what was **verified**.
- **Unbounded growth** of the memory or skill store until retrieval quality collapses. Prune.
- **No rollback**, so a bad change cannot be undone.
- **Optimising the measurable proxy** rather than the goal.

> [!warning] The boundary that must not move
> A self-improving system must never be able to change **what it is permitted to do**. Knowledge,
> skills and examples may grow; permissions, sandboxes and allowlists are changed by a human,
> reviewed, and version-controlled. A system that can grant itself capability has no security
> model at all.

## Status in this stack

An agent layer capable of self-improvement is an **approved requirement with a written
specification, and no implementation**. Two mature candidates were evaluated by running them,
not by reading their marketing:

- **HKUDS/OpenSpace** — its `CAPTURED`/`DERIVED` learning runs only inside `execute_task`, so it
  can only learn from work *it* executes; and it pays ~70 s of cold start on every process
  start. Both disqualify it here.
- **NousResearch/hermes-agent** — its learning loop needs the full Hermes AIAgent runtime
  (`curator.py` forks an agent; `learn_prompt.py` returns a prompt, not an engine). Its
  *patterns* are reusable; its loop is not extractable.

The lesson generalises: **the valuable part of a self-improving system is the discipline, not
the engine.** Lifecycle states, archive-never-delete, write-origin provenance and static
scanning are a few hundred lines of policy. The engine is a prompt to a model you already run.

The mechanism Vision will use is specified in
[[Agents/Self-Improvement Specification|Self-Improvement Specification]].

---

## See also

- [[Coding Knowledge/04 - Agent Engineering/Skill Systems|Skill Systems]]
- [[Coding Knowledge/04 - Agent Engineering/Evaluation Loops|Evaluation Loops]]
- [[Coding Knowledge/04 - Agent Engineering/Permissions|Permissions]]
- [[Coding Knowledge/03 - AI Engineering/Agent Memory|Agent Memory]]

## Sources

- Practitioner synthesis. The status statement reflects this project as of 2026-09-03:
  requirement approved and specified, nothing built. Candidate findings come from running
  OpenSpace and reading the Hermes source directly, both MIT.
