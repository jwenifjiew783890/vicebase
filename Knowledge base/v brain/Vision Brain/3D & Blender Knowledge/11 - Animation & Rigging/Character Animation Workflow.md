---
type: note
domain: 3D & Blender Knowledge
section: 11 - Animation & Rigging
created: 2026-09-03
---

# Character Animation Workflow

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging|Animation & Rigging]]

## What it is

Making a rigged character act. Distinct from
[[3D & Blender Knowledge/11 - Animation & Rigging/Animation Fundamentals|Animation Fundamentals]],
which covers keyframes and curves - this is the process of building a performance.

## Blocking first, always

The professional sequence, and the one that separates workable animation from an unfixable mess:

1. **Blocking** - key poses only, on **constant interpolation** so nothing interpolates. Judge
   pose and timing with no smoothing to hide behind.
2. **Breakdowns** - the poses between key poses that define *how* it moves from one to the next.
   This is where the character of the motion is decided.
3. **Splining** - convert to interpolated curves
4. **Polish** - curve refinement, overlap, follow-through, settle

**Do not skip blocking.** Animating in splined mode from the start produces motion that is
smooth, floaty and structurally wrong, and fixing it means starting again.

## Poses carry the performance

- **Silhouette test** - a pose should read as a black shape. If the action is unclear in
  silhouette, it is unclear.
- **Line of action** - one clear curve through the body
- **Avoid symmetry and twinning** - identical left and right reads as dead
- **Weight** - where is the character's mass, and what is supporting it

## Timing and spacing

Covered generally in Animation Fundamentals; for characters specifically:

- **Heavier characters accelerate more slowly** and take longer to stop
- **Anticipation before action** scales with effort
- **Overlap** - hips lead, chest follows, head follows, extremities last. Everything arriving
  simultaneously reads as mechanical.
- **Moving holds** - a character holding a pose is never completely still

## Practical tools

- **Pose libraries** for reusable poses
- **Onion skinning / motion paths** to see the arc of motion
- **Ghosting** neighbouring frames
- **Actions** as reusable animation blocks, combined in the NLA editor for cycles and layering
- Animate on **twos** where appropriate - not every frame needs a key

## Walk and run cycles

The standard exercise, and the standard interview test:

- Contact, down, passing, up - the four core poses
- Hips move in a figure of eight, not straight
- Arms oppose legs
- Head remains relatively stable - it is what the viewer watches
- Test the cycle **in place**, then apply forward motion

## Common mistakes

- Splining from the start
- Poses that do not read in silhouette
- Everything moving on the same frames
- No anticipation or follow-through
- Perfect symmetry
- Polishing before the timing works
- Animating without reference - film yourself

## Related

[[3D & Blender Knowledge/11 - Animation & Rigging/Animation Fundamentals|Animation Fundamentals]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Facial Animation & Lip Sync|Facial Animation & Lip Sync]]

## Sources

Blender Manual (CC-BY-SA 4.0) - actions, NLA editor, pose library, motion paths, onion skinning.
Blocking-to-polish workflow and pose craft are long-established animation practice.
