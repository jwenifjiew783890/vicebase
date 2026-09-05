---
type: note
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# Blender Engineering Constraints

Documented Blender behaviour that changes what you should do. Not opinions — these are
properties of the software, and working against them wastes time reliably.

## Transforms

**Object scale and mesh scale are different things.** Scaling in Object Mode changes the object's
scale factor; the mesh data is unchanged. Almost everything downstream reads the *mesh*, so a
non-uniform object scale silently corrupts:

- **Bevel widths** — inconsistent across axes
- **Modifier offsets** — array spacing, solidify thickness
- **Physics** — collision shapes and mass behave nonsensically
- **Exported geometry** — the receiving application may or may not honour the factor
- **UV distortion** on subsequent unwraps

`Ctrl+A → Scale` writes the scale into the mesh and resets the factor to 1. **Do this before
bevelling, before physics, before export.** If a bevel looks uneven for no reason, check the
scale first — it is the cause more often than the bevel settings.

**Origin is not centre of mass.** The origin is the object's pivot for rotation, scaling and
placement. A door hinged at its centre rotates wrongly; move the origin to the hinge.

## Normals

Normals define which way a face points, and therefore how it is lit. Blender renders backfaces,
so a flipped normal is not invisible — it is *subtly wrong shading* that reads as a material
problem.

- Recalculate outside: Edit Mode → `Shift+N`
- Diagnose visually: Overlays → Face Orientation. Blue is outward, **red is inward**.
- **Non-manifold geometry breaks normal calculation**, because "outside" is undefined. Fix
  topology first, then recalculate.

Flipped normals also break booleans, solidify and 3D printing. When several things are wrong at
once, check normals before anything else — one cause, many symptoms.

## Modifiers

**The stack is evaluated top to bottom, and order changes the result.** This is not a subtlety;
it is usually the whole problem.

| Order | Result |
| --- | --- |
| Mirror → Subdivision | Halves join smoothly across the seam. Correct. |
| Subdivision → Mirror | Each half is smoothed independently, then duplicated — a visible seam. |
| Bevel → Subdivision | Bevel produces the sharp edge, subdivision smooths the rest. Correct for hard surface. |
| Subdivision → Bevel | Bevels the already-dense smoothed mesh. Usually wrong and very heavy. |

General rule: **generate geometry first, then smooth; deform last.**

Modifiers are non-destructive until applied. Applying is one-way — the stack is gone.

## Mesh topology

- **Quads subdivide predictably. Triangles and n-gons do not.** Subdivision of a triangle
  produces pinching; of an n-gon, unpredictable flow.
- **N-gons are acceptable on flat, static, non-subdivided surfaces** and nowhere else. This is
  the pragmatic position: flat panel with a 7-sided face that never deforms is fine.
- **Poles** (vertices where 3, 5 or more edges meet) are unavoidable; place them in flat regions
  where the shading artefact they cause is invisible, not on a curved silhouette.
- **Deformation needs edge loops where the bend is.** A limb with no loops at the joint cannot
  bend cleanly no matter how good the rig is.

## Render engines

| | Cycles | EEVEE |
| --- | --- | --- |
| Method | Path tracing — physically based light simulation | Rasterisation — real-time approximation |
| Strength | Physical accuracy, true reflection/refraction/GI | Speed, iteration, look-development |
| Cost | Time, and noise that must be resolved | Approximations that must be worked around |
| Use for | Final stills, archviz, anything where light realism carries the image | Previews, animation where speed dominates, stylised work |

They are **not interchangeable and a scene lit for one is not lit for the other.** Materials
mostly transfer; lighting behaviour does not.

## Cycles specifics

- **Noise is variance, not error.** More samples reduce it as the square root — 4× the samples
  for half the noise. Diminishing returns are steep.
- **Denoising is the practical answer**, not brute-force sampling. Denoise, then add samples only
  if the denoiser is smearing detail.
- **Fireflies** (single bright pixels) come from small, intense light sources reached by
  improbable paths. Clamping indirect light kills them, at the cost of some energy.
- **Light bounces** cost time. Interior scenes need more; a product on a backdrop needs few.

## Python API — documented constraints

From Blender's official Python API documentation:

- **Python threads are not supported.** They cause crashes that are hard to diagnose, including
  during Cycles renders. Threads only work if they finish before the script does (joined while
  the main thread is blocked). Use `multiprocessing` for independent work.
- **`bpy.ops` operators depend on context** and cannot take data arguments — they act on whatever
  the context selects. `poll() failed, context is incorrect` means the operator was called from
  a state it does not accept. Prefer direct data access (`bpy.data`) where an equivalent exists.
- **Python objects wrapping Blender data have limited lifetime.** Storing them persistently can
  lead to invalid memory access. Do not keep references across operations that may free the
  underlying data.
- **Newly created data may not receive the name you requested** — Blender enforces uniqueness and
  length limits. Never assume `bpy.data.objects["MyName"]` will exist after creating "MyName";
  use the returned reference.

## Files and scenes

- **Linked vs appended:** linking keeps a live reference to the source file (updates propagate,
  data is not editable locally); appending copies the data in (editable, no longer tracks the
  source). Choose deliberately — a library of linked assets is maintainable; a scene of appended
  copies is not.
- **Orphaned data persists** until the file is saved and reloaded, or purged. A file that keeps
  growing usually holds unused meshes, materials and images.
- **`.blend1` backups** are written on save if enabled. They are the cheapest recovery path from
  a corrupted or wrongly-overwritten file.

## Related

[[3D & Blender Knowledge/04 - Debugging Method (3D)|Debugging Method]] ·
[[3D & Blender Knowledge/01 - Modelling Method|Modelling Method]] ·
[[3D & Blender Knowledge/05 - Failure Patterns (3D)|Failure Patterns]]

## Sources

- Blender Manual (docs.blender.org/manual, CC-BY-SA 4.0) — transforms, modifiers, normals,
  render engines, linking and appending.
- Blender Python API documentation (docs.blender.org/api) — *Gotchas*: threading, operators,
  internal data lifetime, data-name limitations. These four are documented behaviour, quoted in
  substance and not verbatim.
- Modifier-order consequences and the topology positions are practitioner synthesis consistent
  with that documented behaviour.
