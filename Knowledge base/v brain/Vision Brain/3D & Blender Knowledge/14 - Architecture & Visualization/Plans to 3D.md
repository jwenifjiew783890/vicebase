---
type: note
domain: 3D & Blender Knowledge
section: 14 - Architecture & Visualization
created: 2026-09-03
---

# Plans to 3D

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization|Architecture & Visualization]]

## What it is

Converting 2D drawings - floor plans, elevations, sections - into accurate 3D geometry.

## Accuracy is the requirement

An architectural model that looks right but measures wrong is worthless: it misrepresents
something that will be built. Every dimension must be traceable to the drawing.

## Setting up the reference

1. **Set scene units to metric, metres**, before anything else.
2. Import the plan as a reference image or imported vector geometry.
3. **Scale it using a known dimension.** Find a dimensioned element - a wall length, a door width,
   a grid spacing - and scale until it measures exactly that.
   **Never scale a plan by eye.** Every subsequent dimension inherits that error.
4. Verify with a second known dimension elsewhere on the plan. If both agree, the scale is right.
5. Lock the reference so it cannot be nudged.

## Working order

Build in the order a building is built - it keeps relationships correct:

1. **Grid and levels** - structural grid, floor heights
2. **Structure** - columns, load-bearing walls, slabs
3. **Envelope** - external walls, roof
4. **Internal divisions** - partitions
5. **Openings** - doors and windows cut into the walls that now exist
6. **Circulation** - stairs, ramps, lifts
7. **Fixed elements** - kitchens, bathrooms, built-in furniture
8. **Loose furniture and dressing**

## Reading a plan

- **Walls** are two parallel lines; the gap is the real thickness and matters
- **Doors** show a leaf and a swing arc, which tells you the hinge side and opening direction
- **Windows** appear as breaks in the wall with thinner lines
- **Stairs** show tread lines with a direction arrow and a break line
- **Levels and sections** give heights, which a plan alone never does
- **Hatching** indicates material

**A plan gives no height information.** Elevations and sections are required, and if they are
missing the heights must be established from standards or from the client - never guessed silently.

## Standard dimensions to sanity-check against

| Element | Typical |
| --- | --- |
| Internal wall | 100-150 mm |
| External wall | 250-400 mm |
| Door | 2.0 m x 0.8-0.9 m |
| Ceiling, residential | 2.4-2.7 m |
| Window sill | ~0.9 m |
| Stair riser / going | 0.15-0.19 m / 0.25-0.30 m |
| Corridor | 1.2 m minimum |
| Counter | 0.9 m |

If a modelled element falls outside these, check the drawing rather than assuming.

## Common mistakes

- Scaling the plan by eye
- Modelling walls as zero-thickness planes, so openings and reveals are impossible
- Ignoring wall thickness, making internal dimensions wrong
- Guessing heights when no section was supplied
- Reference image nudged mid-project, invalidating everything after
- Not verifying scale against a second dimension

## Related

[[3D & Blender Knowledge/03 - Modelling/Precision Modelling|Precision Modelling]] ·
[[3D & Blender Knowledge/14 - Architecture & Visualization/Walls, Openings & Building Elements|Walls, Openings & Building Elements]]

## Sources

Practitioner synthesis. Dimensions are standard architectural reference figures and vary by
jurisdiction and building code - **verify against local regulations for real projects**.
