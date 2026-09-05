---
type: note
domain: 3D & Blender Knowledge
section: 16 - Add-ons & Pipelines
created: 2026-09-03
---

# Asset Libraries

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/16 - Add-ons & Pipelines/00 - Add-ons & Pipelines|Add-ons & Pipelines]]

## What it is

A structured collection of reusable data - objects, materials, node groups, world settings -
available across projects through the Asset Browser.

## Why it matters

Without one, reuse means remembering which file contained the good concrete material and appending
from it. That does not scale, and it means quality work is effectively lost.

## Setting up

1. Designate one or more **asset library folders** in preferences
2. Mark data-blocks as assets, with previews
3. Organise with **catalogues** - a hierarchy independent of file structure
4. Tag assets so they are findable by property, not just name

## What is worth marking

| Type | Value |
| --- | --- |
| **Materials** | Very high - a good material is reusable almost everywhere |
| **Node groups** | Very high, especially geometry-node tools |
| **Props and furniture** | High for repeated set dressing |
| **World / HDRI setups** | High - a known-good lighting start |
| **Modular kit pieces** | High |
| **Poses and rigs** | Useful for character work |

## Link versus append from a library

Appending copies the asset in - it becomes editable and independent. Linking keeps it live, so
fixing the source fixes every use.

For a library you maintain, **linking is usually right**, with library overrides where local
adjustment is needed. See
[[3D & Blender Knowledge/02 - Blender Fundamentals/Linking, Appending & Assets|Linking, Appending & Assets]].

## Maintenance

A library only stays useful if it is curated:

- previews that actually show the asset
- consistent naming
- assets at correct real-world scale, with scale applied
- textures packed or on reliable relative paths
- removing what turned out not to be good

**An asset at the wrong scale is worse than no asset**, because it silently contaminates every
scene it enters.

## Common mistakes

- Never setting one up, and appending from old project files forever
- Assets with no previews, so the browser is unusable
- Inconsistent scale across the library
- Broken texture paths once the library moves
- Marking everything, so nothing is findable

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Linking, Appending & Assets|Linking, Appending & Assets]] ·
[[3D & Blender Knowledge/19 - Production Workflows/Asset Pipeline|Asset Pipeline]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Asset Browser, asset libraries, catalogues and marking. Curation
guidance is practitioner judgement.
