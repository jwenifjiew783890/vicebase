---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Smoke, Fire & Explosions

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Gas simulation - smoke, fire, steam, explosions - using the same domain/flow/effector structure as
liquid, but rendered as a **volume** rather than a surface.

## Structure

- **Domain** - the simulated volume, rendered volumetrically
- **Flow** - emits smoke, fire, or both
- **Effectors** - obstacles and forces

Fire and smoke are separate channels: fire carries flame and temperature, smoke carries density.
Most convincing fire uses both.

## Volumes are expensive to render

This is the practical difference from other simulation. A volumetric domain adds significant render
cost on top of simulation cost, and volumetrics are among the most expensive things in Cycles.

Consequences:

- keep the domain **tight** around the action
- lower the domain resolution before assuming samples are the render cost
- consider rendering the volume as a separate pass and compositing it

## Getting believable results

**Motion is what convinces, not resolution.**

- **Vorticity** adds swirling detail; without it smoke rises as a smooth plume and reads as fake
- **Dissolve** so smoke fades rather than persisting forever
- **Buoyancy and temperature** drive the rise; fire rises because it is hot
- **Noise / upresolution** adds fine detail on top of a coarse base simulation - far cheaper than
  simulating at that resolution
- **Wind and turbulence** effectors break up regularity

## Explosions

An explosion is a short, violent flow event plus debris:

- a brief high-velocity flow burst, not a continuous emitter
- high initial temperature, rapid dissolve
- **the debris is a separate rigid-body or particle simulation** - the gas sim does not throw solid
  pieces
- the two are combined at render or composite time

Layering separate elements - flame, smoke, debris, sparks, heat distortion - reads far better than
one simulation attempting everything.

## Rendering

- Cycles renders volumes physically; EEVEE approximates them and is far faster for previews
- Volume step size trades quality against time
- **Emission from fire lights the scene** in Cycles, which is expensive but is what makes fire look
  integrated

## Common mistakes

- Domain far larger than the action
- No vorticity, giving smooth unconvincing plumes
- Smoke that never dissolves
- Expecting one simulation to produce flame, smoke and debris
- Iterating at high resolution
- Not budgeting for volumetric render cost

## Related

[[3D & Blender Knowledge/12 - Simulation/Fluid & Liquid Simulation|Fluid & Liquid Simulation]] ·
[[3D & Blender Knowledge/12 - Simulation/Particles & Destruction|Particles & Destruction]] ·
[[3D & Blender Knowledge/10 - Rendering/Cycles Sampling & Noise|Cycles Sampling & Noise]]

## Sources

Blender Manual (CC-BY-SA 4.0) - gas domain settings, flow types, vorticity, dissolve, noise,
volume rendering.
