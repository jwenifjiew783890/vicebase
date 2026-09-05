---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# CGI & Live-Action Integration

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

Making a rendered element look like it was photographed with the plate. This is where a shot
succeeds or fails, and it is mostly about **matching**, not about render quality.

## What actually gives CG away

In rough order of how often it is the problem:

1. **Lighting direction and colour do not match**
2. **Black shadows** - CG shadows with no bounce light in them
3. **Too clean** - no grain, no lens artefacts, perfect edges
4. **Wrong scale**, so depth of field and motion feel wrong
5. **No interaction** - the CG does not touch, shadow, reflect or occlude anything real
6. **Perfectly sharp** where the plate is soft or blurred
7. **Colour not matched** to the plate's grade

Note that "the render is not photoreal enough" is not on the list. **A modestly detailed asset
matched well beats a beautiful asset matched badly**, every time.

## Matching lighting

The reliable route is an **HDRI shot on location**. Failing that, reconstruct from the plate:

- identify the key light's direction from shadows in the footage
- estimate its colour and hardness from shadow edges and highlights
- build the ambient from the environment's dominant colours
- reproduce practical light sources visible in the shot

A **grey ball and chrome ball** shot on set give direction, intensity and the environment directly.
If they exist, use them.

## Shadow catcher and holdouts

The essential mechanic for integration:

- A **shadow catcher** object is invisible in the render but receives shadows and, in Cycles, is
  rendered so that the CG shadow can be composited onto the plate. Model rough stand-in geometry
  matching the real surfaces.
- A **holdout** removes CG where a real object should occlude it.

Without stand-in geometry, CG objects float - they cast no shadow onto anything, and nothing real
passes in front of them.

## Contact is what sells it

The junction between CG and plate is scrutinised more than anything else:

- **contact shadow** where the object meets a surface - dark, tight, close
- **ambient occlusion** in the gap
- reflection of the CG in nearby real surfaces, if they are reflective
- dust, displaced material, or a slight settling at the contact point

## Final integration in comp

Applied to the CG so it matches the plate's imperfections:

| Step | Why |
| --- | --- |
| **Grade to the plate** | Match black level, highlight roll-off and colour cast |
| **Match sharpness** | The plate is softer than a render. Blur the CG slightly. |
| **Add grain** | Matched to the plate's grain. Clean CG over grainy plate is instantly visible. |
| **Lens effects** | Slight chromatic aberration, vignette, bloom - matched, not added arbitrarily |
| **Redistort** | Reapply the lens distortion removed for tracking |
| **Atmosphere** | Haze between camera and object, if the plate has depth |

**Grain is the most consistently forgotten step** and one of the most effective.

## Common mistakes

- Perfect, clean, sharp CG over grainy soft footage
- Black shadows with no bounce
- No stand-in geometry, so nothing catches shadow or occludes
- Forgetting to redistort
- Matching on a still frame, never in motion
- Improving render quality when the problem was matching

## Related

[[3D & Blender Knowledge/20 - VFX & Compositing/Compositor Fundamentals|Compositor Fundamentals]] ·
[[3D & Blender Knowledge/08 - Lighting/Natural & Environment Lighting|Natural & Environment Lighting]]

## Sources

Blender Manual (CC-BY-SA 4.0) - shadow catcher and holdout object properties, compositing nodes,
lens distortion. The integration checklist and failure ordering are standard VFX practice.
