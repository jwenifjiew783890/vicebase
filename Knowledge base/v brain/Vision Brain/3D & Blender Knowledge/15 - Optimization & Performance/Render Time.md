---
type: note
domain: 3D & Blender Knowledge
section: 15 - Optimization & Performance
created: 2026-09-03
---

# Render Time

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/15 - Optimization & Performance/00 - Optimization & Performance|Optimization & Performance]]

## What it is

Finding where render time actually goes, rather than adjusting the setting that is easiest to
reach.

## Measure by elimination

Render a small region or a low resolution, then disable one thing at a time and observe:

1. Reduce **max bounces** - large change means light transport dominates
2. Disable **volumetrics** - large change means volumes dominate
3. Reduce **subdivision render levels** - large change means geometry dominates
4. Reduce **texture size** - large change suggests memory pressure
5. Reduce **samples** - if this is the only thing that helps, then sampling really was the driver

**Most people adjust samples first, and it is often not the main cost.**

## Common dominant costs

| Cost | When it dominates |
| --- | --- |
| Light bounces | Interiors, glass, anything with heavy GI |
| Volumetrics | Any scene with fog, smoke or god rays |
| Transmission / caustics | Glass and liquids |
| Geometry | High subdivision, dense scatter |
| Memory pressure | GPU fallback to CPU - catastrophic and often unnoticed |
| Sampling | Clean scenes where the others are already low |

## Reliable savings

- **Denoise** rather than brute-force sampling - the largest single saving in most scenes
- **Adaptive sampling** with a noise threshold, spending effort only where needed
- **Bounce limits tuned per scene** - an exterior does not need interior bounce counts
- **Light portals** on interior openings
- **Clamp indirect** to kill fireflies rather than sampling them away
- **Render only what is visible** - exclude off-camera geometry

## Animation

Per-frame cost multiplies. A 10-second animation at 24 fps is 240 renders, so a 30-second saving
per frame is two hours.

- Render image sequences, never video
- Consider EEVEE seriously - for many animations the difference is not visible in motion
- Use persistent data between frames where the scene is static
- Test-render scattered frames across the sequence, not just frame 1

## Common mistakes

- Raising samples as the first response
- Not noticing a CPU fallback
- Default bounces on every scene regardless of type
- Volumetrics at full quality during look development
- No denoising
- Optimising a still when the deadline is an animation

## Related

[[3D & Blender Knowledge/10 - Rendering/Cycles Sampling & Noise|Cycles Sampling & Noise]] ·
[[3D & Blender Knowledge/15 - Optimization & Performance/VRAM & Memory|VRAM & Memory]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Cycles performance settings, adaptive sampling, persistent data.
The diagnostic-by-elimination approach is practitioner judgement.
