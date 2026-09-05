---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# Video Sequence Editor & Audio

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

Blender's built-in non-linear video editor. It cuts, arranges, transitions and mixes audio, and it
renders out finished video - inside the same application as the 3D work.

Easy to overlook, and genuinely useful for a specific set of jobs.

## When it is the right tool

- **Assembling a sequence of rendered shots** without leaving Blender
- **Previs and animatics** - cutting storyboard frames to timing before animating
- **Simple edits** of rendered output: titles, cuts, fades, speed changes
- **Audio for animation** - loading a dialogue or music track so animation can be timed to it
- Batch conversion of image sequences to video

## When it is not

- Complex multi-track edits with heavy colour grading and effects - a dedicated editor is better
- Collaborative editing workflows
- Anything needing broad codec support or delivery-spec compliance

**Being honest about this matters:** using the VSE for a job it is poor at wastes more time than
learning another tool would.

## Audio for animation

This is the highest-value use for most 3D work. Load the audio, and the waveform is visible in the
timeline and dope sheet, so animation can be keyed against it directly.

Essential for lip sync - see
[[3D & Blender Knowledge/11 - Animation & Rigging/Facial Animation & Lip Sync|Facial Animation & Lip Sync]].

Note that audio scrubbing and synchronisation depend on playback settings; if audio and animation
appear out of step during playback, check the sync mode before assuming the animation is wrong.

## Image sequences, not video

Render animations as **image sequences**, then assemble in the VSE. A crash costs one frame rather
than the whole render, and individual frames can be re-rendered and dropped back in.

The VSE is exactly the right tool for turning that sequence into a deliverable.

## Practical notes

- The VSE reads the scene's frame rate; a mismatch between footage and scene frame rate causes
  drift
- Strips can reference **other scenes**, so a sequence can cut between different 3D scenes in one
  file
- Proxies help with playback performance on heavy footage
- Colour management applies here too - the view transform affects what you see

## Common mistakes

- Rendering animation directly to video and losing everything to one crash
- Frame-rate mismatch between footage, scene and delivery
- Using the VSE for an edit that needs a real editor
- Not loading audio, then animating timing by guesswork
- Forgetting the view transform applies to VSE output

## Related

[[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/Storyboarding & Previsualisation|Storyboarding & Previsualisation]] ·
[[3D & Blender Knowledge/10 - Rendering/Colour Management & Output|Colour Management & Output]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Video Sequencer, strips, audio, proxies, scene strips. Tool-choice
guidance is practitioner judgement.
