---
type: note
domain: 3D & Blender Knowledge
section: 22 - Game & Real-Time Assets
created: 2026-09-03
---

# LOD & Real-Time Optimisation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/22 - Game & Real-Time Assets/00 - Game & Real-Time Assets|Game & Real-Time Assets]]

## What it is

Level of Detail - shipping several versions of an asset at decreasing complexity, and swapping
between them by distance. Plus the wider set of decisions that keep a real-time scene at frame
rate.

## Why LODs exist

An object 20 pixels tall does not need 50,000 triangles. Rendering it at full detail costs the
same as rendering it filling the screen, and returns nothing. LODs pay the cost proportionate to
the screen size.

## Building a chain

A typical chain reduces roughly by half at each step:

| Level | Use | Typical reduction |
| --- | --- | --- |
| LOD0 | Close, hero | Full detail |
| LOD1 | Mid distance | ~50% |
| LOD2 | Far | ~25% |
| LOD3 / billboard | Very far | Silhouette only, or a card |

**Preserve the silhouette at every level.** Interior detail can go; the outline cannot, because
that is what the eye reads at distance.

Reduce by removing loops and detail deliberately where possible; automatic decimation is faster
but ignores what matters and often destroys the silhouette. Automatic decimation is acceptable for
the furthest levels.

## Popping

The visible jump when a level swaps. Reduce it by:

- keeping silhouettes consistent between levels
- switching at distances where the difference is below perception
- keeping UVs and materials identical, so texturing does not shift

**Popping is usually a silhouette problem**, not a distance problem.

## Beyond LODs

Real-time performance is rarely only geometry:

| Cost | Control |
| --- | --- |
| Draw calls | Merge objects, atlas textures, share materials |
| Overdraw | Avoid many layers of large transparent surfaces - a common and severe cost |
| Texture memory | Resolution proportionate to screen coverage; compression; mipmaps |
| Shader complexity | Instructions per pixel; simplify for distant materials |
| Shadow casting | Not every object needs to cast; disable on small props |
| Real-time lights | Expensive. Bake static lighting where possible. |

**Transparency and overdraw are the most commonly underestimated costs** - foliage cards in
particular.

## Profile, do not guess

Engines provide profilers showing where frame time actually goes. Optimising the wrong thing is the
normal outcome of guessing - the same discipline as
[[3D & Blender Knowledge/15 - Optimization & Performance/Render Time|Render Time]].

## Common mistakes

- LODs that lose the silhouette, producing visible popping
- Automatic decimation on the near levels
- Different UVs between levels, so textures shift on swap
- Optimising geometry when draw calls or overdraw were the cost
- Every object casting shadows
- No profiling

## Related

[[3D & Blender Knowledge/15 - Optimization & Performance/Scene Weight|Scene Weight]] ·
[[3D & Blender Knowledge/22 - Game & Real-Time Assets/Game Asset Workflow|Game Asset Workflow]]

## Sources

Practitioner synthesis - standard real-time optimisation practice. Decimation and mesh tools are
documented in the Blender Manual (CC-BY-SA 4.0).
