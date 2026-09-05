---
type: note
domain: 3D & Blender Knowledge
section: 13 - Environment & Scene Design
created: 2026-09-03
---

# Terrain & Landscape Generation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/13 - Environment & Scene Design/00 - Environment & Scene Design|Environment & Scene Design]]

## What it is

Building ground - hills, mountains, valleys, coastlines - and the surfaces that cover them.

## Approaches

| Approach | Control | Use |
| --- | --- | --- |
| **Sculpting a subdivided plane** | Highest artistic control | Hero terrain the camera is close to |
| **Displacement from a texture** | Fast, procedural, adjustable | Mid and far terrain, large areas |
| **Geometry Nodes** | Fully procedural and parametric | Repeatable, adjustable, large-scale generation |
| **Real elevation data** | Accurate | Real locations, site context |
| **Landscape add-ons** (e.g. A.N.T.) | Fast starting point | Quick blockouts and background terrain |

Most production terrain combines them: procedural or data-driven base, sculpted where the camera
looks.

## Resolution where the camera is

The recurring efficiency principle. Terrain covering square kilometres cannot be uniformly dense.

- high resolution only in the camera's near field
- displacement carries mid-distance detail
- far distance can be very coarse, or a matte

**Adaptive subdivision** ties displacement detail to camera distance, which is exactly the right
behaviour, at a cost.

## Making terrain read as real

Real landforms are shaped by **process**, and terrain that ignores this reads as noise:

- **Erosion** - water carves valleys and deposits material lower down. Ridges are sharp, valleys
  smooth.
- **Stratification** - visible layers in exposed rock
- **Slope determines cover** - vegetation on shallow slopes and where water collects; bare rock on
  steep faces. Drive scatter density by slope, not uniformly.
- **Scale variation** - large forms, medium forms, surface detail, at clearly different scales

Pure fractal noise gives a uniformly bumpy surface that reads as artificial precisely because it
lacks these.

## Texturing terrain

- **Blend by slope and altitude** using geometry attributes, not by hand-painting everywhere
- Tile detail textures, and break the tiling with a large-scale variation map
- Add unique detail only where the camera resolves it

## Scattering onto terrain

Covered in
[[3D & Blender Knowledge/13 - Environment & Scene Design/Scattering & Set Dressing|Scattering & Set Dressing]].
The terrain-specific point: **use the surface itself to drive distribution** - slope, altitude,
curvature and proximity to water are all readily available and produce believable placement for
free.

## Common mistakes

- Uniform subdivision across a huge area
- Pure noise with no erosion logic
- One texture scale, so the surface reads as tiled
- Vegetation scattered uniformly regardless of slope
- Sculpting detail the camera will never resolve
- Ignoring real elevation data when the location is real

## Related

[[3D & Blender Knowledge/13 - Environment & Scene Design/Scattering & Set Dressing|Scattering & Set Dressing]] ·
[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Geometry Nodes Fundamentals|Geometry Nodes Fundamentals]] ·
[[3D & Blender Knowledge/14 - Architecture & Visualization/Exteriors & Site Context|Exteriors & Site Context]]

## Sources

Blender Manual (CC-BY-SA 4.0) - displacement, adaptive subdivision, geometry nodes, sculpting.
Landform and erosion reasoning is general geomorphology applied as practitioner judgement.
