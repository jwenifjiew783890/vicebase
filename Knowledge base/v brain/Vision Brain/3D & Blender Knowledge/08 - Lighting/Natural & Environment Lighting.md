---
type: note
domain: 3D & Blender Knowledge
section: 08 - Lighting
created: 2026-09-03
---

# Natural & Environment Lighting

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/08 - Lighting/00 - Lighting|Lighting]]

## What it is

Lighting from sky, sun and surroundings rather than placed fixtures.

## HDRI environment lighting

A high-dynamic-range panoramic image used as the world. It provides both illumination and
reflection, and it is the fastest route to plausible lighting because it carries real-world light
distribution.

- **Rotation matters** - it sets sun direction and therefore the whole composition of shadow
- Resolution matters only if the environment is visible in reflections or background; otherwise a
  small HDRI lights just as well
- An HDRI alone is often flat. **Add a sun** for direction and crisp shadow, with the HDRI carrying
  ambient and reflection.

## Sun and sky

The Sun light is directional - parallel rays, so shadow direction is uniform and size controls
penumbra softness. Angle controls how soft the shadow edge is; the real sun subtends about half a
degree.

A physical sky model gives correct sky colour and sun position for a time and place, which is
essential for architectural work where the sun path is a design constraint.

## Interiors

Interiors are the hardest lighting case, because nearly all illumination is **bounced**.

- Light through openings, not by placing lights inside pretending to be daylight
- Path tracing needs enough bounces for light to travel in - too few and interiors are unrealistically
  dark
- **Portals** on windows tell the renderer where light enters, dramatically reducing noise in
  interiors
- Expect longer renders. Interior GI is expensive and there is no way around it.

## Time of day

| Time | Character |
| --- | --- |
| Golden hour | Low, warm, long shadows, strong modelling. The reliable flattering choice. |
| Midday | High, harsh, short shadows, flat on horizontal surfaces |
| Overcast | Enormous soft source, minimal shadow, even and neutral |
| Blue hour | Cool ambient, artificial lights dominate, high contrast between the two |
| Night | Point sources, deep falloff, colour contrast carries the image |

## Common mistakes

- HDRI alone with no directional source, giving an evenly lit and lifeless result
- Never rotating the HDRI, so sun direction is accidental
- Interiors lit by lights placed inside instead of through windows
- Too few light bounces, then compensating by brightening lights until it looks wrong
- No window portals, then fighting interior noise with sample count

## Related

[[3D & Blender Knowledge/14 - Architecture & Visualization/Archviz Lighting|Archviz Lighting]] ·
[[3D & Blender Knowledge/10 - Rendering/Cycles Sampling & Noise|Cycles Sampling & Noise]]

## Sources

Blender Manual (CC-BY-SA 4.0) - world/environment lighting, sun light, sky texture, light portals.
Time-of-day characterisation and interior guidance are practitioner judgement.
