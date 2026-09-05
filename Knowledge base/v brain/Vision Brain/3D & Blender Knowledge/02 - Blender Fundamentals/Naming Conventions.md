---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Naming Conventions

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

Naming is not tidiness. It is **addressability** - the ability to find, select, script against and
hand over work.

`Cube.014` costs nothing on a single object and makes a fifty-object scene unworkable.

## A convention that holds up

```
<type>_<subject>_<variant>_<lod>

SM_Chair_Oak_LOD0        static mesh
SK_Character_Male        skinned mesh
MAT_Wood_Oak_Rough
TEX_Wood_Oak_BaseColor
GN_Scatter_Grass         geometry node group
CAM_Hero_Exterior
LGT_Key
```

The exact scheme matters far less than using one consistently.

## What must be named

- **Objects** - the obvious one
- **Meshes** - the data-block, which is separate and usually left as the default. Scripts and
  exporters often read the mesh name rather than the object name.
- **Materials** - `Material.003` on a delivered asset is a defect
- **Node groups** - unnamed groups are unreusable
- **UV maps** - matters when an exporter expects a particular name
- **Collections** - the structure of the scene

## Why it matters for automation

Every script that touches a scene addresses things by name. Consistent naming turns a fragile
script into a robust one, and turns manual selection into a pattern match.

Note the documented Blender behaviour: **the name you request is not guaranteed**. Blender enforces
uniqueness, appending `.001`. Scripts must use the returned reference rather than looking up the
name they hoped for - see
[[3D & Blender Knowledge/17 - Python & Automation/Safe Scripting Practices|Safe Scripting Practices]].

## Common mistakes

- Naming objects but never their mesh data
- Renaming after the fact, breaking scripts and links that referenced the old name
- Spaces and punctuation in names destined for engines that dislike them
- Assuming a requested name was granted

## Related

[[3D & Blender Knowledge/19 - Production Workflows/Scene Hygiene|Scene Hygiene]] ·
[[3D & Blender Knowledge/17 - Python & Automation/Safe Scripting Practices|Safe Scripting Practices]]

## Sources

Naming schemes are practitioner convention. The name-uniqueness behaviour is documented in the
Blender Python API documentation (docs.blender.org/api, *Gotchas*).
