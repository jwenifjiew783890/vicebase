---
type: note
domain: 3D & Blender Knowledge
section: 16 - Add-ons & Pipelines
created: 2026-09-03
---

# Import, Export & Interchange

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/16 - Add-ons & Pipelines/00 - Add-ons & Pipelines|Add-ons & Pipelines]]

## What it is

Moving geometry and scenes between applications. Every format loses something; the skill is knowing
what.

## Format selection

| Format | Carries | Use for |
| --- | --- | --- |
| **glTF / GLB** | Mesh, PBR materials, animation, scene graph | Real-time, web, the modern default for delivery |
| **FBX** | Mesh, materials (loosely), rigs, animation | Game engines, wide legacy support |
| **OBJ** | Mesh, UVs, basic materials. No animation. | Simple static geometry exchange |
| **USD** | Full scenes, layering, instancing | Large pipelines, increasingly the standard |
| **Alembic** | Baked geometry and animation caches, no rigs | Handing simulation or animation between packages |
| **STL / 3MF** | Raw triangles, no materials | 3D printing |

## What breaks, reliably

- **Units and scale** - the most common failure. Confirm the expected unit at both ends.
- **Axis convention** - Blender is Z-up; many targets are Y-up. Exporters offer conversion; use it
  deliberately.
- **Materials** - almost never transfer perfectly. Expect to rebuild them, and treat transferred
  materials as a starting point.
- **Modifiers** - generally must be applied, or explicitly enabled for export
- **Custom normals** - frequently lost or misinterpreted
- **Normal map green channel** - OpenGL vs DirectX convention
- **N-gons** - triangulated on export, sometimes badly. Triangulate deliberately if it matters.

## Pre-export checklist

Covered fully in
[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]]; the essentials:

- apply scale, clean transforms
- apply or intentionally keep modifiers
- normals correct
- UVs present and named
- materials and textures named, paths resolvable
- units matching the destination

## Verify by importing

**An export is not verified until something else has opened it.** Re-import into Blender at
minimum; ideally open it in the actual destination application.

This catches scale, axis and material problems immediately, and it takes a minute.

## Common mistakes

- Exporting without applying scale
- Wrong axis convention
- Expecting materials to survive
- Not triangulating when the target requires it
- Absolute texture paths
- Never testing the export

## Related

[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]] ·
[[3D & Blender Knowledge/19 - Production Workflows/Export Discipline|Export Discipline]]

## Sources

Blender Manual (CC-BY-SA 4.0) - import/export operators and their options. Format trade-offs and
failure list are practitioner knowledge.
