---
type: note
domain: 3D & Blender Knowledge
section: 03 - Modelling
created: 2026-09-03
---

# Retopology

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/03 - Modelling/00 - Modelling|Modelling]]

## What it is

Building new, clean, purposeful topology over an existing dense surface - a sculpt, a scan, or
boolean output.

## Why it exists

A sculpt has millions of evenly distributed triangles. That is right for sculpting and wrong for
everything else: it cannot be rigged, UV-unwrapped sensibly, or rendered efficiently. Retopology
produces a mesh with the *same shape* and *usable structure*.

## When it is needed

- After sculpting anything that will be animated, textured or shipped
- After 3D scanning or photogrammetry
- When inherited geometry is unusable
- When a high-poly must be baked onto a low-poly

**When it is not needed:** a sculpt destined only for a still render, where the dense mesh renders
fine and nobody will edit it. Retopologising it wastes a day for nothing.

## Approaches

| Approach | Result | Use |
| --- | --- | --- |
| Manual (poly build, snapping to surface) | Best control, best edge flow | Characters, anything deforming |
| Shrinkwrap a simple base | Fast, decent | Props with simple forms |
| Automatic (quad remesh) | Even, no intent | Base for further sculpting, background assets |
| Voxel remesh | Uniform, ignores edge flow | Mid-sculpt topology reset, not final |

Automatic remeshing does not understand what the model is. It gives even topology, not *meaningful*
topology - no loops at joints, no density where detail is.

## Practical setup

- Snap to face, with Project Individual Elements enabled
- A small Shrinkwrap on the retopo mesh keeps it on the surface as you work
- Slight offset or "in front" display so the new mesh is visible against the dense one
- Mirror modifier for symmetric subjects

## Priorities while retopologising

1. **Loops where it deforms** - around joints, mouth, eyes
2. **Density where the detail and the camera are**
3. **Quads**, since this mesh will subdivide
4. **Silhouette preserved** - check against the original from the camera angle

## Common mistakes

- Retopologising something that never needed it
- Even density everywhere, wasting polygons on flat regions and starving detailed ones
- Auto-remesh accepted as final on a character
- Forgetting the retopo mesh must still be UV-unwrapped
- Losing the silhouette while chasing clean loops

## Related

[[3D & Blender Knowledge/05 - Organic & Sculpting/Sculpt Workflow|Sculpt Workflow]] ·
[[3D & Blender Knowledge/05 - Organic & Sculpting/Baking|Baking]] ·
[[3D & Blender Knowledge/01 - 3D Fundamentals/Topology|Topology]]

## Sources

Blender Manual (CC-BY-SA 4.0) - snapping, Shrinkwrap, remesh tools. Approach selection and
priorities are practitioner judgement.
