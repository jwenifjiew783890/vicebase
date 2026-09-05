---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Render Failures

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

A render crashes, hangs, produces black frames, or
looks nothing like the viewport.

## Likely causes

1. **Out of GPU memory** - fails, or silently falls back to CPU and becomes very slow
2. **No light in the scene**, giving black output
3. **Camera inside geometry**, or no camera at all
4. **Render visibility** differing from viewport
5. **Subdivision render levels** far above viewport, exhausting memory or time
6. **Volumetrics** at high resolution
7. **Compositor node tree** altering the output after render
8. **Colour management / view transform** making the image look wrong
9. **Driver or GPU instability** on long renders

## Diagnosis

1. **Render a small region at low resolution first.** If that works, it is a scale problem - memory
   or time - not a fundamental fault.
2. Watch memory during the render. A fallback to CPU is the usual explanation for an unexpectedly
   slow render.
3. Check the **compositor** - an unnoticed node is a classic cause of "the render does not match
   the viewport".
4. Check **colour management** - a changed view transform alters everything.
5. For black frames: is there a light, is the camera inside geometry, is anything in the view
   layer.
6. Disable **volumetrics** and re-test.
7. Test with a default scene to isolate whether the problem is the file or the installation.

## Evidence to collect

- Console output during render
- Memory usage at peak
- Whether a low-resolution region render succeeds
- Compositor state, and whether Use Nodes is enabled
- View transform setting

## Safest fix

Match the cause: reduce texture resolution or subdivision for memory; add or fix lighting; correct
render visibility; disable or simplify the compositor; set the intended view transform.

For instability on long renders, render in **smaller batches or frame ranges** rather than one
long job.

## Verification

Render the **actual final frame at final settings**, not a preview. Then look at it at 100%, not as
a thumbnail.

## Common mistakes

- Increasing samples when the problem is memory
- Not noticing a CPU fallback
- Forgetting the compositor exists
- Judging a render at thumbnail size
- Rendering a long animation without testing a single frame at final settings

## Prevention

Test-render one full-quality frame before committing to a sequence. Keep an eye on memory. Save
before long renders.

## Related

[[3D & Blender Knowledge/10 - Rendering/Cycles Sampling & Noise|Cycles Sampling & Noise]] ·
[[3D & Blender Knowledge/15 - Optimization & Performance/VRAM & Memory|VRAM & Memory]]

## Sources

Blender Manual (CC-BY-SA 4.0) - render settings, colour management, compositor, device settings.
