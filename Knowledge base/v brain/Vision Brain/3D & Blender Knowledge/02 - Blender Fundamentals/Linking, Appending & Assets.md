---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Linking, Appending & Assets

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

Two ways to bring data from another .blend file, and they are not interchangeable.

| | Link | Append |
| --- | --- | --- |
| Relationship | Live reference to the source file | Copy into this file |
| Updates | Source changes propagate | Frozen at import |
| Editable locally | No (needs library override) | Yes |
| File size | Small | Grows with each copy |
| Use for | Shared assets, team pipelines, repeated set pieces | One-off imports, assets you will modify |

## Why linking matters

A scene of a hundred linked chairs updates when the chair file is fixed. A scene of a hundred
appended chairs requires fixing a hundred chairs. On any project lasting more than a day, this is
the difference between maintainable and not.

The cost: linked data is read-only locally. **Library overrides** let you pose or transform linked
data without breaking the link - the mechanism that makes linked character rigs usable.

## The Asset Browser

Marks data-blocks as assets with catalogues, previews and tags, drawn from a designated asset
library folder. It is the practical way to build a reusable component library rather than
remembering which file a good material lives in.

Worth marking as assets: materials, node groups, geometry-node setups, and any prop used more than
once.

## Relative versus absolute paths

Links and textures can be stored either way. **Relative paths survive moving the project;
absolute paths do not.** For anything shared or archived, use relative paths, or pack external
data into the .blend.

A missing texture after moving a project is almost always an absolute path.

## Common mistakes

- Appending what should have been linked, then maintaining copies
- Breaking links by reorganising folders after using absolute paths
- Linking a rig and then being unable to pose it, because no override was created
- Never packing textures, then archiving a file that cannot be reopened elsewhere

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Objects & Data|Objects & Data]] ·
[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Asset Libraries|Asset Libraries]]

## Sources

Blender Manual (CC-BY-SA 4.0) - linking, appending, library overrides, the Asset Browser and path
handling.
