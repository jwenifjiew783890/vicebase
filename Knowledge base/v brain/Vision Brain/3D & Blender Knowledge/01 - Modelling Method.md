---
type: note
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# Modelling Method

The order of operations for any 3D task. Read this before starting one.

The single most expensive mistake in 3D is **starting to model before deciding what is being
made**. Everything below exists to delay geometry until the cheap decisions have been made.

## The sequence

```
requirement → reference → blockout → technical plan → model
           → materials → lighting → camera → validate → render → review → export
```

Each stage is cheap to change and expensive to skip. A camera angle chosen after the model is
finished dictates that the model was detailed in the wrong places.

### 1. Requirement — what is this for?

The answer changes everything downstream:

| Purpose | Consequence |
| --- | --- |
| Single hero render | Detail only what the camera sees. Topology barely matters. |
| Animation | Topology matters enormously — deformation needs edge loops in the right places. |
| Game asset | Polygon budget, UV layout and baking are constraints, not afterthoughts. |
| 3D print | Manifold geometry, wall thickness and real-world scale are pass/fail. |
| Architectural viz | Real scale is non-negotiable; materials and lighting carry the image. |

**Ask what the final output is before opening Blender.** A model that is right for one of these
is wrong for the others.

### 2. Reference — never model from memory

Gather reference *first*, including orthographic views where the object is man-made and
dimensioned drawings where accuracy matters. Modelling from memory produces objects that look
subtly wrong in ways nobody can name.

For anything real, find the actual dimensions. A door is ~2.0 m tall; a chair seat ~0.45 m. Scale
errors are invisible in isolation and glaring in a scene.

### 3. Blockout — establish proportion and scale before detail

Build the silhouette in primitives at correct real-world dimensions. Judge it from the intended
camera angle. Fix proportion *here*, where it costs nothing.

> A detailed model with wrong proportions is worth less than a blockout with right ones.

### 4. Technical plan — decide before building

Decide, and write down if the object is non-trivial:

- **Topology strategy** — subdivision, or flat-shaded hard surface, or sculpt-then-retopologise?
- **Modifier stack** — what stays procedural (non-destructive) and what gets applied, and when?
- **Symmetry** — mirror from the start, or build both sides?
- **Modularity** — is this one object, or a kit of reusable parts?
- **Scale and units** — set the scene units before the first vertex.

### 5. Model — detail last, and only where it is seen

Work coarse to fine. Detail that the camera never resolves is wasted time and wasted memory.

## Choosing a modelling technique

The recurring decision, resolved by what the object *is*:

| The object is | Use | Because |
| --- | --- | --- |
| Smooth, curved, organic | Subdivision surface | Smooth curvature is what subdivision produces naturally |
| Mechanical with sharp edges | Poly modelling + bevel, flat shading | Bevels catch light; subdivision fights hard edges |
| Repetitive or parametric | Geometry Nodes / array + curve modifiers | Change one parameter, not two hundred vertices |
| Complex organic form | Sculpt, then retopologise | Sculpting finds the form; retopology makes it usable |
| Cut-away, panel lines, holes | Booleans + cleanup | Faster than manual topology, but the cleanup is the job |
| Architectural | Precise poly modelling to real dimensions | Accuracy dominates; the geometry is mostly planar |

**When not to use subdivision:** on a mechanical object with mostly flat faces and sharp edges.
You will spend the whole time adding support loops to fight the smoothing. Flat shading plus a
bevel modifier gets there faster and reads better.

**When not to use booleans:** when the resulting topology must deform or subdivide. Booleans
produce n-gons and inconsistent edge flow, which is fine on a static prop and fatal on anything
that bends.

**When not to sculpt:** when the form is describable in dimensions. Sculpting a bolt is slower
and worse than modelling one.

## Non-destructive by default

Keep operations live in the modifier stack as long as possible — mirror, array, bevel,
subdivision, boolean. Applying a modifier converts a decision you can revise into geometry you
must rebuild.

Apply only when you must: before exporting, before sculpting on the result, or when the stack
has become slower to evaluate than the frozen geometry is to edit.

## Validation gates

Do not proceed past a stage with a known defect. The checks belong to
[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]], but the two
that catch the most damage early:

- **Apply scale** (`Ctrl+A`) before bevelling, before physics, before export. Non-uniform object
  scale makes bevel widths inconsistent and physics behave nonsensically.
- **Check normals** before shading looks final. Flipped normals masquerade as material bugs and
  waste hours in the shader editor.

## Common mistakes

- **Detailing before blockout.** The most common and most expensive.
- **Modelling at the wrong scale**, then scaling the object rather than the mesh — leaving a
  non-uniform object scale that corrupts every downstream operation.
- **Applying modifiers early** to "see it properly", destroying revisability.
- **Perfecting geometry the camera never sees.**
- **Deferring UVs** on anything that needs textures. Retrofitting UVs onto finished dense
  geometry is far worse than unwrapping as you go.
- **No reference**, then discovering the proportions are wrong after detailing.

## Related

[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]] ·
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]] ·
[[3D & Blender Knowledge/05 - Failure Patterns (3D)|Failure Patterns]]

## Sources

Practitioner synthesis. The technique-selection table and the non-destructive discipline are
standard practice across production 3D work rather than any single documented source; the
apply-scale and normals gates are consequences of documented Blender behaviour — see
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]].
