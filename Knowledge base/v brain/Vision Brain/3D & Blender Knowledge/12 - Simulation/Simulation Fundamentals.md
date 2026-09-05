---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Simulation Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Motion computed from physical rules rather than keyframed - rigid bodies, cloth, soft bodies,
particles, fluid, smoke and fire.

## The three causes of nearly every failure

**1. Wrong scale.** Physics assumes metres and real gravity. An object modelled 100 times too large
falls in slow motion; too small, and it behaves like a toy. **Apply scale before simulating** - a
non-uniform object scale produces collision shapes that do not match the visible mesh.

This is the single most common cause of "the simulation looks wrong".

**2. Too few substeps.** The solver advances in discrete steps. If an object moves further in one
step than its own thickness, it passes straight through a collider - the classic tunnelling
failure. Fast motion and thin colliders both demand more substeps.

Symptoms: objects passing through surfaces, jitter, cloth exploding.

**3. Collision margins and thin geometry.** Colliders have a thickness. Too small and objects
interpenetrate; too large and they float above surfaces. Cloth on a thin collider needs enough
margin to catch it, and single-sided planes are unreliable as colliders - give them thickness.

## Caching

Simulations are cached per frame. The cache must be **baked** to be reliable, and it becomes
**invalid whenever the scene changes upstream** - moving a collider, changing scale, editing the
mesh.

Symptoms of a stale cache: the simulation does not react to a change, or behaves inconsistently
between playback and render. **Clear and rebake when anything upstream changes.**

Always simulate from frame 1. Starting mid-simulation gives objects no history and produces
nonsense.

## Practical discipline

- Simulate at **low resolution first**, confirm the behaviour, then raise resolution. High-detail
  simulation of wrong behaviour is a long way to waste an afternoon.
- Bake before rendering. Never render an unbaked simulation.
- Keep colliders **simple** - a low-poly proxy is faster and more stable than the render mesh.
- Cloth wants reasonable subdivision; too coarse cannot fold, too fine is slow and unstable.

## Cost

Fluid and smoke are the most expensive things in Blender, in both time and disk. A high-resolution
fluid cache can be tens of gigabytes. Budget for it before starting.

## Common mistakes

- Not applying scale, then fighting the solver
- Default substeps on fast motion, giving tunnelling
- Render mesh used as the collider
- Editing the scene without clearing the cache, then debugging a stale result
- High resolution before the behaviour is right
- Rendering unbaked

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Scale & Units|Scale & Units]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Simulation Failures|Simulation Failures]]

## Sources

Blender Manual (CC-BY-SA 4.0) - rigid body, cloth and fluid settings, substeps, collision margins,
caching and baking. Failure attribution is practitioner synthesis.
