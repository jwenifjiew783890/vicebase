---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# Masking & Rotoscoping

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

Hand-authored mattes. Rotoscoping is drawing a matte around a subject frame by frame when no key is
possible - which is most of the time, because most footage is not shot against a screen.

Blender provides a **Mask Editor**, available as a mode in the Movie Clip Editor, and masks can be
**moved and deformed by tracking data**.

## When roto is needed

- No green screen
- A real object must appear **in front of** a CG element
- Isolating part of the frame for a local grade
- Removing something - rigs, markers, modern objects in a period shot
- Garbage masks around a key

## The technique that halves the work

**Let tracking drive the mask.** Rather than adjusting every point on every frame, track a feature
and parent the mask to it, so the mask follows the motion. Blender supports exactly this - tracks
can move and deform masks in the Mask Editor.

The general principle: **animate as few points as possible, as rarely as possible.**

## Practical approach

1. **Split the subject into parts** that move independently - upper arm, forearm, hand - rather
   than one shape for everything. Each part then moves simply.
2. Use **as few points as the shape allows.** Every extra point is another thing to animate and
   another source of chatter.
3. Key on **extremes** - the frames where motion changes direction - then check the frames between
   and correct only where needed.
4. **Feather to match the footage.** A hard-edged matte against motion-blurred footage reads as cut
   out. Feather should vary - sharper where the subject is sharp, softer where it is blurred.
5. Work at the frame rate the shot will play at, and **review in motion**.

## Judging roto

Play it at full speed over a contrasting background. Look for:

- **Chatter** - the edge vibrating frame to frame. The most common defect, caused by too many
  animated points.
- **Slipping** - the matte lagging the subject
- **Uniform feather** where the footage has variable blur
- Corners that pop as points cross over each other

## Cost

Rotoscoping is slow and unglamorous, and it is often the largest time cost in a shot. **Estimate it
honestly.** A few seconds of a complex moving subject can be a day.

Reducing the cost: shoot for it if you can, use tracking to drive masks, split into simple parts,
and accept that a matte only needs to be good enough for the shot's actual duration and size.

## Common mistakes

- One complex shape for a whole articulated subject
- Too many control points, producing chatter
- Adjusting every frame rather than keying extremes
- Uniform hard feather against motion-blurred footage
- Not using tracks to drive masks
- Underestimating the time

## Related

[[3D & Blender Knowledge/20 - VFX & Compositing/Camera Tracking & Matchmoving|Camera Tracking & Matchmoving]] ·
[[3D & Blender Knowledge/20 - VFX & Compositing/Keying & Green Screen|Keying & Green Screen]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Mask Editor in the Movie Clip Editor, mask parenting to tracking
data, feather controls. Roto technique and acceptance criteria are standard VFX practice.
