---
type: note
domain: 3D & Blender Knowledge
section: 01 - 3D Fundamentals
created: 2026-09-03
---

# Topology

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals|3D Fundamentals]]

## What it is

The *arrangement* of a mesh's polygons - not how many, but how they flow. Two meshes can share a
silhouette and differ completely in usability.

## What topology is actually for

Topology serves three purposes. If none applies, it matters far less than people insist.

1. **Deformation.** A surface that bends needs edge loops running around the bend. No loops, no
   clean deformation, however good the rig.
2. **Subdivision.** Quads subdivide predictably. Triangles pinch. N-gons behave unpredictably.
3. **Editability.** Clean loops let you select, slide and adjust whole regions. Chaotic topology
   makes every change manual.

A static, non-subdivided prop seen once from one angle needs a good silhouette far more than it
needs perfect quads.

## Edge loops and rings

A **loop** follows edges through four-way intersections until it closes or meets a pole. A **ring**
is the perpendicular set. Loops are how detail is added in a controlled way - inserting a loop adds
resolution exactly where it is needed without disturbing the rest.

Loops stop at poles, which is why pole placement determines how editable a mesh stays.

## Poles

A pole is a vertex where the edge count is not four - typically three or five.

Poles are **unavoidable** on any closed curved surface. The skill is in placing them:

- put poles in **flat regions**, where the shading artefact is invisible
- keep them **off the silhouette**, where they would be seen
- accept them at natural transitions, such as where a cylinder meets a plane

Chasing a pole-free all-quad mesh on a form that mathematically requires poles is wasted effort.

## Topology for deformation

Where a limb bends, run loops around the joint - typically three or more, so the surface can
compress on the inside and stretch on the outside without collapsing. Faces should run *along* the
direction of stretch, not across it.

Anatomical edge flow follows muscle direction for exactly this reason: the mesh then deforms the
way the underlying form does.

## When to stop caring

- Static hero prop, one camera angle, no subdivision - silhouette and shading are what matter
- Background asset - polygon budget matters, topology barely does
- Anything animated, subdivided, or handed to another artist - topology matters a great deal

## Common mistakes

- Perfect topology on a background asset nobody will ever edit
- No loops at joints, discovered at rigging time
- Poles sitting on visible curved silhouettes
- Treating "all quads" as the goal rather than a means to one

## Related

[[3D & Blender Knowledge/03 - Modelling/Retopology|Retopology]] ·
[[3D & Blender Knowledge/03 - Modelling/Subdivision Workflow|Subdivision Workflow]]

## Sources

Practitioner synthesis. The subdivision behaviour underlying it - quads predictable, triangles
pinch - is documented in the Blender Manual (CC-BY-SA 4.0).
