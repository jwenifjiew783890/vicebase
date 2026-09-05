---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# VFX Pipeline & Plate Preparation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

The order in which a shot with live-action footage is actually assembled, and the preparation the
footage needs before any of it works.

## The order matters and is not negotiable

```
1. Acquire plate        footage, plus on-set data if available
2. Prepare plate        colour space, undistort, reference frames
3. Track                2D features -> 3D camera or object solve
4. Set scene scale      orient and scale the solved scene to the real world
5. Rough layout         place CG roughly, confirm the track holds
6. Roto and masks       isolate elements needing to sit in front of CG
7. Model / animate      the CG content
8. Match lighting       HDRI or reconstructed lighting from the plate
9. Render with passes   including shadow catcher and cryptomatte
10. Composite           integrate, grade, add grain, redistort
11. Review in motion    at full speed, at delivery size
```

**Nearly every VFX failure comes from doing these out of order** - modelling before the track is
solved, or lighting before scale is set.

## Plate preparation

Footage is not ready to use as it arrives:

- **Colour space.** Footage has its own transfer function. Interpreting it wrongly makes every
  subsequent colour and lighting judgement wrong. Set it deliberately on the image node.
- **Undistort.** All camera lenses distort. Track and place CG against an *undistorted* plate, then
  **redistort the CG at the end** so it matches the original footage. Skipping this is why CG
  slides against the plate near frame edges.
- **Frame rate and resolution** must be established and held throughout.
- **Reference frames** - a clean plate (the scene without the subject) is enormously useful for
  roto and patching, if it exists.

## On-set data, if you can get it

Cheap to record, expensive to reconstruct later:

- camera focal length and sensor size
- camera height and approximate distances
- **HDRI of the environment** - the single most valuable item
- a **grey/chrome ball** shot in the scene lighting, which gives lighting direction and intensity
- measurements of anything the CG must sit on or align with

## Working in motion

**Judge everything at full speed.** A composite that holds up frame-by-frame can slide, chatter or
pop in motion, and that is the only thing the viewer will see. Still-frame perfection is not the
goal.

## Common mistakes

- Tracking a distorted plate, or forgetting to redistort at the end
- Wrong footage colour space, poisoning all colour decisions downstream
- Modelling before the camera solve is confirmed
- No scene scale set, so lighting falloff and depth of field are wrong
- Judging only on still frames
- Not collecting on-set data when it was free to collect

## Related

[[3D & Blender Knowledge/20 - VFX & Compositing/Camera Tracking & Matchmoving|Camera Tracking & Matchmoving]] ·
[[3D & Blender Knowledge/20 - VFX & Compositing/CGI & Live-Action Integration|CGI & Live-Action Integration]] ·
[[3D & Blender Knowledge/01 - 3D Fundamentals/Scale & Units|Scale & Units]]

## Sources

Blender Manual (CC-BY-SA 4.0) - movie clip editor, lens distortion, colour management of input
footage. The pipeline order and on-set data list are standard VFX practice.
