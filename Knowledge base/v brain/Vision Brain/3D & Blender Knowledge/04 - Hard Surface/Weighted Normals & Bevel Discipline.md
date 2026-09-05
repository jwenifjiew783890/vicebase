---
type: note
domain: 3D & Blender Knowledge
section: 04 - Hard Surface
created: 2026-09-03
---

# Weighted Normals & Bevel Discipline

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface|Hard Surface]]

## What it is

The two techniques that make hard-surface models read as real manufactured objects rather than
computer geometry.

## Why bevels matter more than anything else

**Nothing in the physical world has a perfectly sharp edge.** Every manufactured edge has a small
radius, from machining, casting, moulding or wear. That radius catches light and produces the thin
bright line along every edge that the eye uses to read an object as real.

A model with perfectly sharp edges looks like computer graphics *even when everything else is
right*. Adding bevels is the single highest-value change to a hard-surface model.

## Bevel scale

Bevels should be **small** - a fraction of a millimetre to a couple of millimetres on a
human-scale object. Large enough to catch a highlight, small enough that you would not
consciously notice it.

Too large and the object looks soft, moulded or toy-like. Too small - or absent - and it looks
synthetic.

Segments: 1-2 for background, 2-3 for mid-ground, more only where the edge is close to camera.
Each segment costs geometry on every edge.

## The shading problem bevels cause

Bevelling a smooth-shaded mesh creates uneven shading across large flat faces, because vertex
normals get averaged with the narrow bevel faces. The surface looks dented or smeared near edges.

**Weighted Normal modifier** fixes this: it weights normal averaging by face area, so large flat
faces dominate and stay flat, while the narrow bevel still catches light.

## The standard hard-surface stack

```
Bevel            small width, 2-3 segments, angle-limited, harden normals off
Weighted Normal  keep sharp on
Subdivision      only if the form genuinely needs it
```

Plus smooth shading with an angle threshold, or smooth-by-angle.

**Apply scale before bevelling.** Non-uniform scale gives inconsistent bevel width across axes,
and it looks like the bevel modifier is broken. It is not.

## Bevel by weight and limit method

- **Angle** limit - bevel every edge sharper than a threshold. Fast, good default.
- **Weight** - bevel only edges you mark. Precise control on complex objects.
- **Vertex group** - selective, useful in procedural setups.

Angle first; weights when angle gives the wrong result somewhere specific.

## Common mistakes

- No bevels at all - the most common reason a hard-surface render looks fake
- Bevels far too large, making everything look injection-moulded
- Bevel without Weighted Normal, then fighting the resulting shading in the shader editor
- Not applying scale, then blaming the bevel modifier for uneven width
- Excessive segments on background objects, wasting geometry invisibly

## Related

[[3D & Blender Knowledge/01 - 3D Fundamentals/Normals & Shading|Normals & Shading]] ·
[[3D & Blender Knowledge/02 - Blender Fundamentals/Modifiers|Modifiers]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Bevel and Weighted Normal modifiers, shading. The physical
argument for edge radii and the scale guidance are practitioner judgement grounded in how real
surfaces are manufactured.
