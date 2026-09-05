---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Performance & Memory Problems

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

The viewport is
unusable, the render takes far too long, or Blender runs out of memory.

## Likely causes

1. **Subdivision viewport levels** too high across many objects
2. **Duplicated rather than instanced** geometry
3. **Realised instances** in geometry nodes
4. **High-resolution textures** beyond what the image resolves
5. **Live simulation caches**
6. **Booleans on dense meshes**, re-evaluating constantly
7. **Volumetrics**
8. **Too many objects** - object count itself has overhead independent of polygon count

## Diagnosis

**Measure before optimising.** The bottleneck is usually not where it feels like it is.

1. **Statistics overlay** - objects, vertices, faces. An unexpected number points straight at the
   cause.
2. Disable collections one at a time and watch responsiveness - this isolates the offender in
   seconds.
3. For render time, eliminate by category: bounces, volumetrics, subdivision, textures, samples -
   in that order.
4. Watch memory. A fallback from GPU to CPU explains many "suddenly slow" reports.

## Evidence to collect

- Statistics overlay figures
- Which collection, when disabled, restores responsiveness
- Peak memory usage
- Render time change per category disabled

## Safest fix

| Cause | Fix |
| --- | --- |
| Subdivision | Reduce viewport levels; use Simplify for a global cap |
| Duplicates | Convert to linked duplicates or collection instances |
| Realised instances | Keep them instanced |
| Textures | Reduce resolution to match screen coverage; Simplify texture limit |
| Simulation | Bake, then disable live evaluation |
| Working set too large | Exclude collections not currently being worked on |

**Collection exclusion is the highest-value, lowest-effort lever** and is consistently
under-used.

## Verification

Re-measure. An optimisation that was not measured before and after is a guess.

## Common mistakes

- Optimising the render when the viewport was the problem, or the reverse
- Reducing quality globally rather than finding the one heavy object
- Not noticing GPU-to-CPU fallback
- Optimising past the point of usefulness

## Prevention

Instance from the start. Keep viewport subdivision low as a habit. Budget texture resolution
against screen coverage.

## Related

[[3D & Blender Knowledge/15 - Optimization & Performance/Scene Weight|Scene Weight]] ·
[[3D & Blender Knowledge/15 - Optimization & Performance/VRAM & Memory|VRAM & Memory]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Simplify, instancing, statistics, device settings.
