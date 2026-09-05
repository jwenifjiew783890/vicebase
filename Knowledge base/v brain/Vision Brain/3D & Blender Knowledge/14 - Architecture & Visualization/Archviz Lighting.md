---
type: note
domain: 3D & Blender Knowledge
section: 14 - Architecture & Visualization
created: 2026-09-03
---

# Archviz Lighting

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization|Architecture & Visualization]]

## What it is

Lighting for architecture, where light is partly a design subject rather than only a presentation
choice - the building was designed for particular light, and the render should show it.

## Sun position is a design fact

For a real project the sun path is determined by **latitude, orientation, date and time**. It is
not free. A south-facing facade in the northern hemisphere behaves differently from a north-facing
one, and the design usually depends on that.

Blender's sky model can position the sun from geographic coordinates and time, which is the correct
approach when the image claims to represent reality.

## Choosing the moment

| Condition | Character | Use for |
| --- | --- | --- |
| **Clear midday** | High sun, short hard shadows, strong contrast | Showing form and massing; harsh for facades |
| **Golden hour** | Low warm sun, long shadows, strong modelling | The reliable flattering exterior choice |
| **Overcast** | Huge soft source, no strong shadow, even | Honest material presentation; can be flat |
| **Dusk / blue hour** | Cool ambient, warm interior light glowing out | The classic hero exterior shot |
| **Night** | Artificial light only, high contrast | Lighting design, commercial frontage |

**Dusk is popular because it lets interior light read**, giving the building warmth and life
against a cool sky. It also flatters, which is why it is sometimes considered dishonest - a
building should also be shown in ordinary daylight.

## Interior daylight

Covered in [[3D & Blender Knowledge/14 - Architecture & Visualization/Interiors|Interiors]], but the
essentials: light through openings, portals on windows, enough bounces, and patience.

## Artificial lighting

- Match real fixture types and outputs where the lighting design is known
- Colour temperature consistency matters - mixed unintentional temperatures look like an error
- Downlights produce characteristic scallops on walls; getting them right reads as designed
- Do not over-light. Real interiors have pools of light and darker areas.

## Honesty

An architectural visualisation is used to make decisions and to sell. There is a real line between
presenting a design well and misrepresenting it:

- lighting that never occurs at that location
- rooms lit far brighter than the fixtures could achieve
- perpetual golden hour on every facade
- ultra-wide lenses making spaces read larger than they are

**The image should be achievable.** That is both an ethical and a practical position - clients
notice when the building does not match the render.

## Common mistakes

- Arbitrary sun direction on a real project
- Every image at golden hour
- Interiors lit by invisible fill lights with no motivation
- Mixed colour temperatures by accident
- Over-lit interiors with no shadow
- No portals, so interior noise never resolves

## Related

[[3D & Blender Knowledge/08 - Lighting/Natural & Environment Lighting|Natural & Environment Lighting]] ·
[[3D & Blender Knowledge/14 - Architecture & Visualization/Archviz Presentation|Archviz Presentation]]

## Sources

Blender Manual (CC-BY-SA 4.0) - sky texture, sun positioning, light portals. Time-of-day
characterisation and the honesty discussion are practitioner judgement.
