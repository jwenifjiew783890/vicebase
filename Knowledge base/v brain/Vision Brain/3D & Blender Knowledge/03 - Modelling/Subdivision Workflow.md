---
type: note
domain: 3D & Blender Knowledge
section: 03 - Modelling
created: 2026-09-03
---

# Subdivision Workflow

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/03 - Modelling/00 - Modelling|Modelling]]

## What it is

Subdivision surface takes a low-polygon **cage** and produces a smooth limit surface. You model
the cage; the smooth result is derived.

## The control problem

Subdivision smooths everything, including edges you wanted sharp. Three ways to control it:

| Method | How | When |
| --- | --- | --- |
| **Support loops** | Extra edge loops near the edge to be held | The general solution. Predictable, exports everywhere. |
| **Edge creases** | Per-edge crease weight | Fast, but exports poorly and can look artificial |
| **Bevel then subdivide** | Bevel modifier above subdivision | Hard surface. Best of both - see section 04. |

**The closer the support loops, the sharper the edge.** That is the whole mechanism.

## Cage discipline

- **Quads**, because triangles pinch and n-gons behave unpredictably
- **Even spacing** where curvature is even - uneven cage spacing shows as uneven smoothing
- **Poles away from the silhouette**
- Keep the cage as light as it can be. A dense cage defeats the purpose and is harder to edit.

## When subdivision is the wrong tool

On mechanical objects with mostly flat faces and sharp edges. You spend the whole time adding
support loops to fight the smoothing. Flat shading plus a bevel modifier reaches a better result
faster - see [[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface|Hard Surface]].

Also wrong when the polygon budget is fixed and low, and when the asset must match a scanned or
photogrammetric reference exactly.

## Viewport versus render levels

Separate settings. Viewport 1, render 3 is a sensible working default - and the standard reason a
render is unexpectedly slow or unexpectedly heavy. Check it before diagnosing anything else.

## Common mistakes

- Support loops so far from the edge that everything looks soft, or so close that shading pinches
- Triangles left in a subdivision cage
- Creases used everywhere, then discovering the exporter drops them
- Subdividing to fix a silhouette that was wrong in the cage - subdivision smooths, it does not
  correct proportion
- Render level left at 4 or 5 on a scene with many objects

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Topology|Topology]] ·
[[3D & Blender Knowledge/04 - Hard Surface/Weighted Normals & Bevel Discipline|Weighted Normals & Bevel Discipline]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Subdivision Surface modifier, creasing, viewport/render levels.
Cage discipline is practitioner judgement.
