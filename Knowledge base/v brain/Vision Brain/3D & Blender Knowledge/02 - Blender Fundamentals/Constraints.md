---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Constraints

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

A constraint creates a relationship evaluated every frame, rather than baking a result. Copy
Location, Track To, Child Of, Limit Rotation, Follow Path and the rest.

## Constraints versus parenting

Parenting is a hard hierarchical relationship. Constraints are selective and stackable:

- **Parent** when the child should simply inherit the parent's transform entirely
- **Constrain** when you want only part of the relationship - position but not rotation, or
  rotation limited to one axis, or influence blended over time

Constraints have an **influence** value, which parenting does not. That alone decides many cases.

## The ones worth knowing

| Constraint | Use |
| --- | --- |
| Copy Location / Rotation / Scale | Selective inheritance, per axis |
| Track To / Damped Track | Point something at something else - cameras, eyes, turrets |
| Child Of | Parenting that can be animated on and off - picking up an object |
| Limit Location / Rotation / Scale | Mechanical limits - a hinge that cannot over-rotate |
| Follow Path | Motion along a curve |
| Shrinkwrap | Stick to a surface |

## Evaluation order

Constraints evaluate top to bottom in their own stack, after parenting. A Copy Location above a
Limit Location behaves differently from the reverse. When a rig does something inexplicable,
check constraint order before suspecting the armature.

## Common mistakes

- Using parenting where influence blending was needed, then keyframing awkward workarounds
- Constraint loops - A tracks B while B tracks A - producing jitter or nothing
- Forgetting that constraints do not change the underlying transform values, so the N panel shows
  numbers that do not match what you see
- Leaving constraints on exported objects, where the target may not exist

## Related

[[3D & Blender Knowledge/11 - Animation & Rigging/Rigging Fundamentals|Rigging Fundamentals]]

## Sources

Blender Manual (CC-BY-SA 4.0) - constraint types and evaluation. Selection guidance is
practitioner judgement.
