---
type: note
domain: 3D & Blender Knowledge
section: 19 - Production Workflows
created: 2026-09-03
---

# Scene Hygiene

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/19 - Production Workflows/00 - Production Workflows|Production Workflows]]

## What it is

Keeping a file in a state where someone else - or you in a month - can work with it.

## The habits

- **Name as you create.** Renaming later is a chore that never happens. `Cube.014` is a defect the
  moment there are twenty objects.
- **Collections by role**, not creation order
- **Apply scale** as a routine step
- **Purge orphan data** before handing over or archiving
- **Delete what is genuinely dead.** A `99_Trash` collection excluded from render is fine for
  things you might want back; keeping everything forever is not.
- **One material per surface type**, reused - not forty near-identical materials
- **Origins deliberate**
- **Reference and blockout geometry** in a clearly named collection, excluded from render

## Why it matters more than it seems

A tidy scene is not aesthetics. It is:

- **Speed** - finding things instantly rather than hunting
- **Scriptability** - automation addresses things by name
- **Handover** - someone else can pick it up
- **Debuggability** - a clean scene makes anomalies obvious
- **Performance** - purged, instanced, organised scenes are lighter

## The handover test

**Could someone else open this file and work on it without asking questions?**

If not, the file is not finished, whatever the render looks like. This is the standard that
separates professional work from personal work.

Practical version: could *you* pick it up in three months?

## Cleanup before delivery

- purge orphan data
- pack or relink textures
- delete or clearly mark work-in-progress geometry
- verify names
- save a clean final version separate from the working file

## Common mistakes

- Leaving naming until "later"
- Forty materials that should have been four
- Reference geometry left in the render
- Never purging, producing an enormous file
- Handing over a file only the author can navigate

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Naming Conventions|Naming Conventions]] ·
[[3D & Blender Knowledge/02 - Blender Fundamentals/Collections & Scene Organisation|Collections & Scene Organisation]]

## Sources

Practitioner synthesis - standard studio practice.
