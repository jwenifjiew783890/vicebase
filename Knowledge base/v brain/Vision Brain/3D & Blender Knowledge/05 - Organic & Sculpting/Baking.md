---
type: note
domain: 3D & Blender Knowledge
section: 05 - Organic & Sculpting
created: 2026-09-03
---

# Baking

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/05 - Organic & Sculpting/00 - Organic & Sculpting|Organic & Sculpting]]

## What it is

Transferring detail from a high-polygon mesh onto textures used by a low-polygon mesh. The
low-poly then *looks* detailed at a fraction of the cost.

## What gets baked

| Map | Carries |
| --- | --- |
| **Normal** | Surface direction - the illusion of geometric detail |
| **Ambient occlusion** | Contact shadow in crevices |
| **Displacement / height** | Actual or parallax offset |
| **Curvature** | Convex and concave edges, used to drive wear in texturing |
| **Diffuse / base colour** | Colour, if painted on the high-poly |

## Requirements

Baking fails in specific, diagnosable ways. It needs:

1. **Low-poly UV-unwrapped**, without overlapping islands. Overlaps mean two surfaces competing
   for the same texture pixels.
2. **Both meshes occupying the same space**, aligned.
3. **A cage or sensible ray distance**, so rays from the low-poly find the right high-poly surface.
4. **Correct normals on both.**
5. **Non-Color colour space** on the resulting normal map when it is used.

## The recurring failures

| Symptom | Cause |
| --- | --- |
| Patches of noise or wrong detail | Ray distance too large - rays hitting the wrong surface |
| Missing detail in places | Ray distance too small, or high-poly outside the cage |
| Hard seams in the normal map | UV seams with no padding, or mismatched smoothing |
| Detail from the other side of the mesh | Overlapping UVs, or no cage on a thin object |
| Normal map looks inverted | Green channel convention differs between applications |

**Green channel direction (OpenGL vs DirectX) is a real and common problem** when moving between
Blender and a game engine. It shows as lighting that appears to come from the wrong side within
surface detail.

## Practical sequence

1. Finish and check the low-poly UVs.
2. Position high and low together.
3. Set ray distance / cage, starting small and increasing until gaps close.
4. Bake at higher resolution than needed and downsample - it hides small errors.
5. **Inspect the map itself**, not only the result. Errors are obvious in the texture and subtle
   in the render.
6. Verify on the low-poly under moving light.

## Common mistakes

- Baking before the UVs are final
- Overlapping UVs on the bake target
- One ray distance for an object with widely varying thickness
- Not padding the bake, so seams show at lower mip levels
- Wrong colour space on the resulting map

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/UVs & Texture Space|UVs & Texture Space]] ·
[[3D & Blender Knowledge/07 - Materials & Shaders/Texture Workflow|Texture Workflow]]

## Sources

Blender Manual (CC-BY-SA 4.0) - bake types, cage and ray distance, colour space. The failure table
is practitioner synthesis.
