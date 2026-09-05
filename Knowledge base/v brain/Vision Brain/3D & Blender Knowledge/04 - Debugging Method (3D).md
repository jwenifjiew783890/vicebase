---
type: note
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# Debugging Method (3D)

How to find the cause of a 3D problem instead of guessing at it.

3D debugging has a specific trap: **the symptom appears in the render, but the cause is almost
never in the renderer.** Shading looks wrong → the artist opens the shader editor → the actual
cause was a flipped normal or a non-uniform scale three steps upstream. Most wasted time in 3D
comes from debugging the wrong layer.

## The layer order

Check in this order. Each layer is cheaper to check than the one after it, and a fault in an
early layer produces convincing symptoms in every later one.

```
1. Transforms   scale applied? origin sane? object actually where it appears?
2. Geometry     normals? manifold? doubles? degenerate faces?
3. Modifiers    stack order? something disabled in viewport but on in render?
4. UVs          unwrapped? overlapping? outside 0-1 where it matters?
5. Materials    node actually connected? correct colour space?
6. Lighting     is anything emitting? is it inside geometry?
7. Camera       clipping? focal length? is the object behind the near plane?
8. Render       engine, samples, visibility flags, view layer
```

**Never start at layer 5 because the symptom looks like a material problem.** It usually is not.

## The procedure

1. **Reproduce.** Confirm the problem is present and consistent. Intermittent problems in 3D are
   usually viewport-versus-render differences, not randomness.
2. **Isolate.** Move the suspect object to an empty scene, or hide everything else. Half of all
   "broken material" reports are one object casting a shadow onto another.
3. **Bisect.** Disable the modifier stack from the bottom up. Turn off lights one at a time.
   Reconnect shader nodes one at a time. The step that changes the symptom contains the cause.
4. **Collect evidence** before changing anything (below).
5. **Fix the cause, not the symptom.** Increasing samples to hide fireflies is not fixing them.
6. **Verify** in a render, not the viewport — EEVEE and Cycles disagree, and the viewport lies.
7. **Record it** if it cost more than a few minutes. See
   [[3D & Blender Knowledge/05 - Failure Patterns (3D)|Failure Patterns]].

## Evidence to collect

Before you change anything, gather what tells you where you are:

| Evidence | Reveals |
| --- | --- |
| Statistics overlay (verts/faces/objects) | Runaway subdivision, duplicated geometry, an array gone wrong |
| Face Orientation overlay | Flipped normals — red is inward |
| Object scale in the N panel | Non-uniform scale, the invisible cause of many bevel and physics faults |
| Wireframe / edit-mode view | N-gons, doubles, interior faces, degenerate geometry |
| System Console (Window → Toggle System Console) | Python errors and add-on tracebacks that never surface in the UI |
| Outliner → Blender File / Orphan Data | What is actually in the file, and what is unused |
| Render vs viewport comparison | Modifier or object visibility flags that differ between the two |
| Compositor node tree | An image altered after render by a node nobody remembers adding |

**The System Console is the single most under-used diagnostic in Blender.** If a script or add-on
misbehaves, the traceback is there and nowhere else.

## Symptom → first suspect

A lookup for the recurring ones. Full procedures live in
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|section 18]].

| Symptom | Check first |
| --- | --- |
| Shading looks blotchy or dark in patches | Normals (Face Orientation), then custom split normals |
| Bevel width inconsistent around the object | Object scale not applied |
| Boolean produces holes or garbage | Non-manifold input, coplanar faces, or overlapping geometry |
| Object invisible in render, visible in viewport | Render visibility toggle, or the camera/view-layer/collection is excluded |
| Texture missing or magenta | Broken file path, or a relative path after moving the .blend |
| Material black | No light reaching it, or normals inverted, or a node disconnected |
| Render far slower than expected | Subdivision render levels, volumetrics, too many light bounces, or a runaway modifier |
| Scene will not fit in VRAM | Texture resolution and subdivision levels, in that order |
| Sculpt brush does nothing | Wrong object mode, hidden mask, or multires level at 0 |
| Simulation explodes or passes through | Substeps too low, scale not applied, or collision margins |
| Python script fails silently | Look in the System Console — it did not fail silently |

## Viewport versus render

A large class of "unreproducible" bugs is simply that the viewport is not the renderer:

- Modifiers have **separate viewport and render visibility toggles** — a subdivision set to 1 in
  viewport and 3 in render is the usual cause of "it was fine until I rendered".
- Objects have **separate viewport and render visibility**.
- Collections can be **excluded from a view layer** while still appearing in the outliner.
- EEVEE approximates what Cycles simulates. A material that reads correctly in EEVEE may be wrong
  in Cycles and vice versa.

**When viewport and render disagree, trust neither — find the flag that differs.**

## Common mistakes

- **Debugging the last thing changed** rather than the first layer that could produce the symptom.
- **Changing several things at once**, so the fix cannot be attributed.
- **Fixing the symptom**: raising samples, adding lights, scaling the object — each hides a cause
  and adds a second problem.
- **Trusting the viewport** for a render problem.
- **Rebuilding rather than diagnosing.** Rebuilding hides the cause, which returns.
- **Not saving before a destructive fix.** Incremental save first; the fix may be worse.

## Related

[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]] ·
[[3D & Blender Knowledge/05 - Failure Patterns (3D)|Failure Patterns]] ·
[[3D & Blender Knowledge/03 - Scene Quality Checklist|Scene Quality Checklist]]

## Sources

Practitioner synthesis. The layer order and the symptom table encode the causal structure of
Blender's evaluation pipeline as documented in the Blender Manual
(docs.blender.org/manual, CC-BY-SA 4.0); the diagnostic discipline itself is general and
consistent with [[Coding Knowledge/02 - Debugging Method|the software debugging method]].
