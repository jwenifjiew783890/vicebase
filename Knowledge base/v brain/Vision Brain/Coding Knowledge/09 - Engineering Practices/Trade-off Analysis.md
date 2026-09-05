---
type: note
domain: Coding Knowledge
section: 09 - Engineering Practices
created: 2026-09-03
---

# Trade-off Analysis

Choosing deliberately between options that are all imperfect, and recording why.

## Every choice has a cost

If an option appears to have no downside, you have not found it yet. Naming the cost is the
analysis; a recommendation without one is advocacy.

The most common concealed costs: operational burden, cognitive load on future readers, a new
failure mode, an irreversible commitment, and a dependency you now maintain forever.

## The method

1. **State the decision and the constraints.** What must be true regardless of the option chosen?
2. **List real options**, including "do nothing" and "the simplest thing".
3. **Identify the two or three dimensions that actually matter here.** Not a generic list -
   the ones specific to this decision.
4. **For each option, state what it gives up.** This is the step that does the work.
5. **Weight by what matters now** - not by what might matter.
6. **Recommend one**, with the reason, and say what would change the answer.

That last clause is disproportionately valuable: "we would revisit this if write volume exceeds
X" turns a decision into something that can be re-evaluated on evidence rather than on argument.

## The recurring trade-offs

| Trade | Which side wins, usually |
| --- | --- |
| **Simple vs flexible** | Simple. Flexibility for imagined futures is usually wasted |
| **Build vs buy** | Buy for undifferentiated work; build for what makes you distinctive |
| **Now vs later** | Now, if the debt is recorded and has a trigger |
| **Fast vs correct** | Correct. A fast wrong answer has negative value |
| **Consistency vs availability** | Depends entirely on the domain - decide explicitly |
| **Coupling vs duplication** | Duplication, early. The wrong abstraction costs more |
| **Generic vs specific** | Specific, until the third real case |
| **Local reasoning vs DRY** | Local reasoning, when they conflict |

These are defaults, not rules. The value of stating them is that departing from one becomes a
conscious act requiring a reason.

## Reversibility as the tiebreak

When options are close, **pick the one that is cheaper to undo.** A reversible decision made
quickly beats an irreversible one made slowly, because you can learn from the first and cannot
from the second.

Conversely, for genuinely irreversible decisions - a data model, a shard key, a public API -
slow down and get more input. The asymmetry justifies the different pace.

## What makes an analysis honest

- **Real alternatives**, not one option plus two straw men.
- **The cost of the preferred option stated as plainly as its benefits.**
- **Uncertainty acknowledged**, with the assumptions labelled.
- **What would change the decision**, stated.
- **The decision recorded** where the next person will find it - see
  [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]].

## Failure modes

- **The false binary** - two options when there are five.
- **Deciding by novelty**, or by what is familiar, without acknowledging that is the reason.
- **Weighing on dimensions that do not matter here.**
- **Analysis paralysis** on a reversible decision - just pick one and learn.
- **Deciding fast on an irreversible one.**
- **No record**, so the same debate recurs annually with nobody able to say why.

---

## See also

- [[Coding Knowledge/09 - Engineering Practices/System Design|System Design]]
- [[Coding Knowledge/09 - Engineering Practices/ADRs|ADRs]]
- [[Coding Knowledge/01 - Engineering Principles|Engineering Principles]]
- [[Coding Knowledge/10 - Engineering Experience/Engineering Trade-offs|Engineering Trade-offs]]

## Sources

- Practitioner synthesis. The reversible/irreversible asymmetry is widely used in engineering and management practice (often framed as one-way versus two-way doors).
