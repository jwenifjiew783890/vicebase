---
type: note
domain: 3D & Blender Knowledge
section: 01 - 3D Fundamentals
created: 2026-09-03
---

# Normals & Shading

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals|3D Fundamentals]]

## What it is

A **normal** is the direction a surface faces. It determines how light interacts with the surface -
so normals control shading, and wrong normals look like wrong materials.

- **Face normal** - one direction per face
- **Vertex normal** - averaged from adjacent faces; what smooth shading interpolates
- **Custom split normals** - manually authored vertex normals, used to fake smooth shading on
  low-poly geometry

## Smooth versus flat

Flat shading uses the face normal, so every face reads as distinct. Smooth shading interpolates
vertex normals, making faceted geometry appear curved.

Smooth shading adds no geometry. A smooth-shaded cube still has eight vertices; it merely looks
wrong. The silhouette always reveals the true polygon count.

**Smooth by angle** applies smooth shading only where the angle between faces is below a
threshold, keeping genuinely sharp edges sharp. This is usually the correct default for
hard-surface work.

## Diagnosing flipped normals

Overlays > **Face Orientation**. Blue is outward, **red is inward**. This is the fastest
diagnostic in Blender and it is badly under-used.

Fix: Edit Mode, select all, Recalculate Outside.

**If recalculation produces nonsense, the mesh is non-manifold.** Blender cannot determine
"outside" for a surface that is not closed. Fix the topology first, then recalculate.

## Why normals get blamed on materials

The symptom - patchy dark shading, a surface that looks dirty or inside-out - appears in the
render. So the search starts in the shader editor, and the cause is in the mesh. Check Face
Orientation before touching a single shader node.

## Custom split normals

Powerful and dangerous. They let a low-poly game asset shade as though it were smooth, and they
override everything else. They also silently defeat later normal-affecting operations and survive
operations you might expect to reset them.

If shading is inexplicable and Face Orientation looks correct, check whether custom split normals
exist - clearing them is often the fix.

## Common mistakes

- Debugging shading in the shader editor when the cause is a flipped face
- Recalculating normals on non-manifold geometry and trusting the result
- Applying smooth shading to a hard-surface object with no angle threshold, smearing the edges
- Forgetting custom split normals exist, then fighting them for an hour

## Related

[[3D & Blender Knowledge/04 - Hard Surface/Weighted Normals & Bevel Discipline|Weighted Normals & Bevel Discipline]] ·
[[3D & Blender Knowledge/04 - Debugging Method (3D)|Debugging Method]]

## Sources

Blender Manual (CC-BY-SA 4.0) for normals, shading modes and the Face Orientation overlay.
Diagnostic ordering is practitioner judgement.
