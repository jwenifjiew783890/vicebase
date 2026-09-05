---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Fluid & Liquid Simulation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Liquid simulated within a **domain** - a box defining the simulated volume. Objects inside it act
as flow sources, effectors or obstacles.

The most expensive simulation type in Blender, in time, memory and disk.

## The components

| Object | Role |
| --- | --- |
| **Domain** | The simulated volume. Everything happens inside it; nothing outside exists. |
| **Flow** | Emits liquid - inflow, or an initial volume |
| **Effector** | Obstacles and forces the liquid interacts with |

**The domain bounds the simulation absolutely.** Liquid leaving the domain vanishes, and a domain
larger than needed wastes resolution everywhere.

## Resolution and cost

Resolution is the dominant cost, and it scales badly - it is a volumetric grid, so doubling
resolution multiplies cost roughly eightfold.

**Always develop at low resolution.** Get the motion, timing and framing right, then raise
resolution once. Simulating at high resolution while iterating is how days disappear.

## Scale matters more here than anywhere

Fluid behaviour is strongly scale-dependent. A domain 100 times too large produces liquid that
moves like syrup in slow motion; too small and it behaves like a fine mist.

**Set real-world scale before simulating**, and apply scale on every participating object.

## Getting detail without brute force

- **Mesh** settings control how the liquid surface is generated from the simulation grid; upresolving
  the mesh is cheaper than raising the base simulation
- **Secondary particles** - spray, foam, bubbles - add apparent complexity without raising the base
  resolution, and are usually what makes liquid read as real
- Viscosity, surface tension and the liquid's material do a great deal of the visual work

## Caching

Fluid caches are large - tens of gigabytes is normal at production resolution. Plan for it:

- keep caches out of backup sets; they are regenerable
- bake before rendering, always
- clear and rebake after any upstream change

See [[3D & Blender Knowledge/19 - Production Workflows/Asset Pipeline|Asset Pipeline]] on separating
regenerable from irreplaceable data.

## Common mistakes

- Iterating at high resolution
- Wrong scene scale, giving syrup or mist
- Domain much larger than the action needs
- No secondary particles, so the liquid looks like moving jelly
- Rendering unbaked
- Caches backed up as though irreplaceable

## Related

[[3D & Blender Knowledge/12 - Simulation/Smoke, Fire & Explosions|Smoke, Fire & Explosions]] ·
[[3D & Blender Knowledge/12 - Simulation/Simulation Fundamentals|Simulation Fundamentals]]

## Sources

Blender Manual (CC-BY-SA 4.0) - fluid domain, flow and effector objects, resolution, mesh
generation, secondary particles, caching.
