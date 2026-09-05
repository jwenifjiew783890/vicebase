---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Shading Artifacts

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

Blotchy patches, dark regions, smeared edges, or
a surface that looks inside-out.

## Likely causes

1. **Flipped normals** - by a wide margin the most common
2. **Non-uniform object scale** - distorts shading and bevel width
3. **Custom split normals** overriding everything else
4. **Doubled vertices** splitting the surface invisibly
5. **Bevel without Weighted Normal**, smearing shading near edges
6. **Smooth shading with no angle threshold** on hard-surface geometry
7. **N-gons or triangles** in a subdivision cage, pinching
8. **Overlapping coplanar faces** producing z-fighting

## Diagnosis

Work in this order - each is faster than the next:

1. **Face Orientation overlay.** Red is inward. This alone resolves most cases.
2. **N panel - check scale.** Not 1,1,1 means apply scale.
3. **Object Data Properties** - does the mesh carry custom split normals?
4. **Merge by Distance** and watch the vertex count. A drop means doubles existed.
5. **Wireframe view** - look for hidden interior faces and coplanar overlaps.
6. Toggle the Bevel and Subdivision modifiers to see which introduces the artefact.

## Evidence to collect

- Face Orientation screenshot
- Object scale values
- Vertex count before and after Merge by Distance
- Whether the artefact exists with all modifiers disabled

## Safest fix

- Flipped normals: Edit Mode, select all, Recalculate Outside. **If the result is still wrong the
  mesh is non-manifold** - fix topology first.
- Scale: apply it
- Custom split normals: clear them, unless they were deliberate
- Doubles: Merge by Distance
- Bevel smearing: add a Weighted Normal modifier after the Bevel
- Hard surface: use smooth-by-angle rather than blanket smooth shading

## Verification

Look at the surface under a **moving light or a rotating HDRI**. Static lighting hides shading
faults; moving light reveals them immediately. Then confirm in a render, not the viewport.

## Common mistakes

- Debugging in the shader editor when the cause is geometry
- Recalculating normals on non-manifold geometry and trusting it
- Applying smooth shading to hide a topology problem
- Fixing the symptom on one face while the cause affects the whole object

## Prevention

Check Face Orientation and apply scale as routine steps before shading work - both are in
[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]].

## Sources

Blender Manual (CC-BY-SA 4.0) for normals, overlays and modifiers. Diagnostic ordering is
practitioner judgement.
