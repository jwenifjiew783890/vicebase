---
type: note
domain: 3D & Blender Knowledge
section: 12 - Simulation
created: 2026-09-03
---

# Soft Body & Deformation Physics

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/12 - Simulation/00 - Simulation|Simulation]]

## What it is

Objects that deform under force while keeping their overall shape - jelly, cushions, flesh, tyres,
inflatables. Distinct from cloth, which is a surface, and from rigid bodies, which do not deform.

## When to use it, and when not

Soft body is slow, hard to control and easily unstable. **Use it only when the deformation genuinely
must be physical.**

Usually better alternatives:

| Want | Better tool |
| --- | --- |
| Jiggle on a character | Bone-based jiggle, or a dedicated wobble setup |
| A cushion compressing | Shape key, driven by contact |
| Fabric | Cloth simulation |
| A wobbling antenna | A simple bone chain with damping |

Reaching for soft body first is a common misjudgement - it is the tool of last resort, not first.

## Setup

- **Goal** - a vertex group defining how strongly vertices return to their original position. This
  is the main control: high goal means stiff, low means floppy.
- **Edge stiffness** - resistance to stretching
- **Bending** - resistance to folding
- **Mass** and damping
- Collision with other objects, again via simplified colliders

## Stability

Soft body is the least stable simulation in Blender. Instability shows as vibration, expansion, or
geometry exploding.

Causes, in order:

1. **Unapplied scale**
2. Too few **substeps** for the stiffness used
3. Very stiff settings, which need much smaller time steps
4. Geometry that is too dense, or has very uneven edge lengths
5. Starting in an intersecting state

**If it explodes, reduce stiffness and raise substeps before changing anything else.**

## Practical approach

- Simulate at low resolution; apply subdivision after
- Even topology matters more here than in most simulation - long thin faces destabilise the solver
- Keep the simulated frame range short; bake and move on
- Consider whether the shot actually needs it at all

## Common mistakes

- Using soft body where a shape key or bone would do
- Very high stiffness with default substeps
- Dense, uneven geometry
- Unapplied scale
- Expecting fine art direction

## Related

[[3D & Blender Knowledge/12 - Simulation/Cloth Simulation|Cloth Simulation]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Shape Keys & Drivers|Shape Keys & Drivers]]

## Sources

Blender Manual (CC-BY-SA 4.0) - soft body settings, goal, edges, collision, solver steps. The
tool-selection guidance is practitioner judgement.
