---
type: note
domain: 3D & Blender Knowledge
section: 14 - Architecture & Visualization
created: 2026-09-03
---

# Archviz Presentation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization|Architecture & Visualization]]

## What it is

Delivering images that read as architectural photography rather than as 3D renders.

## Verticals must be vertical

The strongest single convention. Architectural photography uses tilt-shift lenses to keep the
sensor parallel to the building, so vertical lines stay vertical.

In 3D: **keep the camera level and use camera shift** to frame upward. A tilted camera producing
converging verticals immediately reads as amateur.

## Camera height and position

- **Eye level, 1.5-1.6 m** for both interior and exterior. This is how the building is experienced.
- Ground-level or aerial views are legitimate for specific purposes but are not the default.
- Corner views show two facades and give depth; straight-on elevation views read as technical.

## The set of images

A visualisation is usually a set, not one image. A conventional set:

- **Hero exterior** - the main image, best angle, best light
- **Approach** - how you arrive at the building
- **Key interiors** - main living or working spaces
- **Detail shots** - materials, junctions, designed elements
- **Context** - the building in its setting
- Optionally: plan-view or axonometric for spatial understanding

Consistency of treatment across the set matters more than any single image.

## Post-processing

Restrained is the rule. Acceptable and normal:

- exposure and contrast adjustment
- slight colour grading for consistency across the set
- subtle glare on bright sources
- minor cleanup

Not acceptable in work presented as representative:

- painting in elements that do not exist
- altering proportions
- lighting that could not occur

**Render passes and cryptomatte** make adjustment possible without re-rendering - see
[[3D & Blender Knowledge/10 - Rendering/Colour Management & Output|Colour Management & Output]].

## Presentation output

- High resolution, since these are often printed or shown large
- Consistent aspect ratio across the set
- 16-bit or EXR if grading follows
- Colour-managed with a deliberate view transform

## Common mistakes

- Converging verticals
- Camera at an arbitrary height
- Inconsistent treatment across the set
- Heavy-handed post-processing
- Delivering 8-bit JPEGs then being asked for adjustments
- One image where a set was needed

## Related

[[3D & Blender Knowledge/09 - Cameras & Composition/Focal Length & Perspective|Focal Length & Perspective]] ·
[[3D & Blender Knowledge/10 - Rendering/Colour Management & Output|Colour Management & Output]]

## Sources

Practitioner synthesis, following established architectural photography convention. Camera shift
and colour management are documented in the Blender Manual (CC-BY-SA 4.0).
