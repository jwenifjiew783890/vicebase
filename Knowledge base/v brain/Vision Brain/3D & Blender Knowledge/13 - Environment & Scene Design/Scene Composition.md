---
type: note
domain: 3D & Blender Knowledge
section: 13 - Environment & Scene Design
created: 2026-09-03
---

# Scene Composition

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/13 - Environment & Scene Design/00 - Environment & Scene Design|Environment & Scene Design]]

## What it is

Assembling an environment so it reads as a place and directs attention.

## Build from the camera outward

The most useful discipline in environment work: **place the camera first**, then build what it
sees, in order of visual importance.

This prevents the standard failure of building a complete environment of which the shot uses 5%.

## Layers

An environment that reads has depth structure:

| Layer | Job | Detail level |
| --- | --- | --- |
| Foreground | Frames the shot, gives depth cue | Often out of focus - low detail is fine |
| Midground | Usually the subject | Highest detail |
| Background | Context and scale | Low detail, can be cards or matte |

Something in the foreground - even a blurred branch or doorway edge - transforms a flat image.

## Believability

Real places have history and function:

- **Wear where things are touched or walked** - handles, thresholds, corners
- **Accumulation where things collect** - leaves in corners, dust on ledges
- **Irregularity** - nothing is perfectly aligned, evenly spaced or identical
- **Evidence of use** - objects left, moved, worn

**Perfect and uniform is the strongest tell of a computer-generated environment.** A slightly
crooked picture frame does more than another thousand polygons.

## Scale anchors

Include objects with known size - doors, steps, handrails, furniture, people. Without them a viewer
cannot judge scale, and the space reads as ambiguous.

## Managing weight

Environments become heavy fast. See
[[3D & Blender Knowledge/15 - Optimization & Performance/Scene Weight|Scene Weight]], but the
structural decisions belong here:

- Detail only what the camera resolves
- Instance everything repeated
- Use collections and exclusion to work on parts in isolation
- Background as cards or low detail

## Common mistakes

- Building the environment before choosing the camera
- Uniform detail everywhere
- No foreground layer
- Everything perfectly aligned and clean
- No scale anchors
- Unique geometry where instances would have worked

## Related

[[3D & Blender Knowledge/09 - Cameras & Composition/Framing & Composition|Framing & Composition]] ·
[[3D & Blender Knowledge/13 - Environment & Scene Design/Scattering & Set Dressing|Scattering & Set Dressing]]

## Sources

Practitioner synthesis - standard environment art practice.
