---
type: note
domain: 3D & Blender Knowledge
section: 06 - Procedural & Geometry Nodes
created: 2026-09-03
---

# Instancing & Scattering

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/00 - Procedural & Geometry Nodes|Procedural & Geometry Nodes]]

## What it is

Placing many copies of geometry by reference rather than duplication. The mechanism behind forests,
crowds, rivets, gravel and every scene with more objects than memory would allow.

## Why instances are cheap

An instance stores a transform and a pointer to geometry. Ten thousand instances of a tree cost one
tree plus ten thousand matrices. Ten thousand *copies* cost ten thousand trees.

This is the difference between a scene that renders and one that does not.

## Distribution

**Distribute Points on Faces** is the usual source, with two modes:

- **Random** - fast, and produces clumping, because true randomness clumps
- **Poisson disk** - enforces minimum distance, giving even natural-looking spread. Usually the
  better default.

Control density with a **density attribute** - vertex paint, a texture, or a computed field. This
is how you get grass that thins near a path without placing anything by hand.

## Making it not look procedural

Uniform instances read as obviously generated. Vary:

- **Rotation** - random around the up axis at minimum
- **Scale** - a modest random range, not uniform
- **The source itself** - a Collection Info node with Pick Instance gives variety from several
  source objects
- **Density** - driven by a map, so distribution has structure

Small variation removes most of the artificial reading.

## Controlling what is where

- Weight paint or attributes to mask regions
- Proximity to other geometry - thin instances near paths, walls or water
- Slope and altitude from the surface normal - grass on flat ground, rock on steep

## Performance

- Keep source geometry light - an instanced tree at full detail multiplied ten thousand times is
  still ten thousand trees at render time
- Provide lower-detail sources for distant instances
- Do not realise unless required
- Viewport display can be reduced independently of render

## Common mistakes

- Realising instances, then wondering where the memory went
- Uniform rotation and scale, so the pattern is obvious
- Random distribution with visible clumps where Poisson would have been right
- Heavy source geometry
- Scattering across the whole surface when the camera sees a tenth of it

## Related

[[3D & Blender Knowledge/13 - Environment & Scene Design/Scattering & Set Dressing|Scattering & Set Dressing]] ·
[[3D & Blender Knowledge/15 - Optimization & Performance/Scene Weight|Scene Weight]]

## Sources

Blender Manual (CC-BY-SA 4.0) - point distribution, instancing nodes, Collection Info. Variation
and performance guidance is practitioner judgement.
