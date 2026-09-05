---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Cloth Simulation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Simulated fabric - clothing, curtains, flags, banners, soft covers.

## Resolution is the first decision

Cloth needs enough subdivision to fold, and not so much that it becomes slow and unstable.

- Too coarse: it cannot form realistic folds and looks like stiff card
- Too fine: slow, and prone to instability and self-intersection

**Simulate at moderate resolution, then add detail.** A subdivision surface *after* the cloth
modifier smooths the result without simulating at that density.

## Setup order

1. Model the garment at simulation resolution - reasonably even quads
2. **Apply scale** - cloth behaviour is scale-dependent, and this is the most common cause of cloth
   behaving like a bin liner or a sheet of steel
3. Set the collision object (the body) with **collision** enabled
4. Choose a material preset - cotton, denim, silk, rubber - as a starting point rather than
   inventing values
5. **Pin** the vertices that should not move, using a vertex group - the shoulders of a shirt, the
   top of a curtain
6. Simulate a few frames, check, adjust

## Collision

The main source of failure.

- **Distance / thickness** on both the cloth and the collider. Too small and cloth passes through;
  too large and it floats visibly above the surface.
- **Self-collision** must be enabled for cloth that folds onto itself, and it is expensive
- The collider should be a **simplified proxy**, not the render mesh, and slightly inflated
- Fast motion needs more **substeps** or the cloth tunnels through

## Starting state

The cloth must not intersect the collider on the first frame. Starting interpenetrated produces an
explosion, and it is the single most common cloth failure.

Either model the garment slightly off the body, or animate the body into the garment over the first
frames.

## Getting a specific result

Simulation is not directly art-directable. The practical approaches:

- **Let it settle**, then apply the result as the new rest shape and continue from there
- Use pinning to hold what must stay
- Add sewing or forces to guide, rather than fighting the solver
- Bake, then sculpt corrections on the cached result if a specific fold is required

## Common mistakes

- Unapplied scale
- Cloth intersecting the body at frame 1
- Self-collision off on a garment that folds
- Render mesh used as the collider
- Simulating at very high resolution before the behaviour is right
- Expecting exact art direction from the solver

## Related

[[3D & Blender Knowledge/12 - Simulation/Simulation Fundamentals|Simulation Fundamentals]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Simulation Failures|Simulation Failures]]

## Sources

Blender Manual (CC-BY-SA 4.0) - cloth settings, presets, pinning, collision and self-collision,
substeps and caching.
