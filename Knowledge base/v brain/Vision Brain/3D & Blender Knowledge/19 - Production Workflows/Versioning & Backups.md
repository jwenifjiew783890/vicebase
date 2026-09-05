---
type: note
domain: 3D & Blender Knowledge
section: 19 - Production Workflows
created: 2026-09-03
---

# Versioning & Backups

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/19 - Production Workflows/00 - Production Workflows|Production Workflows]]

## What it is

Keeping recoverable history. The cheapest insurance available, and the habit whose absence causes
the worst days.

## Incremental saves

**Save a new version at every meaningful milestone**, not just at the end of the day.

`project_v001.blend`, `project_v002.blend`, and so on. Blender's Save Incremental does this
automatically.

Save a new version before:

- applying anything destructive
- major structural changes
- running a script that modifies the scene
- experimenting with something that might not work
- long renders
- handing the file to anyone

**Disk is cheaper than rework.** A project directory with thirty versions is not untidy; it is
insured.

## Backups Blender provides

| Mechanism | What it gives |
| --- | --- |
| **`.blend1`** | The previous save, written automatically each save |
| **Auto Save** | Periodic save to the temp directory - check the interval |
| **Quit file** | Recover Last Session, including after a crash |

These are safety nets, not a strategy. They protect against crashes, not against "I made this
worse over three hours and want yesterday's version".

## What to back up

The `.blend` alone is often insufficient:

- textures, if not packed
- simulation caches, if expensive to regenerate
- reference material
- exported outputs
- any scripts

Back up the **project directory**.

## Naming versions

Sequential numbers are unambiguous and sort correctly. Dates are useful but do not convey order
within a day. Descriptive suffixes help at milestones - `project_v012_lighting_approved.blend`.

Avoid `final`, `final2`, `final_real`. Everyone has lived through this and it never ends well.

## Common mistakes

- Working in one file for days
- Overwriting the good version with a broken one
- Backing up the .blend but not the textures
- Deleting `.blend1` files as clutter
- Not knowing the autosave interval
- `final_v2_actually_final.blend`

## Related

[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/File Corruption & Recovery|File Corruption & Recovery]]

## Sources

Blender Manual (CC-BY-SA 4.0) - save versions, auto save, recovery. Versioning discipline is
standard practice.
