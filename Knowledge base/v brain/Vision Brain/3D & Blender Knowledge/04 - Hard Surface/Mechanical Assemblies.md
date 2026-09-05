---
type: note
domain: 3D & Blender Knowledge
section: 04 - Hard Surface
created: 2026-09-03
---

# Mechanical Assemblies

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface|Hard Surface]]

## What it is

Objects made of multiple parts that fit together, and often move relative to each other -
hinges, pistons, linkages, fasteners, panels.

## Model as parts, not as one mesh

Real assemblies are separate components. Modelling them as one merged mesh causes:

- impossible-looking intersections where parts should meet with a gap
- no ability to animate movement
- materials that cannot differ per part
- topology far more complex than any single part needs

**Keep parts separate objects.** It is simpler, not harder.

## Tolerances and gaps

Parts that touch with zero gap read as fused. Real assemblies have clearance:

- a visible gap of a millimetre or two between adjacent panels
- a slight recess where a part seats into another
- fasteners that stand proud, or sit in a countersink

Zero-gap contact also produces z-fighting in the render, which looks like a bug and is actually a
modelling decision.

## Origins for movement

Anything that rotates needs its origin at the axis of rotation - hinge pin, axle, pivot bolt. Set
this while modelling, not when animating. See
[[3D & Blender Knowledge/01 - 3D Fundamentals/Transforms & Coordinate Systems|Transforms]].

## Reuse

Fasteners, brackets and standard parts repeat. Model once, then instance - linked duplicates,
collection instances or geometry-node scatter. A model with 200 individually modelled identical
bolts is 200 times the memory and 200 times the edit cost.

## Construction logic

Ask how the object would actually be made:

- sheet metal is folded, so it has uniform thickness and rounded bends
- cast parts have draft angles and generous fillets
- machined parts have flat faces and sharp small radii
- welded parts have beads at the joins

Matching the process makes the object believable in a way detail alone cannot.

## Common mistakes

- One merged mesh for an assembly
- Parts intersecting with no clearance, producing z-fighting
- Origins left at world centre, so nothing can rotate correctly
- Identical parts modelled repeatedly instead of instanced
- Fillets and thicknesses that contradict the implied manufacturing process

## Related

[[3D & Blender Knowledge/04 - Hard Surface/Panel Lines & Surface Detail|Panel Lines & Surface Detail]] ·
[[3D & Blender Knowledge/03 - Modelling/Precision Modelling|Precision Modelling]]

## Sources

Practitioner synthesis, informed by standard manufacturing practice.
