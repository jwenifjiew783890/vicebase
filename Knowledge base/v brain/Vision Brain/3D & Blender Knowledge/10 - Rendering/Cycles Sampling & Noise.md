---
type: note
domain: 3D & Blender Knowledge
section: 10 - Rendering
created: 2026-09-03
---

# Cycles Sampling & Noise

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/10 - Rendering/00 - Rendering|Rendering]]

## What it is

Path tracing estimates each pixel by sampling light paths. Noise is the **variance** of that
estimate - not an error, but an incomplete average.

## Why more samples is the wrong first answer

Noise falls with the **square root** of sample count. Halving noise requires **four times** the
samples, and therefore roughly four times the render time. The returns are brutal.

The correct order of attack:

1. **Denoise.** Modern denoisers resolve far more noise per unit time than sampling does. Use one.
2. **Fix the cause** of unusual noise - see below.
3. **Then** add samples, only where the denoiser is visibly smearing detail.

## Adaptive sampling

Samples pixels until they reach a noise threshold, spending effort where it is needed. Set the
**noise threshold** rather than the sample count - it targets a quality, not a budget.

Max samples then acts as a ceiling, not a target.

## Fireflies

Single very bright pixels. They come from **improbable paths that carry enormous energy** - a tiny
intense light source found by a rare bounce.

Fixes, best first:

- **Enlarge the light source.** A physically plausible size makes the path probable rather than
  rare.
- **Clamp indirect light.** Caps the energy any single indirect sample can carry. Effective, and it
  does lose some genuine energy.
- Reduce max bounces for glossy or transmissive paths
- More samples - the expensive last resort

## Where render time actually goes

| Cost | Typical driver |
| --- | --- |
| Light bounces | Interiors and glass need many; a product on a backdrop needs few |
| Transmission / caustics | Glass and liquids are disproportionately expensive |
| Volumetrics | Very expensive. Fog and smoke can dominate a render. |
| Subdivision render levels | Silently enormous geometry |
| Texture memory | Especially on GPU, where exceeding VRAM is catastrophic |
| Sample count | The thing people adjust first, and rarely the main driver |

**Diagnose before optimising.** Reduce bounces and check the time change; disable volumetrics and
check again. Guessing wastes more time than measuring.

## Light paths

Max bounces controls how far light travels. Too few makes interiors dark and glass black; too many
costs time for invisible gains. Interiors need meaningfully more than exteriors.

## Common mistakes

- Raising samples as the first and only response to noise
- No denoising
- Fireflies treated with samples instead of light size or clamping
- Bounces left at default for an interior, giving unrealistic darkness
- Volumetrics added without noticing the render time doubled

## Related

[[3D & Blender Knowledge/15 - Optimization & Performance/Render Time|Render Time]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Render Failures|Render Failures]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Cycles sampling, adaptive sampling, denoising, light paths and
clamping. The square-root relationship is a property of Monte Carlo estimation.
