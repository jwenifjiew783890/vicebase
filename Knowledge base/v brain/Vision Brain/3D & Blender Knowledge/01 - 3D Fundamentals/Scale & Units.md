---
type: note
domain: 3D & Blender Knowledge
section: 01 - 3D Fundamentals
created: 2026-09-03
---

# Scale & Units

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals|3D Fundamentals]]

## What it is

Blender works in real-world units when told to. Setting them costs seconds and prevents an entire
class of problems.

## Why it matters more than it appears to

Scale is invisible in isolation and obvious in combination. A chair modelled at twice life size
looks fine alone and absurd beside a person. More practically, wrong scale breaks:

- **Physics** - gravity, mass and collision assume metres. A "building" two units tall falls like
  a toy.
- **Lighting** - real light falls off with the square of distance. Wrong scale gives wrong falloff,
  and no amount of tweaking recovers it.
- **Depth of field** - focus distance and f-stop are physical. Wrong scale gives macro blur on a
  building.
- **Interchange** - other applications assume units. A model arriving 100 times too large has
  usually crossed a centimetre/metre boundary.

## Setting up

Scene Properties > Units. Choose the system and unit scale **before** modelling. For architecture,
work in metres and model to real dimensions.

## Useful real dimensions

Worth knowing without looking up, because they calibrate everything else:

| Thing | Approximate |
| --- | --- |
| Human height | 1.7-1.8 m |
| Eye height, standing | about 1.6 m |
| Door | 2.0 m by 0.8-0.9 m |
| Ceiling, residential | 2.4-2.7 m |
| Chair seat | 0.45 m |
| Desk or table | 0.73-0.75 m |
| Kitchen counter | 0.9 m |
| Stair riser | 0.15-0.19 m |
| Car | about 4.5 m long, 1.5 m tall |

Putting a 1.7 m human reference in the scene is the fastest scale check available.

## Apply scale

If an object was scaled in Object Mode, the mesh has not changed. Applying scale bakes it in. Do
this before bevelling, before physics, before export - see
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]]
for exactly what breaks otherwise.

## Common mistakes

- Modelling before setting units, then finding everything is 100 times off
- Scaling an object to fit rather than modelling it to correct dimensions
- Mixing assets authored at different scales in one scene
- Assuming the receiving application interprets units the same way

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Transforms & Coordinate Systems|Transforms & Coordinate Systems]] ·
[[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization|Architecture & Visualization]]

## Sources

Blender Manual (CC-BY-SA 4.0) for unit settings and Apply Transform. The dimensions are standard
reference figures; the physics and lighting consequences follow from the physical models Cycles
implements.
