---
type: note
domain: 3D & Blender Knowledge
section: 11 - Animation & Rigging
created: 2026-09-03
---

# Rigging Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging|Animation & Rigging]]

## What it is

Building the control structure that deforms a mesh. A rig is a **user interface for a model** -
judge it by whether an animator can work with it quickly.

## Armatures and weights

Bones deform vertices according to **weights** - how much each bone influences each vertex.
Automatic weights are a starting point, never the finish. Problem areas are always joints,
armpits, shoulders and anywhere two influences meet.

Weight painting is the bulk of rigging work. The test is simple: **pose the joint to its extreme
and look for collapse, spiking or geometry passing through itself.**

## Topology comes first

A mesh with no edge loops at a joint cannot deform cleanly regardless of weights. Rigging cannot
repair modelling. See
[[3D & Blender Knowledge/01 - 3D Fundamentals/Topology|Topology]] - the loops must exist before the
rig does.

## IK versus FK

| | Forward Kinematics | Inverse Kinematics |
| --- | --- | --- |
| How | Rotate each bone in the chain | Position the end, solver computes the chain |
| Good for | Arcs, free motion, arms gesturing | Contact - feet on ground, hands on a surface |
| Awkward for | Keeping a hand planted | Smooth arcing motion |

Legs are usually IK, because feet must stay planted. Arms are frequently switchable, because both
are needed. **Offering both, switchable, is the mark of a usable rig.**

IK needs a **pole target** to control the direction the joint bends, or the elbow or knee flips
unpredictably.

## Rig usability

- **Controls, not bones.** Animators should select clearly shaped custom controls, never deform
  bones directly.
- **Layers or collections** to hide the mechanism
- **Limits** on joints that should not hyperextend
- **Naming with .L and .R suffixes**, which enables symmetry and mirrored pasting
- **Reset to rest pose** must be trivial

## Common mistakes

- Rigging a mesh with no loops at the joints
- Accepting automatic weights without testing extremes
- IK with no pole target, giving flipping joints
- Exposing the whole armature instead of clean controls
- No .L/.R naming, losing all mirroring
- Not testing extreme poses until animation has started

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Constraints|Constraints]] ·
[[3D & Blender Knowledge/01 - 3D Fundamentals/Topology|Topology]]

## Sources

Blender Manual (CC-BY-SA 4.0) - armatures, weight painting, IK constraints, bone collections.
Usability guidance is practitioner judgement.
