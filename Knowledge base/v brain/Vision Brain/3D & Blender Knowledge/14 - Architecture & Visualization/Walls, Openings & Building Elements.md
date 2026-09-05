---
type: note
domain: 3D & Blender Knowledge
section: 14 - Architecture & Visualization
created: 2026-09-03
---

# Walls, Openings & Building Elements

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization|Architecture & Visualization]]

## What it is

Modelling the components a building is actually made of, in a way that stays editable.

## Walls have thickness

The most consequential decision. A wall is a volume, not a plane.

Thickness gives you **reveals** - the visible depth at a window or door opening - which is one of
the strongest cues that an interior render is real. Zero-thickness walls produce openings with no
depth, and the result reads as a video game.

Two approaches:

| Approach | Method | Trade |
| --- | --- | --- |
| **Solidify from a plane** | Draw the centreline, solidify to thickness | Fast, stays editable, thickness is one parameter |
| **Modelled volume** | Model the wall as a box | More control, more work to change |

Solidify is usually right during design, when thickness may change.

## Openings

Cut with **booleans from a live cutter object**, kept in a hidden collection:

- The cutter can be moved and resized after the cut - the opening follows
- One cutter can be reused for identical openings
- Keep the boolean modifier **live** as long as possible

A door or window opening should include the **reveal depth** and, where visible, the frame,
lining and sill. These small elements carry disproportionate realism.

## Doors and windows

- Model or source one good door and window, then instance
- Real frames have depth, profile and a shadow gap
- Glass needs thickness - single-plane glass looks wrong in reflection and refraction
- Handles, hinges and ironmongery are small but very visible at eye level

## Stairs

Governed by regulation and by comfort, and wrong stairs are immediately noticeable:

- Riser 0.15-0.19 m, going 0.25-0.30 m as typical residential values
- **All risers in a flight must be equal** - unequal risers are a trip hazard and a code violation
- Headroom above the flight is a real constraint that is easy to miss in 3D
- Handrails at roughly 0.9-1.0 m

Build stairs from one instanced step where possible, arrayed.

## Floors, ceilings and roofs

- Floors have build-up - structure, screed, finish - which affects finished floor level
- Ceilings are often lower than the structural slab, with a void for services
- Roofs need correct pitch and, if visible, correct construction

## Common mistakes

- Zero-thickness walls, giving openings with no reveal
- Boolean applied immediately, so openings cannot move
- Glass with no thickness
- Unequal risers
- Doors and windows modelled individually instead of instanced
- Ignoring floor and ceiling build-up, so heights are subtly wrong

## Related

[[3D & Blender Knowledge/03 - Modelling/Boolean Workflow|Boolean Workflow]] ·
[[3D & Blender Knowledge/13 - Environment & Scene Design/Modular Kits|Modular Kits]]

## Sources

Practitioner synthesis. Stair and dimension figures are typical values and **vary by building
code** - verify locally for real work.
