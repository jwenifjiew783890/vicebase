---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Broken Modifiers

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

A modifier produces nothing, the wrong result, or
something that differs between viewport and render.

## Likely causes

1. **Wrong stack order** - the most common by far
2. **Viewport visibility off** while render visibility is on, or the reverse
3. **Unapplied scale**, making offsets and widths inconsistent
4. **A required input missing** - Boolean with no object, Mirror with no origin on the plane,
   Shrinkwrap with no target
5. **Non-manifold input** where the modifier requires closed geometry
6. **Modifier depends on a vertex group or attribute** that does not exist or is misnamed
7. **Evaluation order with other objects** - a modifier referencing an object that itself has
   modifiers

## Diagnosis

1. **Disable the whole stack**, then re-enable from the top one at a time. The one that introduces
   the problem is the one to examine.
2. Check the **four visibility toggles** on each modifier - edit mode, cage, viewport, render.
3. Check object **scale** in the N panel.
4. Check any referenced objects, vertex groups or attributes actually exist and are named exactly
   right.
5. Compare viewport against a test render.

## Evidence to collect

- The stack order, top to bottom
- Per-modifier viewport and render toggle states
- Object scale
- Whether the problem persists with a single modifier only

## Safest fix

- Reorder: **generate, then smooth, then deform**
- Apply scale
- Supply the missing input
- Fix topology before modifiers that need manifold input
- Correct the vertex group or attribute name

**Do not apply the stack to "fix" it.** That destroys the evidence and the revisability.

## Verification

Toggle the modifier off and on and confirm the change is what you intended. Then render, because
viewport and render evaluate differently.

## Common mistakes

- Applying modifiers to escape a problem, losing all revisability
- Assuming viewport appearance equals render
- Adding a second modifier to compensate for the first being in the wrong place
- Subdivision render level left far above viewport, so the render is unexpectedly heavy

## Prevention

Name modifiers when a stack grows beyond three. Keep the order convention consistent across a
project.

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Modifiers|Modifiers]]

## Sources

Blender Manual (CC-BY-SA 4.0) - modifier stack evaluation and visibility controls.
