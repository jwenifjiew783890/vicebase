---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Collections & Scene Organisation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

Collections group objects. They nest, can be linked into several scenes, and carry visibility and
render flags of their own.

## Structure by role, not by accident

A scene organised by creation order becomes unusable at about fifty objects. Organise by what
things *are*:

```
Scene
  01_Camera
  02_Lighting
  03_Set          walls, floor, structural
  04_Props        furniture, dressing
  05_Vegetation
  06_Reference    blockouts, dimension guides  (excluded from render)
  99_Trash        kept but not shipped
```

Numeric prefixes force useful ordering in the Outliner.

## The three kinds of hiding

This causes constant confusion, because they behave differently:

| Control | Effect | Survives file reload |
| --- | --- | --- |
| Hide in viewport (H, the eye) | Temporary visibility only | No |
| Disable in viewport (the monitor icon) | Excluded from viewport evaluation | Yes |
| Disable in render (the camera icon) | Excluded from render only | Yes |
| Exclude from view layer (the checkbox) | Removed from the layer entirely | Yes |

**"Visible in viewport, missing in render" is almost always the render toggle or view-layer
exclusion.** It is the single most common false bug in Blender.

## Collection instancing

An empty can instance a whole collection. Change the source collection, and every instance updates.
This is the correct mechanism for repeated set pieces - trees, chairs, modular wall sections - and
it costs a fraction of duplicating geometry.

## Common mistakes

- One flat collection with two hundred objects
- Hiding with H and then not understanding why the render still shows the object
- Reference and blockout geometry left enabled in render
- Collection names that describe nothing

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Naming Conventions|Naming Conventions]] ·
[[3D & Blender Knowledge/13 - Environment & Scene Design/Modular Kits|Modular Kits]]

## Sources

Blender Manual (CC-BY-SA 4.0) - collections, view layers, visibility controls and instancing.
