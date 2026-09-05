---
type: note
domain: 3D & Blender Knowledge
section: 07 - Materials & Shaders
created: 2026-09-03
---

# Principled BSDF & PBR Values

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/07 - Materials & Shaders/00 - Materials & Shaders|Materials & Shaders]]

## What it is

A single physically-based shader covering most real materials. Getting plausible values into it
matters far more than node complexity - **most materials need no nodes at all, just correct
numbers.**

## The parameters that carry the result

| Parameter | Physical meaning | Practical guidance |
| --- | --- | --- |
| **Base Colour** | Diffuse albedo | Real surfaces are rarely pure black or white. Keep within roughly 0.03-0.9. |
| **Metallic** | Conductor or dielectric | **Binary.** 0 for everything non-metal, 1 for bare metal. |
| **Roughness** | Microsurface scatter | Where nearly all the character lives. Almost never 0 or 1. |
| **IOR** | Index of refraction | ~1.45 plastics, ~1.5 glass, ~1.33 water |
| **Transmission** | Light passing through | Glass, water, thin plastics |
| **Normal** | Surface direction detail | From a normal map, in Non-Color |

## Metallic is binary

This is the most misunderstood parameter. Metallic describes whether a material is an electrical
conductor. There is no "slightly metallic" material.

Intermediate values are for **transitions across a surface** - dust or paint over metal, driven by
a mask - not for a global "a bit shiny" look. Wanting more shine means lowering roughness, not
raising metallic.

A metal's Base Colour is its **reflection tint** (gold, copper, brass), not a diffuse colour.
Metals have no diffuse component.

## Plausible roughness values

| Surface | Roughness |
| --- | --- |
| Polished mirror, chrome | 0.0-0.05 |
| Polished plastic, glossy paint | 0.1-0.2 |
| Satin paint, smooth ceramic | 0.3-0.4 |
| Untreated wood, matte paint | 0.5-0.7 |
| Concrete, rough stone, fabric | 0.7-0.9 |
| Chalk, dust | 0.9-1.0 |

**Uniform roughness is the strongest tell of a synthetic material.** Real surfaces vary - fingerprints,
wear, dust, moisture. A roughness map, even a subtle noise texture, does more for realism than any
other single change.

## Priority when building a material

1. Correct metallic (0 or 1)
2. Plausible base colour
3. **Roughness variation** - the highest-value step
4. Normal detail
5. Everything else

## Common mistakes

- Intermediate metallic to make something "shiny"
- Pure black or pure white base colour
- Perfectly uniform roughness
- A diffuse colour on a metal, when it should be reflection tint
- Building elaborate node trees before the four core values are right

## Related

[[3D & Blender Knowledge/07 - Materials & Shaders/Texture Workflow|Texture Workflow]] ·
[[3D & Blender Knowledge/07 - Materials & Shaders/Shader Debugging|Shader Debugging]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Principled BSDF parameters. Value ranges follow standard PBR
practice and physical measurement conventions; the priority ordering is practitioner judgement.
