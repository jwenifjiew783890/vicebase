---
type: note
domain: 3D & Blender Knowledge
section: 19 - Production Workflows
created: 2026-09-03
---

# Asset Pipeline

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/19 - Production Workflows/00 - Production Workflows|Production Workflows]]

## What it is

The structure that separates source material from working files from delivered outputs, so that
each can change without corrupting the others.

## The separation that matters

```
project/
  00_reference/      briefs, drawings, photographs
  01_source/         source assets: sculpts, high-poly, raw scans
  02_working/        the .blend files being worked in
  03_textures/       texture maps
  04_cache/          simulation and geometry caches (regenerable)
  05_output/         renders and exports (regenerable)
```

The principle: **regenerable things live apart from irreplaceable things.** Caches and renders can
be rebuilt; source and working files cannot. That distinction decides what must be backed up and
what can be deleted freely.

## Source versus working versus output

- **Source** - the highest-quality original. A multi-million-polygon sculpt, a raw scan. Never
  modified destructively.
- **Working** - what you actually open and edit. May reference source by linking.
- **Output** - renders, exports, deliverables. **Always regenerable, never edited by hand.**

Editing an output is how a deliverable stops matching its source, and it is very hard to recover
from.

## Linking for reuse

A shared asset - a chair used in five scenes - should live in its own file and be **linked**, not
appended into each. Fix it once, and every scene updates. See
[[3D & Blender Knowledge/02 - Blender Fundamentals/Linking, Appending & Assets|Linking, Appending & Assets]].

This is what makes a pipeline rather than a folder of files.

## Relative paths

Use them throughout. A project with absolute paths cannot be moved, archived or shared, and this is
discovered at the worst moment.

## Scaling to a team

Everything above matters more with more people. Additionally: a naming convention agreed in
advance, an asset library everyone draws from, and clarity about who owns which file at which time.

## Common mistakes

- One folder with everything in it
- Outputs edited by hand, diverging from source
- Absolute paths
- Assets appended into every scene, so fixes must be repeated
- Caches backed up as though they were irreplaceable
- No separation between source and working, so the source gets modified destructively

## Related

[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Asset Libraries|Asset Libraries]] ·
[[3D & Blender Knowledge/19 - Production Workflows/Versioning & Backups|Versioning & Backups]]

## Sources

Practitioner synthesis - standard pipeline practice.
