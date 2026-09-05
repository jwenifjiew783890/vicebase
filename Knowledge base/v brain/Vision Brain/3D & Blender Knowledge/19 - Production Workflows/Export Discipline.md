---
type: note
domain: 3D & Blender Knowledge
section: 19 - Production Workflows
created: 2026-09-03
---

# Export Discipline

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/19 - Production Workflows/00 - Production Workflows|Production Workflows]]

## What it is

Getting work out of Blender correctly, the first time.

## Export is not finished until something else has opened it

The single most important rule here. An export that has not been imported somewhere is an
assumption, not a deliverable.

Minimum: re-import into a fresh Blender scene. Better: open it in the actual destination
application.

This takes a minute and catches scale errors, axis errors, missing materials and lost UVs
immediately - all of which are otherwise discovered by the recipient.

## Before exporting

Full list in [[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]]. The
ones that cause most failures:

1. **Apply scale.** Transforms clean.
2. **Modifiers** applied, or explicitly intended to travel
3. **Normals** correct; custom normals handled deliberately
4. **UVs** present and named as the destination expects
5. **Materials and textures** named, paths resolvable by the recipient
6. **Units** matching the destination's expectation
7. **Axis convention** - Blender is Z-up; the destination may not be
8. **Triangulation** if the target requires it - do it deliberately rather than letting the
   exporter decide

## Export only what is needed

Select deliberately and use Selected Only. Exporting the whole scene including reference geometry,
cameras and blockouts is a common and confusing error.

## Deliverable hygiene

- Consistent, meaningful filenames
- Version in the filename if iterations are expected
- Textures alongside, or packed, as agreed
- A short note of scale, units and axis convention - **this saves more time than anything else**
  when handing to another person or team

## Common mistakes

- Never test-importing
- Unapplied scale
- Wrong axis convention
- Expecting materials to survive intact
- Exporting the whole scene
- No note of units, so the recipient guesses

## Related

[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Import, Export & Interchange|Import, Export & Interchange]] ·
[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]]

## Sources

Practitioner synthesis. Format behaviour is documented in the Blender Manual (CC-BY-SA 4.0).
