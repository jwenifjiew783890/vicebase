---
type: note
domain: 3D & Blender Knowledge
section: 21 - Grease Pencil & Motion Design
created: 2026-09-03
---

# Motion Graphics & Text Animation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/00 - Grease Pencil & Motion Design|Grease Pencil & Motion Design]]

## What it is

Animated typography, titles, logos, diagrams and abstract motion - design that moves rather than
characters that act.

## Blender's motion-graphics toolkit

There is no dedicated motion-graphics mode; the capability comes from combining existing systems,
which is why it is easy to miss:

| Tool | Use |
| --- | --- |
| **Text objects** | Real 3D text, extrudable and bevelable, converted to mesh or curve when needed |
| **Geometry Nodes** | Procedural layout, instancing per character or element, driven animation |
| **Drivers** | One value controlling many - the core of procedural motion design |
| **Modifiers** | Build, array, wave, cast, simple deform - animate the modifier, not the geometry |
| **Grease Pencil Build** | Reveal strokes over time |
| **Curves and follow-path** | Motion along authored paths |
| **Shape keys** | Blend between authored states |

## Animating text per character

The recurring motion-graphics requirement. Approaches:

- **Geometry Nodes** - instance per character, offset the animation by index. Fully procedural,
  adjustable, and the right answer for most cases.
- **Convert to mesh and separate** - direct control per letter, but the text is no longer editable
  as text.
- **Build modifier** - reveals over time, simple and effective for a typewriter or draw-on effect.

**Deciding whether the text must stay editable** determines the approach. Converting to mesh is
one-way.

## Timing is the whole craft

Motion design lives or dies on timing, far more than on the visual design:

- **Ease in and out** - linear motion reads as mechanical
- **Overshoot and settle** - the small overshoot past the target then settle back is what makes
  motion feel physical
- **Offset** - elements starting at slightly different times reads as designed; everything moving
  together reads as flat
- **Fast in, slow out** is the general shape of appealing motion

The graph editor is where this is done, not the timeline. See
[[3D & Blender Knowledge/11 - Animation & Rigging/Animation Fundamentals|Animation Fundamentals]].

## Rendering motion graphics

- **EEVEE is usually correct here.** Motion graphics rarely need path-traced accuracy, and the
  iteration speed matters more.
- Motion blur is important - motion graphics without it look stroboscopic
- Alpha output where the result will be composited over something else
- Flat, graphic lighting is often the intent; physical accuracy is not the goal

## Common mistakes

- Linear interpolation everywhere
- Everything animating simultaneously with no offset
- Converting text to mesh before the copy is final
- Cycles where EEVEE would be indistinguishable and far faster
- No motion blur
- Hand-animating per character what geometry nodes would drive procedurally

## Related

[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Geometry Nodes Fundamentals|Geometry Nodes Fundamentals]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Animation Fundamentals|Animation Fundamentals]]

## Sources

Blender Manual (CC-BY-SA 4.0) - text objects, modifiers, drivers, geometry nodes, EEVEE motion
blur. Timing craft is standard motion-design practice.
