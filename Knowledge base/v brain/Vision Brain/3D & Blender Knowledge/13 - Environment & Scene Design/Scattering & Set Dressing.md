---
type: note
domain: 3D & Blender Knowledge
section: 13 - Environment & Scene Design
created: 2026-09-03
---

# Scattering & Set Dressing

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/13 - Environment & Scene Design/00 - Environment & Scene Design|Environment & Scene Design]]

## What it is

Distributing the many small elements that make an environment feel inhabited - vegetation, debris,
gravel, clutter, props.

## Distribute with logic

Random scatter across a whole surface reads as noise. Real distribution has causes:

- **Vegetation** grows where there is soil, light and water - not on paths, not on rock faces
- **Debris** collects in corners, against edges, in depressions - wind and water move it
- **Wear** appears where people walk, which is the shortest route between destinations
- **Clutter** accumulates where people stop and put things down

Drive density with masks - vertex paint, textures, proximity to other geometry, slope from the
surface normal.

## Variation

Uniform instances are immediately obvious. Vary rotation (at minimum around the up axis), scale
within a modest range, and the source object itself from a collection of variants.

## Density and cost

Scattering is where environments become unrenderable. Discipline:

- Scatter **only where the camera sees** - a mask limiting distribution to the visible frustum
  costs nothing and can cut counts by an order of magnitude
- Keep source geometry light; it is multiplied by the instance count
- Lower-detail sources for distant instances
- **Never realise instances** unless required
- Reduce viewport display independently of render

## Layering

Natural environments have several scales at once: large trees, shrubs, ground cover, small debris.
A single scattered element reads as artificial; three or four layers at different scales read as a
place.

## Common mistakes

- Uniform random scatter with no logic
- Identical rotation and scale
- Scattering across the entire terrain when the camera sees a corner
- Heavy source geometry multiplied thousands of times
- Realising instances and exhausting memory
- One layer only

## Related

[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Instancing & Scattering|Instancing & Scattering]] ·
[[3D & Blender Knowledge/15 - Optimization & Performance/Scene Weight|Scene Weight]]

## Sources

Practitioner synthesis - standard environment art practice. Instancing mechanics are documented in
the Blender Manual (CC-BY-SA 4.0).
