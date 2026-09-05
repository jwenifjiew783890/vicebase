---
type: note
domain: 3D & Blender Knowledge
section: 04 - Hard Surface
created: 2026-09-03
---

# Panel Lines & Surface Detail

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface|Hard Surface]]

## What it is

The cuts, seams, fasteners, vents and inset panels that make a surface read as *assembled from
parts* rather than carved from one block.

## Why it matters

Large blank surfaces read as unfinished regardless of material quality. Real manufactured objects
are made of pieces, and the joins between them are visible. Panel lines are how a viewer reads
scale, construction and function.

## Where detail belongs

Detail should follow **function**, not decoration:

- Panels split where a part would actually be removable or serviceable
- Fasteners where load is carried
- Vents where heat or air must move
- Seams where two materials or two processes meet
- Wear where hands, tools or the ground touch

Randomly scattered greebles read as noise. Detail that implies a mechanism reads as design.

## Techniques

| Technique | Use |
| --- | --- |
| **Inset then extrude down** | Recessed panels. Simple, keeps quads. |
| **Boolean cut** | Complex shapes, quick. Needs cleanup if subdividing. |
| **Bevelled edge loops** | Cut lines that catch light |
| **Normal or height map** | Detail with no geometry cost - correct for background and games |
| **Geometry nodes scatter** | Repeated fasteners and rivets across a surface |

**Decide geometry versus texture by camera distance.** Close-up hero object: model it. Background:
texture it. Modelling detail no one will resolve is the most common waste in hard surface.

## Scale discipline

Panel gaps and fastener sizes carry scale information. A rivet modelled at 5 cm makes a vehicle
read as a toy. Use real dimensions - a typical panel gap is a couple of millimetres.

## Common mistakes

- Uniform detail everywhere, so nothing reads as important
- Greebles with no functional logic
- Detail modelled at a scale that contradicts the object's size
- Deep panel lines - real gaps are narrow, and depth reads as damage
- Modelling detail that the final camera cannot resolve

## Related

[[3D & Blender Knowledge/04 - Hard Surface/Weighted Normals & Bevel Discipline|Weighted Normals & Bevel Discipline]] ·
[[3D & Blender Knowledge/03 - Modelling/Boolean Workflow|Boolean Workflow]]

## Sources

Practitioner synthesis - standard hard-surface practice.
