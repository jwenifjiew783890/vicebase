---
type: note
domain: 3D & Blender Knowledge
section: 11 - Animation & Rigging
created: 2026-09-03
---

# Animation Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging|Animation & Rigging]]

## What it is

Defining values at points in time and letting the software interpolate between them. The craft is
almost entirely in **timing and spacing**, not in the keyframes themselves.

## Interpolation

| Mode | Behaviour | Use |
| --- | --- | --- |
| **Bezier** | Smooth, with editable handles | Default for organic motion |
| **Linear** | Constant rate | Mechanical motion, rotating machinery, conveyor belts |
| **Constant** | Holds, then jumps | Visibility switches, stop-motion, discrete states |

**Default Bezier eases in and out of every key.** That is right for a hand gesture and wrong for a
bouncing ball, which should hit the ground at maximum speed. Uncritical Bezier is why amateur
animation floats.

## The graph editor is where animation happens

The timeline shows *when*. The graph editor shows *how* - the curve between keys, which is the
actual motion. Animation that looks wrong but has correct key positions is nearly always a curve
problem.

Watch for:
- Unintended overshoot from Bezier handles
- Flat handles creating a pause where none was wanted
- Curves that should be linear rendered as eased

## Timing and spacing

- **Timing** - how many frames an action takes. Controls weight and scale: heavy things accelerate
  slowly.
- **Spacing** - how the movement is distributed within that time. Controls the character of the
  motion.

Even spacing reads as mechanical. Real motion accelerates and decelerates.

## Principles that transfer directly

- **Ease in / ease out** - things accelerate and decelerate, they do not start at full speed
- **Anticipation** - a movement is preceded by a small opposite movement
- **Follow-through / overlap** - not everything stops at once; trailing parts continue
- **Arcs** - natural motion follows curves, not straight lines
- **Secondary motion** - the consequences of the main motion

## Practical discipline

- **Block first** with constant interpolation - get the poses and timing right before any smoothing
- Then convert to Bezier and refine curves
- Work at final frame rate from the start
- Preview in real time; scrubbing lies about timing

## Common mistakes

- Never opening the graph editor
- Default Bezier on mechanical motion
- Even spacing throughout, giving floaty results
- Everything starting and stopping simultaneously
- Polishing detail before the timing works

## Related

[[3D & Blender Knowledge/11 - Animation & Rigging/Rigging Fundamentals|Rigging Fundamentals]]

## Sources

Blender Manual (CC-BY-SA 4.0) - keyframes, interpolation modes, the graph editor. Animation
principles are long-established craft knowledge.
