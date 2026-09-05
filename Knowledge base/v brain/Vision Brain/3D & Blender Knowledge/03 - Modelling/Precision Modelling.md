---
type: note
domain: 3D & Blender Knowledge
section: 03 - Modelling
created: 2026-09-03
---

# Precision Modelling

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/03 - Modelling/00 - Modelling|Modelling]]

## What it is

Modelling to actual dimensions rather than by eye. Required for architecture, engineering,
product design and anything that must match a drawing or be manufactured.

## The tools

| Tool | Use |
| --- | --- |
| **Numeric input** | Type the value. `G X 2.4` moves exactly 2.4 m on X. |
| **Snapping** | To vertex, edge, face, increment or grid |
| **The N panel** | Read and set exact dimensions and locations |
| **Exact Boolean solver** | Slower, more reliable on precise coplanar geometry |
| **Reference images / drawings** | Set to correct scale, modelled over |

Numeric input is the core skill. Dragging until it looks right is how dimensional errors enter.

## Workflow

1. Set units first.
2. Import the drawing or plan; **scale it using a known dimension**, not by eye.
3. Model the primary dimensions numerically.
4. Snap to derive dependent geometry rather than measuring it again.
5. Verify with the N panel and the measure tool.

## Where precision genuinely matters

- Architecture - a wall of the wrong thickness propagates through the whole model
- Anything manufactured, or 3D printed
- Assets that must fit together - modular kits, mechanical assemblies
- Anything that will be dimensioned or presented as accurate

## Where it does not

Organic forms, background dressing, and anything judged by eye. Imposing numeric precision on a
sculpted rock wastes time and gains nothing.

## Common mistakes

- Scaling a reference image by eye, so every derived dimension inherits the error
- Modelling at arbitrary scale intending to fix it later
- Not applying scale, so the N panel dimensions and the mesh disagree
- Using the fast boolean solver on precise coplanar geometry and getting unstable results
- Trusting the visual result instead of measuring

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Scale & Units|Scale & Units]] ·
[[3D & Blender Knowledge/14 - Architecture & Visualization/Plans to 3D|Plans to 3D]]

## Sources

Blender Manual (CC-BY-SA 4.0) - snapping, transform numeric entry, the measure tool, boolean
solvers. Workflow ordering is practitioner judgement.
