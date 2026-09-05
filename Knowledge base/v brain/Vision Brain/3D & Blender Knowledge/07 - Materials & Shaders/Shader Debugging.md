---
type: note
domain: 3D & Blender Knowledge
section: 07 - Materials & Shaders
created: 2026-09-03
---

# Shader Debugging

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/07 - Materials & Shaders/00 - Materials & Shaders|Materials & Shaders]]

## What it is

Finding why a material does not look right. The important discipline is knowing when the problem is
**not** in the shader - which is most of the time.

## Check these before opening the shader editor

1. **Normals.** Face Orientation overlay. Red means inward. Flipped normals produce shading that
   looks exactly like a material fault.
2. **Is there any light?** A black material is usually an unlit scene, not a bad shader.
3. **Object scale applied?** Non-uniform scale distorts texture projection.
4. **UVs present and sane?** No UVs means no image texture.
5. **Correct material assigned?** Multi-material objects assign per face; slots can be wrong.

**Most reported material bugs are resolved by one of these five.**

## Symptom table

| Symptom | Likely cause |
| --- | --- |
| Material renders black | No light; or normals inverted; or a node disconnected; or fully absorbing |
| Magenta surface | Missing image file - broken path |
| Flat and lifeless | Uniform roughness, no normal detail, or flat lighting |
| Texture stretched or smeared | Bad UVs, or unapplied non-uniform scale |
| Texture swimming during animation | Wrong coordinate space - generated on a deforming mesh |
| Detail lit from the wrong side | Normal map green channel convention, or Non-Color not set |
| Looks right in EEVEE, wrong in Cycles | Approximation difference - EEVEE is not ground truth |
| Metal looks like grey plastic | Metallic not set to 1, or no environment to reflect |
| Glass renders black or opaque | Not enough light bounces, or no environment, or normals wrong |

## Metal needs something to reflect

A metal in an empty scene renders as a dark shape, because a metal shows its surroundings and
there are none. This is correct behaviour and looks like a bug. Add an HDRI or environment
geometry.

## Isolating

- Assign the material to a **default sphere in a known lighting setup**. If it looks right there,
  the problem is the scene or the mesh, not the material.
- Mute node branches one at a time.
- Connect an intermediate value directly to the surface output to see it as colour - the shader
  equivalent of a print statement.

## Common mistakes

- Debugging in the shader editor when the cause is a normal, a light or a UV
- Trusting the EEVEE preview for a Cycles render
- Changing several values at once
- Adding lights to fix a black material caused by inverted normals

## Related

[[3D & Blender Knowledge/04 - Debugging Method (3D)|Debugging Method]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Shading Artifacts|Shading Artifacts]]

## Sources

Practitioner synthesis. Underlying behaviour - colour space, normal maps, engine differences - is
documented in the Blender Manual (CC-BY-SA 4.0).
