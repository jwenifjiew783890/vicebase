---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Particles & Destruction

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Many small elements driven by rules - sparks, debris, dust, rain - and the breaking of objects into
pieces.

Blender has **two** particle approaches, and choosing correctly matters:

| System | Nature | Use |
| --- | --- | --- |
| **Particle system** (legacy) | Emitter and hair types, physics-driven | Hair and fur; simple emitter effects |
| **Geometry Nodes** | Fully procedural, controllable, inspectable | Everything else - and the direction Blender is moving |

**For new work, prefer Geometry Nodes** unless hair or fur is the requirement. It is controllable,
debuggable and integrates with the rest of the node ecosystem. See
[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Instancing & Scattering|Instancing & Scattering]].

## Hair and fur

The one area where the legacy particle system and Blender's newer hair curves remain the tool.
Practical points:

- **Guide-based grooming** - shape a few guides, interpolate between them
- **Children** multiply guides into full density; groom on parents, render with children
- Density and length driven by **vertex groups and textures**
- Hair is expensive to render; keep children counts proportionate to screen size

## Destruction

Blender has no built-in fracture system in the core distribution; destruction is assembled:

1. **Fracture the object into pieces** - via an add-on, geometry nodes, or by modelling the
   fragments
2. **Rigid body simulation** on the pieces, with constraints holding them together initially
3. **Break the constraints** to trigger the collapse
4. **Layer secondary elements** - dust, smoke, small debris - as separate simulations

**The secondary elements are what sell it.** Bare geometric fragments falling read as a physics
demo; the same fragments with dust and small debris read as destruction.

## Practical constraints

- Piece count drives simulation cost. Fracture only what is seen breaking.
- Interior faces of fragments need their own material - freshly broken surfaces do not look like
  the exterior
- Simulate at low piece counts first
- **Bake before rendering**

## Common mistakes

- Legacy particles where geometry nodes would be controllable and faster
- Grooming hair with children enabled, making everything slow
- Fracturing an entire object when only part of it breaks
- No interior material on fragments
- Destruction with no dust or debris layer
- Expecting exact art direction from a rigid-body collapse

## Related

[[3D & Blender Knowledge/12 - Simulation/Rigid Body Dynamics|Rigid Body Dynamics]] ·
[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Instancing & Scattering|Instancing & Scattering]]

## Sources

Blender Manual (CC-BY-SA 4.0) - particle systems, hair, rigid body constraints, geometry nodes.
The absence of a core fracture system and the assembly approach reflect the distribution as of
Blender 5.2; destruction craft is practitioner synthesis.
