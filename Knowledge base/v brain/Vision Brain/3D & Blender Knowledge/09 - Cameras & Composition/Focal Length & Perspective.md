---
type: note
domain: 3D & Blender Knowledge
section: 09 - Cameras & Composition
created: 2026-09-03
---

# Focal Length & Perspective

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/09 - Cameras & Composition/00 - Cameras & Composition|Cameras & Composition]]

## What it is

Focal length sets field of view, and - through the distance you must stand to frame a subject -
controls **perspective distortion**. It is the most consequential camera decision.

## The mechanism

Focal length alone does not distort. **Distance does.** But focal length determines the distance
you must be at to frame the subject, so in practice they are linked:

- **Wide lens** requires standing close, which exaggerates near-far size differences. Features
  closest to camera enlarge dramatically.
- **Long lens** requires standing far, which compresses apparent depth. Foreground and background
  appear closer in size.

## Practical ranges

| Focal length | Character | Use |
| --- | --- | --- |
| 14-24 mm | Strong exaggeration, dramatic depth | Interiors, dramatic architecture, tight spaces |
| 24-35 mm | Wide but controlled | Environments, architecture, establishing shots |
| 35-50 mm | Close to natural human perception | General purpose, neutral |
| 50-85 mm | Mild compression, flattering | Portraits, character work |
| 85-200 mm | Strong compression, isolation | Product detail, isolating a subject |

**50 mm is the default and is rarely the right answer.** Choosing deliberately is a mark of a
considered image.

## Architecture and verticals

Tilting a camera up at a building makes vertical lines converge, which reads as amateur in
architectural work. Real practice uses a **tilt-shift lens** to keep the sensor parallel to the
building while shifting the framing up.

In 3D, the equivalent: keep the camera level and use the camera's **shift** parameters rather than
rotating. Verticals stay vertical.

For interiors, wide lenses are usually necessary, but going too wide produces spaces that look
distorted and larger than they are - which is dishonest in a visualisation context.

## Common mistakes

- Leaving 50 mm because it is the default
- Very wide lenses close to a face, distorting features unintentionally
- Tilting up at buildings and getting converging verticals
- Ultra-wide interiors that misrepresent the actual space
- Changing focal length to reframe rather than moving the camera, altering perspective by accident

## Related

[[3D & Blender Knowledge/09 - Cameras & Composition/Framing & Composition|Framing & Composition]] ·
[[3D & Blender Knowledge/14 - Architecture & Visualization/Archviz Presentation|Archviz Presentation]]

## Sources

Blender Manual (CC-BY-SA 4.0) - camera lens and shift parameters. Optical behaviour and lens
character are standard photographic knowledge.
