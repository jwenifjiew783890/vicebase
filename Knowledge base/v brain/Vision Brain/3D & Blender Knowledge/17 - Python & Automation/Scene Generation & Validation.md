---
type: note
domain: 3D & Blender Knowledge
section: 17 - Python & Automation
created: 2026-09-03
---

# Scene Generation & Validation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation|Python & Automation]]

## What it is

Building geometry and scenes from code, and - the part usually missing - proving the result is
correct.

## Generating geometry

Two levels:

**`bpy.data.meshes` with `from_pydata`** - build from vertex, edge and face lists. Simple, fast,
good for parametric primitives.

```python
mesh = bpy.data.meshes.new("Panel")
mesh.from_pydata(verts, edges, faces)
mesh.update()
mesh.validate()          # catches malformed geometry before it enters the scene
```

`mesh.validate()` is worth calling on any generated mesh. It removes invalid geometry that would
otherwise cause confusing failures later.

**`bmesh`** - for operations needing topology awareness: extrude, bevel, subdivide, boolean. More
capable, more code.

## Why generated scenes need validation

A script that runs without error has not necessarily produced a correct scene. Generated geometry
fails in ways that are silent:

- degenerate or zero-area faces
- inverted normals
- doubled vertices at shared boundaries
- objects created but never linked
- transforms applied to the object when the mesh was meant to change
- non-manifold results from programmatic booleans

**"The script completed" is not evidence of a correct scene.** This is the same discipline as
[[Coding Knowledge/02 - Debugging Method|verifying by execution rather than by inspection]].

## A validation pass

For any generated scene, check programmatically:

| Check | How |
| --- | --- |
| Object exists and is linked | present in the intended collection |
| Geometry non-empty | vertex and polygon counts greater than zero |
| No loose or degenerate geometry | `mesh.validate()` reported no changes |
| Normals consistent | check for inverted faces, or recalculate deliberately |
| Transforms clean | scale is 1,1,1 if it should be |
| Dimensions as intended | compare `obj.dimensions` against the specification |
| Materials assigned | material slots populated as expected |
| Names as expected | compare against the returned references, not assumptions |

Return a **report**, not just a success flag. A generator that says "created 14 objects, all
dimensions within tolerance, no degenerate geometry" is trustworthy; one that says "done" is not.

## Determinism

- Seed any randomness explicitly, so a scene can be regenerated identically
- Avoid depending on selection or active object
- Avoid depending on the state a previous run left behind

## Batch processing

```
blender --background --python script.py -- arg1 arg2
```

Arguments after `--` are passed to the script. For processing many files, run one Blender process
per file rather than looping inside one - a crash then costs one file, not the batch.

## Common mistakes

- Treating "no exception" as success
- No dimension check, so a scale error propagates silently
- Non-deterministic generation that cannot be reproduced
- Creating data without linking
- One long-running process for a whole batch, losing everything on a crash
- No `mesh.validate()` on generated geometry

## Related

[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]] ·
[[3D & Blender Knowledge/17 - Python & Automation/Safe Scripting Practices|Safe Scripting Practices]]

## Sources

Blender Python API documentation (docs.blender.org/api) - mesh creation, `from_pydata`,
`validate`, bmesh, command-line arguments. The validation discipline is practitioner judgement,
consistent with the verification standard used elsewhere in this vault.
