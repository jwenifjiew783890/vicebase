---
type: note
domain: 3D & Blender Knowledge
section: 10 - Rendering
created: 2026-09-03
---

# Colour Management & Output

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/10 - Rendering/00 - Rendering|Rendering]]

## What it is

How rendered values become displayed pixels, and what file you deliver. Getting this wrong makes
technically correct renders look wrong.

## View transform

A render holds high dynamic range values. The **view transform** maps them to display range.

- A **standard** transform clips highlights hard. Bright areas turn flat white with harsh edges,
  which is a common reason renders look cheap.
- A **filmic or AgX-style** transform rolls highlights off gradually, as film and cameras do.
  Highlights retain colour and gradation.

**This is a display transform, not an effect.** It does not change the render; it changes how the
render is shown. Judge lighting through the transform you will deliver with.

## Formats

| Format | Bit depth | Use |
| --- | --- | --- |
| **OpenEXR** | 16/32-bit float | Compositing, grading, anything with further work to do. Keeps full dynamic range. |
| **PNG** | 8 or 16-bit | Final delivery, lossless |
| **JPEG** | 8-bit | Web delivery only, lossy |
| **TIFF** | 8/16-bit | Print delivery |

**Render to EXR if any post-work will happen.** Once written to 8-bit, the highlight and shadow
information is gone and no amount of grading recovers it.

For animation, render **image sequences, not video files.** A crashed render loses one frame rather
than the whole render, and frames can be re-rendered selectively.

## Render passes

Separate components - diffuse, glossy, emission, ambient occlusion, cryptomatte, depth, normal -
written alongside the beauty render. They allow adjustment in compositing without re-rendering.

**Cryptomatte** is the practical one: it gives per-object and per-material mattes, so a single
object can be adjusted afterwards. Cheap to render, and it converts many re-renders into
composites.

## Resolution and aspect

Set resolution and aspect **before** composing, because framing depends on aspect ratio. Changing
it afterwards changes the composition.

Render at delivery resolution. Rendering large then downsampling does reduce visible noise, at
proportionally more time.

## Common mistakes

- Judging lighting under a different view transform than the delivery one
- Delivering 8-bit and then being asked to grade it
- Video output for animation, losing everything on a crash
- No cryptomatte, then re-rendering because one object needed adjusting
- Resolution changed after framing

## Related

[[3D & Blender Knowledge/09 - Cameras & Composition/Depth of Field & Camera Realism|Depth of Field & Camera Realism]]

## Sources

Blender Manual (CC-BY-SA 4.0) - colour management, view transforms, output formats, render passes
and cryptomatte.
