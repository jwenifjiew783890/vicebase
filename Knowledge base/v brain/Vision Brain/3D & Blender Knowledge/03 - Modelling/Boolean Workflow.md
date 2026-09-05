---
type: note
domain: 3D & Blender Knowledge
section: 03 - Modelling
created: 2026-09-03
---

# Boolean Workflow

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/03 - Modelling/00 - Modelling|Modelling]]

## What it is

Combining or cutting volumes - union, difference, intersect. Enormously faster than modelling a
complex intersection by hand, and it produces topology you must then decide whether to care about.

## The trade

Booleans give you the shape immediately and hand you n-gons, long thin triangles and inconsistent
edge flow. Whether that matters depends entirely on what happens next:

| Next step | Boolean output |
| --- | --- |
| Static prop, flat shaded, never subdivided | Fine as is |
| Subdivision | Must be cleaned up, or it will pinch |
| Deformation or rigging | Must be cleaned up |
| Baking normals from high to low | Usually fine on the high-poly |
| 3D print | Fine if manifold |

## Preconditions

Booleans fail on bad input, and the failure looks like a Blender bug when it is a mesh problem:

- **Both meshes must be manifold.** Open surfaces have no interior, so difference is undefined.
- **Normals must be correct.** Inverted normals invert what counts as inside.
- **Avoid exactly coplanar faces.** Two faces at precisely the same position produce z-fighting in
  the solver. Offset by a tiny amount.
- **Apply scale first.**

Most "the boolean did nothing" or "the boolean produced garbage" reports are one of these four.

## Workflow

1. Build the cutter as a clean, closed, manifold volume.
2. Keep cutters in a dedicated collection, hidden, named as cutters.
3. Add the Boolean modifier - keep it **live** as long as possible so the cut stays editable.
4. Apply only when necessary, then immediately: Merge by Distance, recalculate normals, and
   inspect the result in wireframe.
5. If subdividing afterwards, add supporting geometry around the cut.

## Cleanup after applying

- Merge by Distance
- Recalculate normals outside
- Look for long thin triangles and coplanar leftovers
- Add support loops around the cut if subdivision follows

## Common mistakes

- Boolean on non-manifold input, then blaming the modifier
- Applying immediately, losing the ability to move the cut
- Coplanar faces producing flickering, unstable results
- Subdividing boolean output without cleanup, producing pinching along every cut
- Cutter objects left visible in the render

## Related

[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Boolean Failures|Boolean Failures]] ·
[[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface|Hard Surface]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Boolean modifier and solver behaviour. Preconditions and cleanup
sequence are practitioner judgement grounded in that behaviour.
