---
type: note
domain: 3D & Blender Knowledge
section: 07 - Materials & Shaders
created: 2026-09-03
---

# Procedural Materials

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/07 - Materials & Shaders/00 - Materials & Shaders|Materials & Shaders]]

## What it is

Surfaces built from noise, gradients and maths rather than images. Resolution-independent, tileable
without seams, and adjustable by parameter.

## When they win

- No UVs available or wanted
- Infinite or very large surfaces where tiling would show
- Variation needed across many objects from one material
- Resolution must hold at any camera distance
- The look is being explored and needs to stay adjustable

## When images win

- Photographic realism from real-world source
- Specific, authored detail - a label, a logo, particular wear
- Performance matters, especially real-time
- Someone else must edit it in a texture package

**Realistic dirt and wear are usually faster from a texture than from a node graph.** Procedural is
not automatically more advanced.

## The building blocks

| Node | Use |
| --- | --- |
| Noise | The general-purpose irregularity source |
| Voronoi | Cells - stone, scales, cracks, organic patterns |
| Musgrave / fractal noise | Terrain-like multi-scale variation |
| Wave | Stripes, wood grain, ripples |
| Gradient | Directional falloff |
| Color Ramp | **Shapes any of the above into what you actually want** |
| Bump | Surface detail without geometry |
| Mapping / Texture Coordinate | Where the pattern lives and at what scale |

Color Ramp does most of the work. Raw noise rarely looks like anything; noise pushed through a
well-adjusted ramp looks like a material.

## Coordinates matter

- **Generated** - fits the object bounds, survives deformation
- **Object** - stable in object space, good for controlled placement
- **UV** - follows the unwrap
- **World / Geometry** - stable in the scene, so scattered objects do not repeat identically

Choosing the wrong space is why a procedural texture swims during animation or repeats identically
across instances.

## Layering

Real surfaces are layered: base material, larger-scale variation, dirt in crevices, wear on edges.
Mix layers with masks derived from curvature, ambient occlusion or geometry attributes rather than
uniformly.

## Common mistakes

- Raw noise straight into roughness, giving an even fizz that reads as noise rather than material
- No large-scale variation, so the surface is uniform at distance
- One scale only - real surfaces vary at several scales at once
- Procedural everything, including detail an image would have delivered in a minute
- Wrong coordinate space, so textures swim or repeat

## Related

[[3D & Blender Knowledge/07 - Materials & Shaders/Principled BSDF & PBR Values|Principled BSDF & PBR Values]]

## Sources

Blender Manual (CC-BY-SA 4.0) - procedural texture nodes and coordinate systems. Layering and
selection guidance is practitioner judgement.
