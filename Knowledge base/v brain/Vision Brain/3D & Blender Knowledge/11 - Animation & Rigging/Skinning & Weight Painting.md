---
type: note
domain: 3D & Blender Knowledge
section: 11 - Animation & Rigging
created: 2026-09-03
---

# Skinning & Weight Painting

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging|Animation & Rigging]]

## What it is

Binding a mesh to an armature so bones deform it, and adjusting the per-vertex influence until the
deformation is correct.

Extends [[3D & Blender Knowledge/11 - Animation & Rigging/Rigging Fundamentals|Rigging Fundamentals]],
which covers armatures and IK/FK; this note is the deformation layer specifically.

## What weights are

Each vertex carries a weight per bone - how strongly that bone moves it. Weights should normally
**sum to 1** across bones for a vertex; unnormalised weights produce vertices that shrink or
explode when posed.

## Automatic weights are a starting point

Automatic weighting is a reasonable first pass and is never the finished result. It fails
predictably at:

- **joints** - elbows, knees, shoulders, hips
- **regions where two limbs are close** - a hand near a hip picks up hip influence
- **armpits and crotch**, where surfaces nearly touch
- anywhere geometry is close in space but far apart on the body

## Working method

1. **Pose to the extreme first.** Weighting looks fine at rest; problems only appear at the limits
   of motion. Set up test poses and keep them.
2. Work **bone by bone**, isolating the influence being edited.
3. Use **smooth** heavily - abrupt weight transitions produce creasing
4. Check the **falloff across a joint**: influence should transition gradually over several loops,
   not switch abruptly at one edge
5. **Mirror weights** for symmetric characters rather than painting twice - this requires correct
   `.L`/`.R` naming

## Diagnosing bad deformation

| Symptom | Cause |
| --- | --- |
| Surface collapses at a joint | Too few edge loops, or weights transition too abruptly |
| Vertices shoot away when posed | Unnormalised weights, or stray influence from a distant bone |
| A patch does not move | Zero weight - unassigned vertices |
| Candy-wrapper twist at a limb | Insufficient loops plus poor twist distribution |
| Geometry near another limb drags with it | Bleed from automatic weighting |

**Topology first.** No weighting fixes a joint with no edge loops - see
[[3D & Blender Knowledge/01 - 3D Fundamentals/Topology|Topology]].

## Beyond basic skinning

- **Corrective shape keys** driven by bone rotation, for the deformation that weighting cannot fix
- **Helper bones** that move automatically to preserve volume at joints
- Blender's **Bendy Bones**, which curve rather than staying rigid, giving smoother deformation
  from fewer bones

## Common mistakes

- Accepting automatic weights without testing extreme poses
- Painting at rest pose only
- Vertices left unassigned
- Abrupt weight transitions producing creases
- Painting both sides instead of mirroring
- Fighting weights when the real problem is topology

## Related

[[3D & Blender Knowledge/11 - Animation & Rigging/Rigging Fundamentals|Rigging Fundamentals]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Shape Keys & Drivers|Shape Keys & Drivers]]

## Sources

Blender Manual (CC-BY-SA 4.0) - vertex groups, weight paint mode, automatic weighting, bendy bones,
weight mirroring. Diagnostic table is practitioner synthesis.
