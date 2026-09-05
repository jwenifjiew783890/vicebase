---
type: note
domain: 3D & Blender Knowledge
section: 15 - Optimization & Performance
created: 2026-09-03
---

# Scene Weight

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/15 - Optimization & Performance/00 - Optimization & Performance|Optimization & Performance]]

## What it is

Keeping the viewport responsive and the file manageable as a scene grows.

## Measure first

The statistics overlay shows objects, vertices and faces. **Check it before assuming.** A scene
that feels slow because of geometry is often slow because of a single high-subdivision object, or a
texture-heavy material, or a modifier evaluating on every frame.

## The main causes, in order

1. **Subdivision viewport levels** - level 3 on many objects is enormous. Reduce viewport levels;
   render levels are separate.
2. **Duplicated instead of instanced geometry** - the same object copied 200 times costs 200 times
   the memory. Linked duplicates or collection instances cost approximately once.
3. **Realised instances** in geometry nodes.
4. **High-resolution textures** loaded for viewport display.
5. **Modifiers that evaluate constantly** - especially booleans on dense meshes.
6. **Simulations** with live caches.

## Techniques

| Technique | Effect |
| --- | --- |
| **Collection exclusion** | Removes objects from evaluation entirely - the strongest lever |
| **Simplify** | Global cap on subdivision and texture size for viewport and render |
| **Instancing** | Many objects for the cost of one |
| **Bounds display** | Show heavy objects as boxes while working |
| **Local view** | Isolate what you are editing |
| **Linked files** | Keep parts of a large project in separate files |

**Collection exclusion is the most effective and most under-used.** Working on the interior does
not require the landscape to be evaluated.

## File size

A file that keeps growing usually holds:

- orphaned data - purge it
- packed textures at high resolution
- simulation caches
- many full duplicates

## When to stop optimising

When the viewport is responsive enough to work and the render fits the time budget. Optimisation
past that point is procrastination.

## Common mistakes

- Optimising without measuring
- Reducing render quality when the viewport was the problem
- Full duplicates instead of instances
- Never using collection exclusion
- Subdivision viewport level left equal to render level

## Related

[[3D & Blender Knowledge/15 - Optimization & Performance/VRAM & Memory|VRAM & Memory]] ·
[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Instancing & Scattering|Instancing & Scattering]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Simplify, instancing, collection visibility, statistics overlay.
Prioritisation is practitioner judgement.
