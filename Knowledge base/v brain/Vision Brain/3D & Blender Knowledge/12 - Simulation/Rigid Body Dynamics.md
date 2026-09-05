---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Rigid Body Dynamics

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Solid objects that collide, fall and respond to force without deforming. Blender's rigid body
system is built on the Bullet physics engine.

Builds on [[3D & Blender Knowledge/12 - Simulation/Simulation Fundamentals|Simulation Fundamentals]],
which covers scale, substeps and caching - all of which apply here first.

## Active and passive

- **Active** - simulated; moves under gravity and collision
- **Passive** - participates in collision but is not itself simulated. Floors, walls, and objects
  animated by hand that other objects must react to.

An animated passive object needs its **animated** flag enabled or the solver will not see its
motion.

## Collision shapes are the whole performance story

The collision shape is not the render mesh. Choosing it is the main decision:

| Shape | Cost | Accuracy | Use |
| --- | --- | --- | --- |
| Box, Sphere, Capsule | Cheapest | Crude | Primitives, debris, anything small or fast |
| Convex Hull | Cheap | Good for convex objects | The sensible default for most props |
| Mesh | Expensive | Exact | Concave objects where the shape genuinely matters |
| Compound | Moderate | Good | Concave objects built from several convex parts |

**Mesh collision on everything is the standard performance mistake.** It is also less stable -
convex hulls resolve more reliably.

A concave object with a convex hull will not let anything inside it; if a ball must land inside a
bowl, the bowl needs mesh or compound collision.

## The settings that matter

- **Mass** - relative mass matters, absolute does not, but it must be plausible relative to scale
- **Friction** and **bounciness** - the character of the interaction
- **Margin** - a small collision buffer. Too large and objects float; too small and they
  interpenetrate or jitter.
- **Damping** - stops objects sliding or rotating forever
- **Deactivation** - lets settled objects sleep, which is a large performance saving in a scene
  with many objects

## Constraints

Rigid body constraints connect objects: hinge, point, slider, generic, motor. This is how doors,
chains, ragdolls and mechanisms are built.

## Baking and control

The simulation is deterministic from the same starting state, but not directly keyframable. To take
control:

- **Bake** the simulation, then convert to keyframes if hand adjustment is needed
- Adjust the starting state, mass and friction rather than trying to art-direct mid-simulation
- For a precise outcome, simulate then adjust the resulting keys

## Common mistakes

- Mesh collision everywhere
- Convex hull on a concave object that must contain something
- Unapplied scale, so collision shapes mismatch the visible mesh
- Too few substeps for fast objects - tunnelling
- Animated passive objects without the animated flag
- Expecting precise art direction from a solver

## Related

[[3D & Blender Knowledge/12 - Simulation/Simulation Fundamentals|Simulation Fundamentals]] ·
[[3D & Blender Knowledge/12 - Simulation/Particles & Destruction|Particles & Destruction]]

## Sources

Blender Manual (CC-BY-SA 4.0) - rigid body settings, collision shapes, constraints, world settings
and caching.
