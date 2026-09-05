---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Boolean Failures

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

A boolean produces holes, garbage geometry, no
change at all, or flickering surfaces.

## Likely causes

1. **Non-manifold input** on either mesh - difference is undefined on an open surface
2. **Inverted normals**, which invert what counts as inside
3. **Exactly coplanar faces** between the two meshes, producing solver ambiguity
4. **Unapplied scale** on either object
5. **Zero-thickness geometry** used as a cutter
6. **Overlapping or self-intersecting** geometry within one of the meshes
7. **Fast solver** on geometry that needs the exact solver

## Diagnosis

1. Check both meshes with **Select > All by Trait > Non Manifold**
2. **Face Orientation** on both
3. Check **scale** on both
4. Look for coplanar surfaces - do any faces sit at exactly the same position?
5. Switch the solver from Fast to **Exact** and see whether the result changes
6. Try the boolean on a **simple primitive** cutter to establish whether the cutter or the target
   is at fault

## Evidence to collect

- Non-manifold selection counts on both meshes
- Face Orientation state
- Scale values
- Whether a simple primitive cutter works where the real one does not

## Safest fix

- Close the mesh - fill holes, remove interior faces, remove loose geometry
- Recalculate normals on both
- **Offset one mesh very slightly** to remove exact coplanarity
- Apply scale
- Give a zero-thickness cutter real thickness with Solidify
- Use the Exact solver for precise geometry

## Verification

Inspect the result in **wireframe and Edit Mode**, not just the shaded viewport. Boolean damage is
often hidden by shading. Check for:

- long thin triangles along the cut
- doubled vertices
- interior faces left behind

Then Merge by Distance and recalculate normals.

## Common mistakes

- Blaming the modifier when the input mesh is at fault
- Applying immediately, so the cut cannot be adjusted
- Subdividing boolean output without cleanup, producing pinching along every cut
- Leaving cutter objects visible in the render

## Prevention

Keep cutters clean, closed, simple and in a dedicated hidden collection. Keep the boolean live as
long as possible.

## Related

[[3D & Blender Knowledge/03 - Modelling/Boolean Workflow|Boolean Workflow]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Boolean modifier and solvers. Failure attribution is practitioner
synthesis.
