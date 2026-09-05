---
type: note
domain: 3D & Blender Knowledge
section: 22 - Game & Real-Time Assets
created: 2026-09-03
---

# Game Asset Workflow

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/22 - Game & Real-Time Assets/00 - Game & Real-Time Assets|Game & Real-Time Assets]]

## What it is

Producing an asset that renders in **milliseconds**, repeatedly, on hardware you do not control -
rather than once, slowly, on yours.

## The constraint that changes everything

A render can take minutes per frame. A game has roughly 16 milliseconds for the **entire scene**.
Consequences:

- Polygon budgets are real and enforced
- Texture memory is a hard limit
- Draw calls matter - one object with one material is cheaper than four objects with four
- No path tracing; lighting is baked or approximated
- Detail comes from **textures, not geometry**

## The standard pipeline

```
blockout -> high-poly -> low-poly (retopology) -> UV unwrap
         -> bake high onto low -> texture -> export -> validate in engine
```

**High-poly** carries all the detail - sculpted or hard-surface with full bevels. It is never
shipped.

**Low-poly** is what ships. It must have a good silhouette, sensible topology for deformation if
animated, and clean UVs. See
[[3D & Blender Knowledge/03 - Modelling/Retopology|Retopology]].

**Baking** transfers the high-poly detail into normal, AO and curvature maps. This is the step that
makes a low-poly asset look detailed - see
[[3D & Blender Knowledge/05 - Organic & Sculpting/Baking|Baking]].

## Budgets

Budgets come from the project, not from Blender. Establish them **before modelling**:

- triangle count per asset class
- texture resolution and how many maps
- material and draw-call count
- bone count, for skinned meshes

Modelling without a budget produces assets that must be rebuilt.

## Where polygons belong

- **Silhouette** - the outline is the only thing a normal map cannot fake. Spend polygons here.
- **Deformation** - loops where it bends
- **Not** on surface detail that a normal map can carry
- **Not** on anything below the pixel size at the distance it will be seen

## Texture practice

- **Atlas** where possible - several objects sharing one texture set reduces draw calls
- **Trim sheets** for architectural and modular work - one texture strip serving many pieces
- **Tiling** materials for large surfaces, with unique detail layered on
- Power-of-two resolutions, as engines expect
- Channel-packed maps - roughness, metallic and AO in separate channels of one image

## Common mistakes

- Render-quality topology on a game asset
- No budget established before starting
- Detail modelled that should have been baked
- Every object with its own unique texture set
- Ignoring draw calls entirely
- Validating only in Blender, never in the engine

## Related

[[3D & Blender Knowledge/22 - Game & Real-Time Assets/LOD & Real-Time Optimisation|LOD & Real-Time Optimisation]] ·
[[3D & Blender Knowledge/22 - Game & Real-Time Assets/Engine Export Preparation|Engine Export Preparation]]

## Sources

Practitioner synthesis - standard game-art pipeline practice. Baking and retopology mechanics are
documented in the Blender Manual (CC-BY-SA 4.0).
