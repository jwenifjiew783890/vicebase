---
type: note
domain: 3D & Blender Knowledge
section: 17 - Python & Automation
created: 2026-09-03
---

# Operators vs Direct Data

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation|Python & Automation]]

## What it is

`bpy.ops` exposes the operations the UI performs. It is the obvious way to script Blender - and
usually the wrong one.

## What the documentation says

Blender's own API documentation states the limits plainly. Operators:

- **cannot be passed data** such as objects, meshes or materials to operate on - they use the
  **context** instead
- **return only success or cancellation**, not the result of the operation
- have a **poll function that can fail** where a direct API call would raise an exception
  explaining exactly what was wrong

The characteristic failure is:

```
RuntimeError: Operator bpy.ops.*.poll() failed, context is incorrect
```

This means the operator was called from a state it does not accept - typically the wrong area
type, wrong mode, or nothing suitable selected. The message does not say which.

## Why this matters for generated code

An agent writing a script that chains `bpy.ops` calls is writing code that:

- depends on selection and mode state that may not hold
- gives an unhelpful error when it fails
- carries full undo-push and dependency-graph overhead per call
- is slow in loops, because each call re-evaluates far more than the operation needs

## Prefer direct data

```python
# Fragile: depends on selection, mode and area
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.transform.translate(value=(0, 0, 1))

# Robust: no context dependency at all
obj.location.z += 1.0
```

```python
# Fragile
bpy.ops.object.modifier_add(type='SUBSURF')

# Robust, and returns the modifier so it can be configured
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 3
```

## When operators are the right choice

Some operations have no data-level equivalent, and then an operator is correct:

- complex mesh operations more easily done through `bmesh` or an operator
- import and export
- baking
- some sculpt and paint operations

When one is required, **override the context explicitly** rather than manipulating selection
globally, so the surrounding scene state is not disturbed.

## Common mistakes

- `bpy.ops` in a loop over many objects - slow and fragile
- Manipulating global selection to satisfy an operator, leaving the scene in a changed state
- Treating a poll failure as a Blender bug
- Not checking whether a direct API equivalent exists

## Related

[[3D & Blender Knowledge/17 - Python & Automation/Safe Scripting Practices|Safe Scripting Practices]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Script Failures|Script Failures]]

## Sources

Blender Python API documentation (docs.blender.org/api), *Gotchas: Using Operators* - the
limitations and the poll-failure behaviour are documented there. Restated, not quoted.
