---
type: note
domain: 3D & Blender Knowledge
section: 09 - Cameras & Composition
created: 2026-09-03
---

# Depth of Field & Camera Realism

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/09 - Cameras & Composition/00 - Cameras & Composition|Cameras & Composition]]

## What it is

The details that make a render read as photographed rather than computed. Depth of field is the
most significant, and the most often overdone.

## Depth of field

Physically, DoF depends on aperture (f-stop), focal length and focus distance. In Blender these are
real parameters, so **real photographic reasoning applies**.

- Lower f-stop - shallower focus, more background blur
- Longer focal length - shallower at the same aperture
- Closer focus distance - shallower

**Scale must be correct for this to behave sensibly.** At wrong scale you get macro-lens blur on a
building.

Use focus **on an object** rather than a fixed distance where the subject may move - the focus then
tracks it.

## The main error: too much

Heavy background blur on everything is the strongest tell of an inexperienced render. Real
photography of architecture and products usually has **deep** focus - f/8 to f/16 - because the
subject must be legible.

Shallow DoF is for isolating a small subject. It is not a realism setting.

## Other realism cues

| Cue | Effect |
| --- | --- |
| **Slight imperfection in framing** | Perfectly centred, perfectly level images look computed |
| **Motion blur** | Essential for animation; wrong to omit on moving subjects |
| **Bloom / glare** | Real lenses bloom around bright sources. Subtle is the operative word. |
| **Chromatic aberration** | Real lenses have it. Very subtle, at frame edges only. |
| **Vignetting** | Slight darkening at corners |
| **Film grain / sensor noise** | A little unifies an image and hides residual render noise |
| **Not-quite-clean surfaces** | Dust, fingerprints, wear - the strongest realism cue of all |

Every one of these is ruined by overuse. The rule is that the viewer should not be able to name
what you did.

## Exposure and colour management

- Set exposure with light intensity, not by compensating in the film settings
- Choose the view transform deliberately. A filmic or AgX-style transform handles bright highlights
  the way a camera does; a plain standard transform clips them harshly and is a common reason
  renders look harsh and video-game-like.

## Common mistakes

- Depth of field so shallow that the subject is unreadable
- DoF at wrong scene scale, producing physically impossible blur
- Stacking bloom, aberration, vignette and grain until the image looks processed
- Fixing exposure in post rather than lighting correctly
- Default view transform on a high-dynamic-range scene, clipping highlights

## Related

[[3D & Blender Knowledge/10 - Rendering/Colour Management & Output|Colour Management & Output]]

## Sources

Blender Manual (CC-BY-SA 4.0) - camera DoF parameters, colour management and view transforms.
Photographic reasoning and restraint guidance are practitioner judgement.
