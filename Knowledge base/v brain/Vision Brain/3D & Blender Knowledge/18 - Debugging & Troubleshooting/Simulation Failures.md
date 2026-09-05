---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Simulation Failures

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

A simulation explodes, passes through
colliders, jitters, or does not react to changes.

## Likely causes

1. **Unapplied scale** - collision shapes do not match the visible mesh
2. **Wrong scene scale**, so gravity and mass are wrong
3. **Too few substeps**, letting fast objects tunnel through colliders
4. **Collision margin** too small or too large
5. **Thin or single-sided colliders**
6. **Stale cache** - the scene changed but the cache did not
7. **Simulation not started from frame 1**
8. **Overlapping geometry at the start frame**, so the solver begins in an impossible state

## Diagnosis

1. **Check and apply scale on everything involved.** This resolves a large share of cases.
2. Check scene units and object real dimensions.
3. **Clear the cache and replay from frame 1.** If the behaviour changes, the cache was stale.
4. Raise substeps substantially and re-test. If it improves, it was tunnelling.
5. Check whether objects intersect at the start frame.
6. Replace the collider with a simple low-poly proxy - if that fixes it, collider complexity was
   the problem.

## Evidence to collect

- Object scale values
- Substep and collision margin settings
- Whether behaviour changes after clearing the cache
- Whether the simulation was played from frame 1
- Cache size and whether it is baked

## Safest fix

- Apply scale on all participating objects
- Increase substeps - fast motion and thin colliders both demand more
- Adjust collision margin to a value proportionate to the scene scale
- Give thin colliders thickness with Solidify
- Use a simplified proxy collider
- **Clear the cache and rebake** after any upstream change

## Verification

Play the full simulation from frame 1 after baking. Never judge from a partially cached playback,
and never render an unbaked simulation.

## Common mistakes

- Debugging a stale cache for an hour
- Increasing resolution before the behaviour is correct
- Using the render mesh as the collider
- Starting playback mid-sequence
- Rendering unbaked, so the render differs from what was previewed

## Prevention

Apply scale before any physics. Bake before rendering. Clear the cache as a reflex after changing
anything upstream. Test at low resolution first.

## Related

[[3D & Blender Knowledge/12 - Simulation/Simulation Fundamentals|Simulation Fundamentals]]

## Sources

Blender Manual (CC-BY-SA 4.0) - physics settings, substeps, collision margins, caching and baking.
