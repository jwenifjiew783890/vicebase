---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Modifiers

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

A modifier is a non-destructive operation applied to geometry at evaluation time. The stack is
evaluated **top to bottom**, and the original mesh is never changed until you apply.

## Order changes the result

Not a subtlety - usually the whole problem.

| Order | Result |
| --- | --- |
| Mirror then Subdivision | Halves join smoothly across the seam. Correct. |
| Subdivision then Mirror | Each half smoothed separately, then duplicated - visible seam |
| Bevel then Subdivision | Bevel makes the sharp edge, subdivision smooths the rest. Correct for hard surface. |
| Subdivision then Bevel | Bevels an already dense mesh. Usually wrong, always heavy. |
| Array then Curve | Copies follow the curve. Correct. |
| Curve then Array | The deformed object is duplicated straight. Rarely wanted. |

**General rule: generate geometry, then smooth, then deform.**

## The modifiers that earn their place

| Modifier | Use |
| --- | --- |
| Mirror | Symmetric modelling. Clipping keeps centre vertices welded. |
| Subdivision Surface | Smooth organic and curved forms |
| Bevel | Edge treatment - the single most important hard-surface modifier |
| Solidify | Thickness from a surface. Walls, panels, cloth. |
| Array | Repetition, optionally along a curve |
| Boolean | Cutting and combining volumes |
| Weighted Normal | Fixes shading on bevelled hard-surface meshes |
| Geometry Nodes | Anything procedural |
| Shrinkwrap | Conforming one surface to another - retopology, decals, terrain |

## Viewport versus render levels

Subdivision carries separate viewport and render levels. A model set to 1 in viewport and 3 in
render is the standard cause of "it was fine until I rendered" - both for appearance and for
render time.

Check this before diagnosing a slow render.

## When to apply

Applying is one-way. Do it only when:

- exporting to a format that will not carry the modifier
- sculpting on the result
- the stack is slower to evaluate than the frozen geometry is to work with
- a later operation genuinely requires real geometry

Otherwise keep it live. A live stack is a decision you can revise.

## Common mistakes

- Wrong order, then blaming the modifier
- Applying early to "see it properly"
- Forgetting render levels are different from viewport levels
- Boolean before the mesh is manifold

## Related

[[3D & Blender Knowledge/04 - Hard Surface/Weighted Normals & Bevel Discipline|Weighted Normals & Bevel Discipline]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Broken Modifiers|Broken Modifiers]]

## Sources

Blender Manual (CC-BY-SA 4.0) - modifier stack evaluation and individual modifiers. The ordering
table records the consequences of that documented evaluation order.
