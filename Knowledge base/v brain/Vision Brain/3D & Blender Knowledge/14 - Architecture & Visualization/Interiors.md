---
type: note
domain: 3D & Blender Knowledge
section: 14 - Architecture & Visualization
created: 2026-09-03
---

# Interiors

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization|Architecture & Visualization]]

## What it is

Interior visualisation - the hardest common case in archviz, because nearly all light is bounced
and every surface is close to camera.

## Why interiors are hard

1. **Light enters through small openings and bounces.** Direct light is a fraction of the
   illumination. Path tracing must transport light through many bounces, which is slow and noisy.
2. **Everything is close to camera**, so detail and material quality cannot hide.
3. **Wide lenses are needed**, which exaggerates perspective and reveals geometry errors.
4. **Spaces read as empty** without extensive dressing.

## Lighting interiors

- Light **through the windows**, with sun and sky outside. Do not place lights inside pretending to
  be daylight - the falloff and direction will be wrong.
- **Window portals** tell the renderer where light enters, cutting interior noise dramatically.
  Effectively mandatory for interiors.
- Increase **light bounces**; interiors need meaningfully more than exteriors, or they render
  unrealistically dark.
- Add practical lights - lamps, downlights - as visible motivated sources.
- Expect long renders. Interior global illumination is expensive and there is no shortcut.

See [[3D & Blender Knowledge/14 - Architecture & Visualization/Archviz Lighting|Archviz Lighting]].

## Dressing

An empty room reads as a model. A dressed room reads as a place. What matters most:

| Element | Why |
| --- | --- |
| **Textiles** | Rugs, curtains, cushions, throws - soften, add colour, catch light |
| **Books, objects, clutter** | Evidence of a person |
| **Plants** | Organic irregularity against architectural straightness |
| **Lighting fixtures** | Motivate the light, and read as designed |
| **Art and mirrors** | Break wall planes |
| **Slight disorder** | A cushion not centred, a chair pulled out - the strongest cue |

**Perfectly tidy reads as a showroom, which reads as computer-generated.** Real spaces have small
disorder.

## Camera in interiors

- **Eye level, around 1.5-1.6 m.** This is how the space will actually be experienced.
- Keep the camera **level**; use shift rather than tilt to keep verticals vertical.
- Wide is necessary but going too wide misrepresents the space, which matters when the image is
  used to sell it.
- Shoot from a corner to show two walls and give depth.

## Materials at close range

Every surface is near the camera, so:

- roughness variation matters enormously - fingerprints, wear, unevenness
- texel density must be high and consistent
- bevels on every visible edge - skirting, frames, furniture

## Common mistakes

- Lights placed inside instead of daylight through windows
- No portals, then fighting noise with samples
- Too few bounces, giving dark corners
- Camera tilted up, converging verticals
- Empty or showroom-tidy rooms
- Too-wide lens misrepresenting the space

## Related

[[3D & Blender Knowledge/08 - Lighting/Natural & Environment Lighting|Natural & Environment Lighting]] ·
[[3D & Blender Knowledge/09 - Cameras & Composition/Focal Length & Perspective|Focal Length & Perspective]]

## Sources

Practitioner synthesis. Portals, bounces and sampling behaviour are documented in the Blender
Manual (CC-BY-SA 4.0).
