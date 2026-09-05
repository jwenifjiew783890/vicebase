---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Objects Disappearing

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

An object is in the outliner but not in the
viewport, or visible in the viewport but missing from the render.

## Likely causes

1. **Render visibility disabled** while viewport visibility is on - the most common
2. **Collection excluded from the view layer** - the checkbox, not the eye
3. **Hidden** with H
4. **Disabled in viewport** with the monitor icon
5. **Camera clipping** - object nearer than clip start or beyond clip end
6. **Object outside the camera frustum**
7. **Scaled to zero**, or moved far from the origin
8. **Modifier removing the geometry** - a Mask, a Boolean consuming everything, an Array with zero
   count
9. **Material fully transparent**
10. **Object is inside another object**

## Diagnosis

**First, determine whether the object exists or is merely not shown.** The Outliner in Blender File
mode shows what exists regardless of visibility.

Then:

1. Check all **four visibility controls** - hide, disable viewport, disable render, and the
   collection exclude checkbox. Enable the filter icons in the Outliner to see all of them at once.
2. Select the object in the Outliner and press **Numpad-period** to frame it. If the view jumps far
   away, it is misplaced rather than hidden.
3. Check **dimensions** in the N panel. Zero means scaled to nothing.
4. Check **camera clip start and end**.
5. Disable modifiers.

## Evidence to collect

- State of all four visibility toggles
- Object dimensions and location
- Camera clip values
- Whether it appears with modifiers disabled

## Safest fix

Enable the specific control that is off. Do not "fix" by re-creating the object - it exists, and
re-creating loses its material, modifiers and relationships.

For clipping: adjust clip start and end. A very small clip start with a very large clip end causes
depth precision problems, so keep the range as tight as the scene allows.

## Verification

Render a test frame. Viewport visibility does not prove render visibility - they are separate
settings and that is the whole point of this failure class.

## Common mistakes

- Checking only the eye icon
- Re-creating an object that was merely hidden
- Enormous clip ranges causing z-fighting elsewhere
- Not realising collection exclusion is distinct from collection hiding

## Prevention

Use collections deliberately, keep reference and blockout geometry in a clearly named collection
excluded from render, and check the render-visibility column before final renders.

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Collections & Scene Organisation|Collections & Scene Organisation]]

## Sources

Blender Manual (CC-BY-SA 4.0) - visibility controls, view layers, camera clipping.
