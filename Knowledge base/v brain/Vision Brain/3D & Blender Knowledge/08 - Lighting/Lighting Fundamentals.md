---
type: note
domain: 3D & Blender Knowledge
section: 08 - Lighting
created: 2026-09-03
---

# Lighting Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/08 - Lighting/00 - Lighting|Lighting]]

## What it is

Placing light so form reads and the image has intent. In a physically based renderer, light behaves
like real light - which means real-world reasoning applies directly.

## The properties that matter

**Size controls shadow softness.** This is the most useful single fact in lighting. A small light
gives hard-edged shadows; a large one gives soft shadows. The sun is enormous but very distant, so
it acts small and gives crisp shadows; an overcast sky is a huge source, so shadows nearly vanish.

To soften a shadow, **make the light bigger**, not dimmer.

**Intensity falls off with the square of distance** for point-like sources. Doubling the distance
quarters the illumination. This is why moving a light is a much stronger control than changing its
power, and why scenes at wrong scale never light correctly.

**Colour temperature** carries meaning: ~1800K candle, ~2700K domestic tungsten, ~4000K neutral
fluorescent, ~5500K daylight, ~7000K+ shade and overcast. Mixing temperatures - warm key against
cool ambient - is what makes an image read as photographic rather than flat.

## Three-point lighting

The standard structure, not because it is a rule but because it maps onto the three jobs light has:

| Light | Job | Typical treatment |
| --- | --- | --- |
| **Key** | Primary illumination, defines form and shadow direction | Strongest, off-axis, often 30-45 degrees from camera |
| **Fill** | Lifts shadows so they are readable | Much weaker, opposite side, larger and softer |
| **Rim / back** | Separates subject from background | Behind the subject, often brighter, narrow |

**Key-to-fill ratio is the mood control.** Near-equal is flat and commercial; a strong ratio is
dramatic; fill from bounce only is moody.

## What makes lighting look real

1. **Motivated sources** - light appears to come from somewhere in the scene: a window, a lamp, the
   sky. Unmotivated lights read as artificial.
2. **Bounce.** Real light bounces and picks up colour from surfaces. Path tracing does this
   automatically if you let it - which is why an interior with only direct light looks wrong.
3. **Variation.** Even illumination is uninteresting and unreal.
4. **Correct scale**, without which falloff is wrong everywhere.

## Common mistakes

- Lighting with one bright light and wondering why it looks flat
- Making shadows softer by reducing intensity, which only makes them dark and still hard
- Light sizes that make no physical sense - a two-metre "bulb"
- Ignoring colour temperature, so everything is neutral white and lifeless
- Lighting in EEVEE and rendering in Cycles
- Adding lights to fix a scene that is dark because of inverted normals

## Related

[[3D & Blender Knowledge/08 - Lighting/Studio & Product Lighting|Studio & Product Lighting]] ·
[[3D & Blender Knowledge/08 - Lighting/Natural & Environment Lighting|Natural & Environment Lighting]]

## Sources

Blender Manual (CC-BY-SA 4.0) - light object types and parameters. Physical behaviour (inverse
square, source size and penumbra, colour temperature) is standard optics; the three-point structure
and mood guidance are established practice.
