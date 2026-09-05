---
type: note
domain: 3D & Blender Knowledge
section: 01 - 3D Fundamentals
created: 2026-09-03
---

# Mesh Anatomy

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals|3D Fundamentals]]

## What it is

A polygon mesh is **vertices** (points), **edges** (pairs of vertices) and **faces** (closed loops
of edges). Everything else is derived from those three.

- **Tri** - three vertices, always planar. What the GPU actually renders.
- **Quad** - four vertices. The working unit of modelling, because it subdivides and loops cleanly.
- **N-gon** - five or more. Convenient, and unpredictable under subdivision.

## Manifold geometry

A mesh is **manifold** if it could exist as a real surface: every edge shared by exactly two faces,
no self-intersection, no vertices joining otherwise separate parts.

Non-manifold geometry breaks:

- normal calculation - "outside" is undefined on an open surface
- booleans
- solidify
- 3D printing, since a slicer cannot fill an open volume

Blender finds it: Edit Mode > Select > All by Trait > Non Manifold.

## The recurring defects

| Defect | What it is | Why it matters |
| --- | --- | --- |
| Doubles | Two vertices in the same place, unmerged | Split shading, visible seams, failed booleans |
| Interior faces | Faces inside the volume | Render artefacts, broken booleans, wasted geometry |
| Zero-area faces | Degenerate geometry | Undefined normals, export errors |
| Loose geometry | Vertices or edges belonging to no face | Invisible, but exported and counted |
| Flipped faces | Normal pointing inward | Shading that reads as a material bug |

**Merge by Distance** removes doubles, and should be a reflex after any boolean, mirror-apply or
import.

## When n-gons are acceptable

On a **flat, static, non-subdivided** surface. A ten-sided face on the flat back of a panel that
never deforms is fine, and arguing otherwise is dogma.

They are not acceptable on curved surfaces, inside subdivision cages, or anywhere that deforms.

## Common mistakes

- Treating "no n-gons" as an absolute rule and spending hours on invisible flat faces
- Not merging doubles after a mirror or boolean
- Shipping loose geometry that inflates counts and confuses receiving applications

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Topology|Topology]] ·
[[3D & Blender Knowledge/01 - 3D Fundamentals/Normals & Shading|Normals & Shading]]

## Sources

Blender Manual (CC-BY-SA 4.0) for mesh structure and the non-manifold selection tools. The
position on when n-gons are acceptable is practitioner judgement.
