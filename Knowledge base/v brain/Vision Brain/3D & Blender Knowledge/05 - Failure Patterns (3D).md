---
type: note
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# Failure Patterns (3D)

Ways 3D work goes wrong that are worth recognising *before* committing to an approach. Each is a
pattern people repeat, not a one-off bug.

## Process failures

**Detailing before blockout.** The dominant time-waster. Proportion errors surface after the
detail is in, and fixing them means redoing the detail. Blockout is cheap precisely because it is
crude.

**No reference.** Modelling from memory produces objects that are subtly wrong in ways no one can
articulate but everyone can see. For man-made objects, also gather *dimensions* — not just images.

**Modelling for the wrong output.** Animation-grade topology on a static hero render is wasted;
render-grade topology on a rig is a disaster. Decide the purpose first.

**Perfecting invisible geometry.** Detail the camera never resolves costs modelling time, memory
and render time, and returns nothing.

**Rebuilding instead of diagnosing.** Faster in the moment, and it hides a cause that recurs. If
something broke, find out why before deleting it.

## Transform failures

**The unapplied scale.** Non-uniform object scale corrupts bevels, arrays, solidify, physics and
export — each producing a symptom that looks like a fault in *that* feature. When several
unrelated things misbehave at once, check scale first.

**Scaling in Object Mode to fix proportion**, then never applying. Same cause, delayed damage.

**Origin wherever it landed.** An object that rotates about the wrong point cannot be placed or
animated sensibly. Set origins deliberately, especially on doors, wheels, hinges and modular
pieces.

## Topology failures

**N-gons on curved or deforming surfaces.** Fine on a flat static panel; a source of pinching and
unpredictable subdivision anywhere else.

**Triangles in a subdivision cage.** Subdivision of a triangle pinches. If the surface must be
smooth, make it quads.

**Poles on the silhouette.** Poles are unavoidable; a pole on a visible curved edge produces a
shading artefact exactly where it will be seen. Hide them in flat regions.

**No edge loops at joints**, then discovering the mesh cannot deform. Topology for deformation is
decided during modelling, not during rigging.

**Boolean output left uncleaned.** Booleans produce n-gons and stray vertices. On a static prop
that is acceptable; on anything subdivided or deformed it is a defect that surfaces later.

## Shading and material failures

**Flipped normals diagnosed as a material bug.** The symptom appears in shading, so the search
starts in the shader editor and the cause is in the mesh. Check Face Orientation first.

**Wrong colour space on data maps.** Roughness, metallic and normal maps must be **Non-Color**.
Loaded as sRGB they are subtly wrong everywhere, and the error is invisible until compared
against a correct render.

**Roughness at 0 or 1.** Almost no real material is perfectly smooth or perfectly diffuse. Values
at the extremes read as computer-generated.

**Intermediate metallic.** Metallic is a binary physical property: conductor or dielectric. Values
between 0 and 1 are for transitional surfaces (dust on metal), not a "slightly metallic" look.

**Fighting a lighting problem in the shader.** If the material looks dead, check whether light is
reaching it before adjusting the material.

## Lighting and render failures

**Fireflies treated with samples.** Bright single pixels come from small intense sources found by
improbable paths. More samples converges eventually and expensively; clamping indirect light or
enlarging the emitter fixes the cause.

**Noise treated with samples alone.** Noise falls with the square root of sample count — 4× the
render time to halve it. Denoise first; add samples only where the denoiser smears detail.

**Lighting a scene in EEVEE and rendering in Cycles.** They approximate light differently. The
lighting will be wrong, and the wrongness will be blamed on materials.

**Black render.** Almost always no light, or normals inverted, or the object is not in the view
layer — not a material fault.

**Render far slower than expected.** In order of likelihood: subdivision render levels,
volumetrics, excessive light bounces, an unnoticed runaway modifier.

## Scene and file failures

**Everything named `Cube.001`.** Costs nothing on a single object and makes a large scene
unworkable. Naming is not tidiness; it is addressability — including for scripts.

**Appended when linking was wanted.** A scene full of appended copies cannot be updated centrally.
Decide link-versus-append deliberately.

**The file that keeps growing.** Orphaned meshes, materials and images persist until purged.

**No incremental saves.** One corrupted file, or one destructive operation, and the day is gone.
`.blend1` backups are the minimum; incremental versions are better.

**Absolute texture paths**, then moving the file. Pack textures or use relative paths.

## Automation failures

**`bpy.ops` in a loop.** Operators depend on context and carry full-scene overhead; used per-item
they are slow and fragile. Prefer direct `bpy.data` manipulation.

**Assuming the requested name was granted.** Blender enforces uniqueness; the created object may
be `Thing.001`. Use the returned reference, never a name lookup you assumed.

**Python threads.** Officially unsupported and a documented cause of hard-to-diagnose crashes,
including during renders.

**Scripts that fail silently.** They did not fail silently — the traceback is in the System
Console, which is closed by default.

## Related

[[3D & Blender Knowledge/04 - Debugging Method (3D)|Debugging Method]] ·
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]] ·
[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]]

## Sources

Practitioner synthesis — these are recurring production failure modes rather than documented
behaviour. Where a pattern rests on documented behaviour (normals, transforms, operators,
threading, colour space) that behaviour is recorded in
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]]
with its source.
