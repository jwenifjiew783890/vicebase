---
type: note
domain: 3D & Blender Knowledge
section: 07 - Materials & Shaders
created: 2026-09-03
---

# Texture Workflow

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/07 - Materials & Shaders/00 - Materials & Shaders|Materials & Shaders]]

## What it is

Driving material parameters with images rather than constants.

## The standard map set

| Map | Drives | Colour space |
| --- | --- | --- |
| Base Colour / Albedo | Base Colour | **sRGB** |
| Roughness | Roughness | **Non-Color** |
| Metallic | Metallic | **Non-Color** |
| Normal | Normal, via a Normal Map node | **Non-Color** |
| Height / Displacement | Displacement or bump | **Non-Color** |
| Ambient Occlusion | Multiplied into base colour, or ignored in path tracing | **Non-Color** |

## The setting that is silently wrong

**Only base colour is sRGB. Every other map is Non-Color.**

An sRGB transform applied to a roughness or normal map alters the values non-linearly. The result
is a material that is subtly wrong everywhere and looks fine in isolation - it only becomes obvious
against a correct version.

This is the single most common material error, and it produces no error message.

## Normal maps

- Always through a **Normal Map** node, never straight into the Normal socket
- Non-Color colour space
- **Green channel convention differs** between OpenGL and DirectX. Wrong convention means detail
  lit from the wrong direction - a subtle but persistent wrongness. Invert the green channel to
  convert.
- Strength above 1 exaggerates and usually looks wrong

## Displacement versus bump versus normal

| Technique | Changes silhouette | Cost |
| --- | --- | --- |
| Normal map | No | Free |
| Bump | No | Free |
| Displacement (true) | **Yes** | Expensive - real geometry |
| Adaptive subdivision + displacement | Yes | Expensive, camera-dependent |

Use normal maps unless the silhouette must change. A brick wall seen straight on needs a normal
map; the same wall at a grazing angle where bricks break the outline needs displacement.

## Managing texture files

- **Pack or use relative paths.** Absolute paths break the moment the project moves.
- Resolution proportionate to screen coverage - 4K on a distant object is waste
- Consistent texel density across a scene
- Name maps so their role is obvious

## Common mistakes

- sRGB on data maps - the silent one
- Normal map plugged in directly without the Normal Map node
- Wrong green channel convention
- 4K textures on everything regardless of visibility
- Absolute paths, then a move breaks every texture

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/UVs & Texture Space|UVs & Texture Space]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Missing Textures & Materials|Missing Textures & Materials]]

## Sources

Blender Manual (CC-BY-SA 4.0) - image texture nodes, colour space, normal maps, displacement.
Green-channel convention and resolution discipline are practitioner knowledge.
