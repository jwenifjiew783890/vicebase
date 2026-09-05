---
type: note
domain: 3D & Blender Knowledge
section: 17 - Python & Automation
created: 2026-09-03
---

# Safe Scripting Practices

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation|Python & Automation]]

## What it is

The documented constraints that make the difference between a script that works once and one that
works. All four below are stated in Blender's own API documentation.

## 1. Names are not guaranteed

A common mistake is assuming newly created data receives the name requested. Blender enforces
uniqueness, so requesting "Wall" when "Wall" exists yields "Wall.001".

```python
# Wrong - assumes the name was granted
bpy.data.objects.new("Wall", mesh)
obj = bpy.data.objects["Wall"]        # may be a different, older object

# Right - use what was returned
obj = bpy.data.objects.new("Wall", mesh)
```

Name lookups after creation are a reliable source of scripts that corrupt the wrong object.

## 2. Python objects wrapping Blender data have limited lifetime

The documentation is explicit: these wrappers are created on demand and deleted when no longer
referenced, and **Blender may free the underlying internal data**, after which a retained Python
reference can lead to invalid memory access.

Consequences:

- Do not store Blender data references persistently - across operators, in module globals, in
  handlers that outlive the operation
- Do not attach your own attributes to them expecting persistence
- Re-acquire references rather than caching them across operations that modify the scene

Where persistence is genuinely needed, store a **name or an identifier** and look it up again,
accepting that the lookup may fail.

## 3. Python threads are not supported

The documentation states this without qualification: Python threads cause Blender to crash in ways
that are hard to diagnose - including during Cycles renders and with drivers.

Threads work only when they complete before the script does, for example by joining while the main
Blender thread is blocked. Note that some standard-library facilities use threads internally.

For genuinely independent work, the documentation recommends `multiprocessing` instead.

**For generated code the rule is simply: do not use threads inside Blender.**

## 4. Mode matters for mesh access

Mesh data is not reliably accessible while in Edit Mode, because the edit-mode representation is
separate. Either switch to Object Mode before reading mesh data, or use `bmesh` from the edit-mode
data properly.

## General discipline

- **Fail loudly.** Validate inputs and raise, rather than continuing on bad state.
- **Make it idempotent** where possible - running twice should not create two of everything.
- **Do not silently overwrite.** Check whether an object exists before replacing it.
- **Print to the console** - see
  [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Script Failures|Script Failures]].
- **Never write to the user's file without saving a copy first**, if the script is destructive.

## Common mistakes

- Name lookup after creation
- Cached data references used after a scene change
- Threads
- Reading mesh data in Edit Mode
- Scripts that half-complete and leave the scene in an inconsistent state

## Related

[[3D & Blender Knowledge/17 - Python & Automation/Operators vs Direct Data|Operators vs Direct Data]] ·
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]]

## Sources

Blender Python API documentation (docs.blender.org/api), *Best Practice* and *Gotchas* -
specifically the pages on data names, internal data and Python object lifetime, threading, and
modes and mesh access. Restated in decision terms rather than quoted.
