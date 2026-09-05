---
type: note
domain: 3D & Blender Knowledge
section: 21 - Grease Pencil & Motion Design
created: 2026-09-03
---

# Storyboarding & Previsualisation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/00 - Grease Pencil & Motion Design|Grease Pencil & Motion Design]]

## What it is

Deciding what the shot is **before** it becomes expensive to change. Storyboards are drawn frames;
previs is rough 3D animation with real cameras and timing.

## Why it is the highest-leverage stage

Changing a camera angle in previs costs minutes. Changing it after lighting, simulation and
rendering costs days. **Every hour in previs saves several later**, and this holds even for a
single still image.

Previs answers questions that cannot be answered by imagining them:

- Does the composition work at the delivery aspect ratio?
- Does the action read in the time available?
- What is actually in frame, and therefore what needs to be built?
- Does the camera move work, or does it feel sickly?
- How long is this sequence really?

## Doing it in Blender

Blender covers the whole chain, which is unusual:

1. **Storyboard** with Grease Pencil - draw frames directly, in 3D space if useful
2. **Animatic** - cut the boards in the Video Sequencer against the audio track to establish timing
3. **Previs** - blockout geometry, real cameras, rough animation at correct scale
4. **Cut the previs** back into the sequencer, replacing boards as shots are made

The same scene file carries through to production, so camera work done in previs is not thrown
away.

## What previs must have to be useful

- **Correct scale** - otherwise lens choice and depth are meaningless
- **Real camera settings** - the focal lengths that will actually be used
- **Correct aspect ratio** from the start
- **Timing against real audio**, if there is any
- Nothing else. Detail, materials and lighting are actively unhelpful here.

**Previs that looks good is previs that took too long.** Grey geometry is the correct level.

## Shot planning output

A useful previs produces, per shot: duration, camera position and lens, what appears in frame, what
must be built, and any technical requirement (simulation, crowd, effect). That list is the build
plan.

## Common mistakes

- Skipping it and discovering framing problems after the model is finished
- Previs with too much detail, becoming production work
- Wrong aspect ratio, so framing decisions do not transfer
- No audio, so timing is guessed
- Boards drawn without regard to the actual lens, producing shots that cannot be reproduced in 3D

## Related

[[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/Grease Pencil Fundamentals|Grease Pencil Fundamentals]] ·
[[3D & Blender Knowledge/09 - Cameras & Composition/Framing & Composition|Framing & Composition]] ·
[[3D & Blender Knowledge/19 - Production Workflows/Planning & Reference|Planning & Reference]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Grease Pencil, Video Sequencer, camera and markers. The previs
discipline is standard production practice.
