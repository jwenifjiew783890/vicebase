---
type: note
domain: 3D & Blender Knowledge
section: 15 - Optimization & Performance
created: 2026-09-03
---

# VRAM & Memory

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/15 - Optimization & Performance/00 - Optimization & Performance|Optimization & Performance]]

## What it is

GPU rendering requires the scene to fit in graphics memory. Exceeding it is a hard failure, not a
slowdown.

## What consumes VRAM

In rough order:

1. **Textures** - usually the largest consumer. A 4K texture set per material across many
   materials adds up quickly.
2. **Geometry after modifiers** - subdivision at render level, realised instances
3. **Volumes** - smoke, fire and fog caches are very large
4. **Simulation caches**

## Symptoms

- Render fails outright with an out-of-memory error
- Blender falls back to CPU, and the render becomes dramatically slower - often mistaken for a
  "slow scene" rather than a memory failure
- System becomes unresponsive during render

**A render that suddenly takes ten times longer has often fallen back to CPU.** Check memory before
optimising anything else.

## Reducing it

| Action | Effect |
| --- | --- |
| **Reduce texture resolution** | Largest single win. A 2K map is a quarter of a 4K one. |
| **Simplify texture limit** | Global cap without editing every material |
| **Lower subdivision render levels** | Direct geometry reduction |
| **Keep instances unrealised** | Instances share geometry |
| **Fewer unique materials** | Each carries its own textures |
| **Lower volume resolution** | Volumes are disproportionately expensive |

## Textures deserve attention first

Texture resolution should be proportionate to **screen coverage**. A 4K map on an object occupying
50 pixels is 4 million pixels of texture for 50 pixels of image.

Audit: for each material, ask how large the object appears in frame. Most scenes have several
objects with far more texture than they need.

## Out-of-core and hybrid rendering

Some configurations allow spilling to system memory, which works but is slow. It is a safety net,
not a plan.

## Common mistakes

- Assuming a slow render is a sampling problem when it is a CPU fallback
- 4K textures everywhere by default
- Realising instances
- Volumes at full resolution during look development
- Not checking memory before a long render

## Related

[[3D & Blender Knowledge/15 - Optimization & Performance/Render Time|Render Time]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Performance & Memory Problems|Performance & Memory Problems]]

## Sources

Blender Manual (CC-BY-SA 4.0) - Cycles device settings, memory, Simplify.
