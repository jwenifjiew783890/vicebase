---
type: note
domain: 3D & Blender Knowledge
section: 17 - Python & Automation
created: 2026-09-03
---

# bpy Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation|Python & Automation]]

## What it is

Blender's Python API. Three modules carry most work:

| Module | Holds |
| --- | --- |
| `bpy.data` | The actual data - objects, meshes, materials, scenes. Direct, context-free access. |
| `bpy.context` | What is currently active or selected. Depends on where the code runs. |
| `bpy.ops` | Operators - the same actions the UI performs. Context-dependent. |

Also useful: `bmesh` for mesh editing, `mathutils` for vectors and matrices.

## Data access is the reliable path

```python
import bpy

# Direct, context-independent, predictable
obj = bpy.data.objects["Cube"]
obj.location = (1.0, 2.0, 3.0)

mesh = bpy.data.meshes.new("MyMesh")
new_obj = bpy.data.objects.new("MyObject", mesh)
bpy.context.collection.objects.link(new_obj)
```

Creating data with `bpy.data.*.new()` does **not** put it in the scene. It must be linked to a
collection. This trips people constantly - the object exists but is invisible.

## Context

`bpy.context` reflects the current state - active object, selection, mode, area. Its contents
depend on **where the code runs**: a script in the text editor, a script run headless, and a
handler each see different contexts.

Code that relies on `bpy.context.active_object` is code that breaks when run from somewhere else.
Prefer explicit references.

## Collections and linking

```python
coll = bpy.data.collections.new("Props")
bpy.context.scene.collection.children.link(coll)
coll.objects.link(new_obj)
```

An object can be linked into several collections. Unlinking from all removes it from the scene but
does not delete the data - see
[[3D & Blender Knowledge/02 - Blender Fundamentals/Objects & Data|Objects & Data]].

## Headless

```
blender --background scene.blend --python script.py
```

Runs without a UI. Essential for batch work and automation. Note that in background mode much of
`bpy.context` is unavailable, which is another reason to avoid depending on it.

## Common mistakes

- Creating data and forgetting to link it, then wondering where the object went
- Depending on context that does not exist in background mode
- Assuming `bpy.data.objects["Name"]` will exist after creating "Name" - see
  [[3D & Blender Knowledge/17 - Python & Automation/Safe Scripting Practices|Safe Scripting Practices]]
- Using operators where direct data access would be simpler and more robust

## Related

[[3D & Blender Knowledge/17 - Python & Automation/Operators vs Direct Data|Operators vs Direct Data]] ·
[[Coding Knowledge/02 - Programming & Languages/Python|Python]]

## Sources

Blender Python API documentation (docs.blender.org/api) - API overview, data access, context.
