---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# Camera Tracking & Matchmoving

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

Recovering the real camera's motion from footage so that CG can be placed in the scene and stay
locked to it. Blender's tracker does **2D feature tracking** and **3D reconstruction**, supporting
camera tracking, object tracking, and plane tracks for compositing.

## Camera solve versus object solve

- **Camera solve** - the camera moved, the scene was static. Recovers camera motion. This is the
  common case.
- **Object solve** - the camera was static (or already solved) and an object moved. Recovers the
  object's motion, so CG can be attached to a moving real object.

## Lens calibration is a prerequisite, not an optional step

The manual is explicit: **all cameras record distorted video**, and accurate camera motion requires
the actual focal length and distortion strength.

- Focal length can come from the camera settings or **EXIF data**
- Distortion can be calibrated manually: draw a line along something known to be straight in the
  footage using the annotation tool, then adjust distortion values until the annotation matches the
  footage

Guessing these produces a solve that looks acceptable and drifts.

## Getting a good track

**Track quality is decided by the markers, not by the solver.**

- Choose features with **high contrast in two directions** - corners, not edges. An edge slides
  along itself.
- Avoid features that are moving, reflective, in shadow that changes, or that pass behind
  something.
- Spread markers across the frame **and across depth**. All markers on one plane cannot resolve
  3D.
- Aim for well over the theoretical minimum; more good markers means a more stable solve.
- Track long, not just a few frames. Short tracks contribute little.
- Use the right pattern and search sizes, and let the tracker use a motion model when the feature
  changes shape.

## Judging the solve

**Solve error is measured in pixels.** Lower is better and under roughly one pixel is a common
working target, but the number alone is not proof:

1. Check the error per track and delete or re-track the worst offenders.
2. **Set up a test:** place simple geometry (a cube, a plane on the ground) into the solved scene
   and play the shot at full speed. If it sits still in the world, the track is good. If it slides,
   swims or drifts, it is not - regardless of the error figure.

This test is the real acceptance criterion.

## Setting scene orientation and scale

A solve is arbitrary in position, orientation and scale. It must be anchored:

- set the **floor** from three or more coplanar tracks
- set the **origin**
- set an **axis** from two markers along a known direction
- **set scale from a known real distance** in the shot

Without scale, physics, depth of field and lighting falloff are all wrong. See
[[3D & Blender Knowledge/01 - 3D Fundamentals/Scale & Units|Scale & Units]].

## Plane tracks

A plane track follows a flat surface in the footage and is used to attach an image or replace a
surface - screens, posters, signs. Far simpler than a full 3D solve when the task is only to
replace a flat region.

## When tracking will not work

Be able to recognise these before spending hours:

- **No parallax** - a pure pan from a fixed point gives no depth information; a 3D solve is
  impossible, though a 2D or plane track may still serve
- Heavy motion blur
- Featureless surfaces - sky, clean walls, water
- Rolling shutter distortion
- A cut in the middle of the shot

## Common mistakes

- Tracking edges instead of corners
- All markers on one plane or in one region
- Trusting a low solve error without a placement test
- Skipping lens calibration
- Never setting scene scale
- Tracking the distorted plate

## Related

[[3D & Blender Knowledge/20 - VFX & Compositing/VFX Pipeline & Plate Preparation|VFX Pipeline & Plate Preparation]] ·
[[3D & Blender Knowledge/20 - VFX & Compositing/Masking & Rotoscoping|Masking & Rotoscoping]]

## Sources

Blender Manual (CC-BY-SA 4.0) - *Motion Tracking*: 2D tracking and 3D reconstruction, camera and
object tracking, plane tracks, manual lens calibration via annotations and EXIF focal length,
scene orientation and scale tools. Marker-selection and acceptance-test guidance is practitioner
judgement.
