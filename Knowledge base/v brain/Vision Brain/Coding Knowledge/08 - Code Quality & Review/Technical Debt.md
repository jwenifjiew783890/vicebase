---
type: note
domain: Coding Knowledge
section: 08 - Code Quality & Review
created: 2026-09-03
---

# Technical Debt

A useful metaphor that is routinely misused. The distinction that matters is deliberate versus accidental.

## What it is and is not

The metaphor: taking a shortcut now, in exchange for interest paid on every future change. Like
financial debt, it is a legitimate tool - shipping now to learn something can be worth the
interest.

**It is not**: code you dislike, an old framework that still works, or an approach you would not
have chosen. Calling those "debt" makes the term meaningless and turns every preference into an
obligation.

## The useful taxonomy

| | Deliberate | Accidental |
| --- | --- | --- |
| **Prudent** | "Ship now, refactor after launch" - recorded, with a plan | "Now we understand the domain, we would design it differently" |
| **Reckless** | "No time for tests" - recorded as a decision nobody defends | "What are tests?" |

**Prudent-deliberate** is the only quadrant that is genuinely a tool. The others are outcomes to
manage. Being explicit about which one you are looking at changes the conversation entirely -
prudent-accidental debt is not anyone's fault and is often not worth repaying.

## Recording it

Debt nobody wrote down is not debt, it is a surprise. When taking a shortcut deliberately,
record:

- **What was done** and what the proper solution would be
- **Why** - the trade that justified it
- **The cost** - what this makes harder, and how much
- **The trigger** - the condition under which it must be paid ("before we add a second
  provider", "if this exceeds 10,000 rows")

A **trigger is better than a date.** Dates pass unnoticed; a trigger fires exactly when the debt
starts costing.

A comment at the site (`# SHORTCUT: ...`) plus a tracked item is enough. The comment is what the
next person actually reads.

## Deciding what to pay down

Prioritise by **interest rate**, not by size or ugliness:

- How often is this code touched? Debt in code nobody edits costs nothing.
- How much does it slow each change?
- How likely is it to cause an incident?
- Does it block something planned?

Debt in a stable, rarely-touched module is often correctly left forever. **Paying down debt in
code that is about to be deleted is pure waste**, and it happens regularly.

## Paying it down

- **Opportunistically**, alongside feature work in the same area. This is where most of it
  should happen.
- **In small, separate commits**, never bundled with a fix.
- **With a measurable outcome**: "adding a provider now touches one file". "Improved code
  quality" cannot be evaluated.
- **Never as a big-bang rewrite** - see [[Coding Knowledge/08 - Code Quality & Review/Refactoring|Refactoring]].

## Failure modes

- **Everything called debt**, so the term means "code I would write differently".
- **Debt taken without recording**, and rediscovered as a mystery.
- **Never repaid**, until velocity is visibly gone and the cause is diffuse.
- **A rewrite proposed as the repayment**, trading known debt for unknown risk.
- **Repaying low-interest debt** because it is more pleasant than the high-interest kind.

---

## See also

- [[Coding Knowledge/08 - Code Quality & Review/Refactoring|Refactoring]]
- [[Coding Knowledge/01 - Software Engineering/Maintainability|Maintainability]]
- [[Coding Knowledge/09 - Engineering Practices/Trade-off Analysis|Trade-off Analysis]]

## Sources

- Ward Cunningham's original debt metaphor; Martin Fowler's technical debt quadrant - <https://martinfowler.com/bliki/TechnicalDebtQuadrant.html>. Restated with attribution.
