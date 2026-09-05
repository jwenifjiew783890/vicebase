---
type: note
domain: 3D & Blender Knowledge
section: 10 - Rendering
created: 2026-09-03
---

# Cycles vs EEVEE

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/10 - Rendering/00 - Rendering|Rendering]]

## What it is

Two fundamentally different renderers. Choosing correctly saves more time than any optimisation.

| | Cycles | EEVEE |
| --- | --- | --- |
| Method | Path tracing - simulates light transport | Rasterisation - approximates it in real time |
| Reflection / refraction | Physically correct | Screen-space approximations with real limits |
| Global illumination | Inherent | Approximated |
| Shadows | Accurate, physically soft | Shadow maps, with bias and resolution artefacts |
| Speed | Slow, and scales with light complexity | Fast, near real time |
| Noise | Present, must be resolved | None - the errors are approximation instead |
| Use for | Final stills, archviz, product, anything where light realism carries the image | Look development, previews, stylised work, animation where speed dominates |

## What does not transfer

**Materials mostly transfer. Lighting does not.** A scene lit to look right in EEVEE will usually
be wrong in Cycles, because EEVEE approximates the bounced light that Cycles simulates.

Specifically unreliable in EEVEE:
- Reflections of anything off-screen - screen-space reflection cannot show what is not rendered
- Refraction through complex glass
- Accurate contact shadows and fine ambient occlusion
- True caustics

**Practical consequence: light in the engine you will render in.** Using EEVEE for speed and
switching to Cycles at the end means relighting.

## When EEVEE is the right choice

- Iterating on materials and layout, where speed of feedback matters more than accuracy
- Stylised or non-photoreal work
- Animation with a deadline, where per-frame Cycles cost is prohibitive
- Real-time or interactive output

## When Cycles is required

- Photorealism
- Interiors, where bounced light is the whole illumination
- Glass, liquids, accurate metals
- Architectural visualisation presented as representative of reality

## GPU and CPU

Cycles renders on either. GPU is usually far faster but is **bounded by VRAM** - a scene that does
not fit falls back or fails. Textures and subdivision dominate VRAM; see
[[3D & Blender Knowledge/15 - Optimization & Performance/VRAM & Memory|VRAM & Memory]].

## Common mistakes

- Lighting in EEVEE, rendering in Cycles
- Expecting EEVEE screen-space reflections to show off-screen objects
- Using Cycles for a stylised animation where EEVEE would have been indistinguishable and far
  faster
- Blaming materials for differences that are engine approximations

## Related

[[3D & Blender Knowledge/10 - Rendering/Cycles Sampling & Noise|Cycles Sampling & Noise]] ·
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Cycles and EEVEE documentation, engine capabilities and
limitations.
