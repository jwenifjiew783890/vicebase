---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Systematic Debugging

Turning debugging from guesswork into a search. The technique is bisection; the discipline is writing the hypothesis down.

## Debugging is a search problem

There is a set of possible causes. Each observation eliminates part of it. Good debugging
maximises **elimination per unit of effort**; bad debugging picks a favourite theory and tests
it repeatedly.

That framing gives the two rules that matter:

1. **Choose the observation that halves the space**, not the one that confirms your theory.
2. **Test the cheapest discriminating observation first**, not the most likely cause. A
   five-second check that eliminates a third of the space beats a twenty-minute investigation
   of the most probable single cause.

## The hypothesis discipline

Before each action, write - literally write - two things:

- **Hypothesis**: "the config is not being read from the file I think it is"
- **Prediction**: "then printing the resolved path will show a different directory"

Then act, and record the outcome. This does three things: it prevents the aimless-change spiral,
it makes the eliminated space explicit, and it means you can hand the investigation to someone
else, or resume it tomorrow, without starting over.

**Change one thing at a time.** Two simultaneous changes make the result unattributable in both
directions - you cannot learn from success either.

## Bisection, along whichever axis is cheapest

| Axis | Method | Best when |
| --- | --- | --- |
| **Time** | `git bisect` between known-good and known-bad | It used to work |
| **Space** | Check the value at the pipeline midpoint | Data is wrong somewhere |
| **Configuration** | Disable components until it stops failing | Many moving parts |
| **Data** | Shrink the input until it stops failing | Input-dependent |
| **Environment** | Compare a working and a failing machine | "Works on mine" |

`git bisect run <script>` automates the time axis completely. It converts a day of archaeology
into minutes, and it is the highest-return debugging tool most people under-use.

**Delta debugging** on the data axis - repeatedly halving the input while it still fails -
produces a minimal reproduction, which usually makes the cause obvious.

## Instrumenting

Printing values is not primitive; it is often the fastest route. Make it useful:

- Print **the actual value and its type**, not just that you reached a line.
- Print at **boundaries** - what went into the function, what came out.
- Include an identifier so lines can be correlated under concurrency.
- Use `repr`-style output so whitespace, `None` and empty strings are visible. `""` and
  `"   "` look identical otherwise, and that distinction is frequently the bug.

Use a debugger when you need to inspect a rich state or step through control flow. Use logging
when the failure is rare, concurrent, or in production - a debugger cannot attach to something
that already happened.

## When stuck

- **Re-read the error.** All of it. Most "I have no information" situations have the answer in
  the part that was skimmed.
- **Verify the assumption you have not checked** - usually that the code you are reading is the
  code that ran.
- **Explain it out loud**, in full sentences. A large fraction of bugs resolve during the
  explanation, before the listener responds.
- **Look at what changed** even if it "cannot be related".
- **Reduce.** Cut everything until a minimal case remains.
- **Stop.** If three hypotheses in a row failed, the model is wrong, not the guesses. Go and
  gather description rather than generating more theories.

## Anti-patterns

| Anti-pattern | Cost |
| --- | --- |
| Changing code to see what happens | Destroys evidence, adds variables |
| Testing the same theory repeatedly | No elimination |
| Starting from the fix | You will find a way to justify it |
| Ignoring the "impossible" | The impossible thing is often the bug |
| Debugging the wrong environment | Hours, and no signal |
| Stopping at "it works now" | It will come back, unexplained |

---

## See also

- [[Coding Knowledge/02 - Debugging Method|Debugging Method]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Root Cause Analysis|Root Cause Analysis]]
- [[Coding Knowledge/07 - Debugging & Problem Solving/Reproducible Debugging|Reproducible Debugging]]

## Sources

- Andreas Zeller, *Why Programs Fail* (2nd ed., 2009) - delta debugging and the scientific method framing; cited, not reproduced. Kernighan & Pike, *The Practice of Programming* (1999) - cited, not reproduced. `git bisect` documentation - <https://git-scm.com/docs/git-bisect>.
