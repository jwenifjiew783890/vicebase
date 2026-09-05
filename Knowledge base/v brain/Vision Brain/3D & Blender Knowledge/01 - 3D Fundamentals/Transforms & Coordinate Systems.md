---
type: note
domain: 3D & Blender Knowledge
section: 01 - 3D Fundamentals
created: 2026-09-03
---

# Transforms & Coordinate Systems

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals|3D Fundamentals]]

## What it is

Every object carries a transform - **location, rotation, scale** - expressed relative to a parent
or to the world. The mesh data underneath is separate and usually unchanged by it.

Blender is **Z-up, right-handed**. Most game engines and several other packages are Y-up. This one
difference causes most "the model imported lying on its side" problems.

## Why it matters

The object transform and the mesh are different data. Almost everything downstream - modifiers,
physics, export, UV projection - reads the mesh. A transform that has not been applied is
therefore invisible to you and highly visible to them.

## Spaces

| Space | Meaning | Used for |
| --- | --- | --- |
| Global | World axes | Placing objects in a scene |
| Local | The object's own axes | Moving along an object's length after it has been rotated |
| Normal | Aligned to the selected face or edge normal | Extruding perpendicular to a surface |
| Parent | Relative to a parent object | Hierarchies, rigs, assemblies |

Choosing the wrong space is why a transform "goes the wrong way".

## Pivots and origins

The **origin** is the point an object rotates and scales about. It is arbitrary until you set it.

- A door needs its origin at the hinge, or it cannot swing.
- A wheel needs its origin at the axle.
- A modular wall piece should have its origin at a corner, on the grid, so pieces snap together.

Setting origins deliberately is one of the cheapest quality steps available.

## Gimbal lock

Euler rotations (X, Y, Z angles) can reach an orientation where two axes align and a degree of
freedom is lost. It appears as an axis that suddenly does nothing, or an animation that flips.
Quaternions avoid it, at the cost of being harder to key by hand. For animated rotation through
arbitrary orientations, prefer quaternion.

## Common mistakes

- Scaling in Object Mode and never applying, so bevels and physics misbehave later
- Assuming Z-up on export to an engine that expects Y-up
- Leaving origins wherever the object happened to be created
- Transforming in Global when the operation is only meaningful in Local or Normal space

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Scale & Units|Scale & Units]] ·
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]]

## Sources

Blender Manual (docs.blender.org/manual, CC-BY-SA 4.0) for transform spaces and orientation
conventions. Origin and gimbal guidance is practitioner judgement.
