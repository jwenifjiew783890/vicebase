---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# Compositor Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

A node graph that processes the rendered image after rendering. It operates on **render passes** -
separate components of the render - and on external images and footage.

## Why it matters more than people expect

**Re-rendering is expensive; compositing is nearly free.** A large fraction of adjustments do not
need a new render:

| Want to change | Re-render? |
| --- | --- |
| Overall exposure, contrast, colour | No - composite |
| Strength of glow, glare, bloom | No - composite |
| Depth of field, if a depth pass exists | No - composite (with limits) |
| One object's colour or brightness | No - if a cryptomatte exists |
| Fog and atmospheric depth | Usually not - depth pass |
| Denoising | No - denoise pass in comp |
| Geometry, lighting direction, materials | **Yes** |

The decision of what to render as passes is therefore made **before** rendering, and it determines
how much can be fixed afterwards.

## Render passes

Passes split the render into components - diffuse, glossy, transmission, emission, environment,
ambient occlusion, depth (Z), normal, vector (motion), and **cryptomatte**.

**Cryptomatte is the one to enable by default.** It produces per-object and per-material mattes
automatically, so any single object can be isolated afterwards. It costs little to render and
converts many re-renders into composites.

Depth and vector passes enable defocus and motion blur in comp, though both are approximations -
they hold for moderate effects and break down on large ones because a single depth value per pixel
cannot represent what is behind an object.

## Working practice

- **Render to multilayer EXR.** It carries all passes in one file at full float precision. Once
  written to 8-bit PNG the information is gone.
- Build the graph in stages and **use the Viewer node constantly** - it is the only way to see what
  a branch is doing.
- Keep the graph readable with frames and labels; a comp graph outlives your memory of it.
- **Backdrop** display in the compositor shows the viewer output behind the nodes.

## Interaction with other systems

- Colour management sits *after* the compositor - the view transform applies to the final result,
  so judge comp work through the transform you will deliver with. See
  [[3D & Blender Knowledge/10 - Rendering/Colour Management & Output|Colour Management & Output]].
- The compositor also runs on the **render result in the viewport render**, which is why an
  unnoticed comp node makes the render "not match the viewport".

## Common mistakes

- Not enabling cryptomatte, then re-rendering because one object needed adjusting
- Compositing on 8-bit output that has already clipped
- Forgetting the comp graph exists, then debugging a "render bug" that is a leftover node
- Trying to fix geometry, lighting direction or material response in comp - those need a re-render
- Heavy defocus from a depth pass on a scene with fine detail or transparency, where it breaks down

## Related

[[3D & Blender Knowledge/10 - Rendering/Colour Management & Output|Colour Management & Output]] ·
[[3D & Blender Knowledge/20 - VFX & Compositing/CGI & Live-Action Integration|CGI & Live-Action Integration]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Render Failures|Render Failures]]

## Sources

Blender Manual (docs.blender.org/manual, CC-BY-SA 4.0) - compositing nodes, render passes,
cryptomatte, multilayer EXR. The re-render decision table is practitioner judgement.
