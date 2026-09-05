---
type: note
domain: 3D & Blender Knowledge
section: 01 - 3D Fundamentals
created: 2026-09-03
---

# UVs & Texture Space

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals|3D Fundamentals]]

## What it is

A UV map flattens a 3D surface into 2D texture space so an image can be painted onto it. Every
vertex gets a UV coordinate, and the mapping is authored rather than automatic.

## Seams

A seam is where the surface is cut so it can lie flat. Every unwrap needs them - a closed surface
cannot flatten without cutting, for the same reason a globe cannot become a flat map without
distortion.

Place seams where they will not be seen:

- natural edges and material boundaries
- creases, panel lines, under overhangs
- the back or underside of the object

**Fewer seams means more distortion; more seams means more visible cuts.** That trade-off is the
whole craft of unwrapping.

## Texel density

Texture resolution per unit of surface area. If one object carries four times the texel density of
the object beside it, the difference is obvious and reads as an error.

Keep density consistent across objects sharing a shot. State it as pixels per metre and hold to it.

## Packing and the 0-1 space

UVs conventionally occupy the 0-1 square. Packing arranges islands to use that space efficiently,
because wasted UV space is wasted texture resolution.

**Overlapping UVs** are correct when tiling or mirroring - two identical halves sharing texture -
and wrong when baking, where two surfaces would compete for the same pixels. Know which case you
are in.

**UDIM** tiles extend beyond 0-1 for high-resolution work spread across multiple texture tiles.

## When you can skip UVs

- procedural materials using generated or object coordinates
- geometry-node instances that inherit mapping
- quick blockouts and previews

You cannot skip them for baking, for painted textures, or for any asset handed to another
application.

## Common mistakes

- Deferring UVs until the mesh is finished and dense - retrofitting is far worse than unwrapping
  as you go
- Inconsistent texel density across a scene
- Overlapping UVs on a mesh that is about to be baked
- A seam down the middle of the most visible surface
- Forgetting to apply scale before unwrapping, which distorts the result

## Related

[[3D & Blender Knowledge/07 - Materials & Shaders/Texture Workflow|Texture Workflow]] ·
[[3D & Blender Knowledge/05 - Organic & Sculpting/Baking|Baking]]

## Sources

Blender Manual (CC-BY-SA 4.0) for unwrapping, seams, packing and UDIM. Texel-density discipline
and seam placement are practitioner judgement.
