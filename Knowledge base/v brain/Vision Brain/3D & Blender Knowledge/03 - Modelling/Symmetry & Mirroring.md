---
type: note
domain: 3D & Blender Knowledge
section: 03 - Modelling
created: 2026-09-03
---

# Symmetry & Mirroring

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/03 - Modelling/00 - Modelling|Modelling]]

## What it is

Modelling one half and generating the other. Halves the work on any symmetric subject, which is
most man-made objects and most creatures.

## The three mechanisms

| Mechanism | Nature | Use |
| --- | --- | --- |
| **Mirror modifier** | Live, non-destructive | The default. Keep it live as long as possible. |
| **Symmetrize** | One-off operation on the mesh | Making an asymmetric mesh symmetric once |
| **X-axis mirror / symmetry option** | Live editing aid in Edit and Sculpt modes | Editing an already-symmetric mesh |

## Mirror modifier discipline

- The mirror is about the **object origin**, so the origin must be on the symmetry plane. If the
  mirror appears offset, the origin is wrong - not the modifier.
- **Enable clipping** to stop centre vertices crossing the plane and creating a split seam.
- Merge threshold welds the centre vertices. Too low, and a seam opens; too high, and nearby
  geometry collapses.

## When to stop mirroring

Perfect symmetry reads as artificial. Real objects are asymmetric - wear, damage, dressing, hair,
pose.

The usual sequence: **model symmetric, then apply the mirror and break symmetry deliberately in
the final pass.** Applying too early doubles the modelling work; applying too late leaves the
object looking synthetic.

For characters, break symmetry in pose and detail even when the base mesh stays symmetric.

## Common mistakes

- Origin off the symmetry plane, producing a gap or overlap that gets blamed on the modifier
- Clipping off, so centre vertices drift apart and leave a seam under subdivision
- Applying the mirror early "to see it", doubling all subsequent work
- Shipping a perfectly symmetric object and wondering why it looks computer-generated

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Modifiers|Modifiers]] ·
[[3D & Blender Knowledge/01 - 3D Fundamentals/Transforms & Coordinate Systems|Transforms & Coordinate Systems]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Mirror modifier, clipping, merge threshold, Symmetrize. Advice on
breaking symmetry is practitioner judgement.
