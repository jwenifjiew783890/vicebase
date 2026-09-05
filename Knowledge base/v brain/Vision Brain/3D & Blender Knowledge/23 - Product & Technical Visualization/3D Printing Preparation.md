---
type: note
domain: 3D & Blender Knowledge
section: 23 - Product & Technical Visualization
created: 2026-09-03
---

# 3D Printing Preparation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/23 - Product & Technical Visualization/00 - Product & Technical Visualization|Product & Technical Visualization]]

## What it is

Preparing geometry that must become a physical object. The requirements are stricter and more
binary than for rendering: geometry that renders perfectly may be unprintable.

## What printing demands that rendering does not

| Requirement | Why |
| --- | --- |
| **Manifold, watertight** | A slicer must determine inside from outside. An open surface has no inside. |
| **Consistent outward normals** | Inside/outside is defined by them |
| **No self-intersection** | Ambiguous volume |
| **No interior geometry** | Slicers may interpret internal faces as voids |
| **No zero-thickness surfaces** | A plane has no volume and cannot be printed |
| **Real-world scale** | The printer works in millimetres |
| **Minimum wall thickness** | Below the process minimum, features will not form |

Rendering forgives every one of these. Printing forgives none.

## Cleanup procedure

Building on [[3D & Blender Knowledge/01 - 3D Fundamentals/Mesh Anatomy|Mesh Anatomy]], which
defines these defects - this is the printing-specific sequence:

1. **Merge by Distance** - remove doubles
2. **Select non-manifold** (Select > All by Trait) and fix each: fill holes, delete interior faces,
   remove loose geometry
3. **Recalculate normals outside**; verify with Face Orientation
4. **Delete interior geometry** that is not intended as a void
5. **Solidify** any surface that has no thickness
6. **Apply all modifiers** - the printer gets geometry, not a modifier stack
7. **Apply scale**, and confirm dimensions in millimetres
8. Check **minimum feature size** against the process

Blender ships a **3D Print Toolbox** add-on that checks manifold status, wall thickness, overhangs
and intersections, and reports what fails. Enable it rather than checking by hand.

## Design for the process

- **Overhangs** beyond roughly 45 degrees need support in FDM printing; design to avoid them where
  possible
- **Wall thickness** must exceed the process minimum, which varies by printer and material
- **Tolerances** - parts that fit together need clearance, typically a few tenths of a millimetre
- **Orientation** affects strength: layer adhesion is the weak axis
- Small text and fine detail below the nozzle or resolution limit will not appear

## Export

- **STL** - universal, triangles only, no units embedded. Confirm the slicer's unit assumption.
- **3MF** - modern, carries units, colour and materials

Export at real size and **verify the dimensions in the slicer** before printing. A scale error
discovered after six hours of printing is an expensive lesson.

## Common mistakes

- Non-manifold geometry sent to a slicer
- Zero-thickness surfaces
- Modifiers not applied
- Wrong scale, discovered after printing
- Features below the printer's resolution
- Ignoring overhangs and then blaming print quality
- Not running the 3D Print Toolbox check

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Mesh Anatomy|Mesh Anatomy]] ·
[[3D & Blender Knowledge/01 - 3D Fundamentals/Scale & Units|Scale & Units]] ·
[[3D & Blender Knowledge/03 - Modelling/Precision Modelling|Precision Modelling]]

## Sources

Blender Manual (CC-BY-SA 4.0) - mesh cleanup tools, non-manifold selection, the 3D Print Toolbox
add-on. Process constraints (overhang angle, wall thickness, tolerances) are general additive-
manufacturing practice and **vary by printer and material** - confirm against the specific process.
