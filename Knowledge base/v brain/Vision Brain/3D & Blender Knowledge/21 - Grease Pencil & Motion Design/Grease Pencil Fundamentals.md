---
type: note
domain: 3D & Blender Knowledge
section: 21 - Grease Pencil & Motion Design
created: 2026-09-03
---

# Grease Pencil Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/00 - Grease Pencil & Motion Design|Grease Pencil & Motion Design]]

## What it is

A drawing system whose strokes are **real objects in 3D space**, not pixels on a flat canvas. A
Grease Pencil object has layers, materials, modifiers and can be animated, lit and rendered like
any other object.

## Why "2D inside 3D" matters

This is the property that makes it more than a sketch tool:

- Drawings can be placed **at depth** in a 3D scene, so a camera move produces real parallax
- Strokes can be **animated with the same tools** as 3D - keyframes, modifiers, drivers
- 2D characters can be lit by 3D lights and composited with 3D geometry
- A drawing can be **traced over rendered 3D**, combining accurate perspective with a hand-drawn
  look

## The core concepts

| Concept | Meaning |
| --- | --- |
| **Stroke** | A drawn line, with points, thickness and pressure |
| **Layer** | Drawing layers with opacity, blend mode and onion skinning |
| **Material** | Controls stroke and fill appearance - a GP material is not a surface shader |
| **Onion skinning** | Seeing neighbouring frames, essential for animation |
| **Drawing planes** | Where a stroke lands in 3D - view, front, cursor, or surface |

**The drawing plane is the setting people get wrong first.** A stroke drawn in view alignment sits
on the camera plane; rotate the view and it is edge-on. Deciding where strokes live in space is the
first decision, not an afterthought.

## What it is good for

- Storyboards and animatics
- Traditional 2D animation, with the timing tools of a 3D package
- Annotation and markup over a 3D scene
- Motion graphics elements
- Stylised rendering - outlines, hand-drawn shading over 3D
- Concept work directly in the 3D scene, at correct scale

## What it is not good for

- Large-format illustration - a dedicated 2D painting application is better
- Photo editing
- Complex vector artwork for print

## Modifiers and effects

Grease Pencil has its own modifier stack - build, simplify, noise, thickness, array, mirror - so a
drawing can be animated procedurally. **Build** in particular reveals strokes over time, which is
the standard way to animate a line drawing appearing.

## Performance

Stroke count is the cost driver, much as polygon count is for meshes. Very dense drawings with many
layers become slow to play back; simplify where detail is not visible.

## Common mistakes

- Drawing without deciding the drawing plane, then finding strokes in the wrong place in 3D
- Treating GP materials as surface shaders
- Not using onion skinning for animation
- Enormous stroke counts, then blaming Blender for slow playback
- Overlooking it entirely - the most common mistake, and the reason this note exists

## Related

[[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/Storyboarding & Previsualisation|Storyboarding & Previsualisation]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Animation Fundamentals|Animation Fundamentals]]

## Sources

Blender Manual (docs.blender.org/manual, CC-BY-SA 4.0) - Grease Pencil objects, layers, materials,
modifiers, drawing planes and onion skinning.
