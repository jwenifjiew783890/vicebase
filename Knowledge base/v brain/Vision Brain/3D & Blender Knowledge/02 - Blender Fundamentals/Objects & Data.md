---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Objects & Data

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

Blender separates the **object** from its **data-block**. The object holds the transform, the
modifier stack and the relationships. The data-block holds the mesh, curve, light or camera.

One data-block can have many users. Two objects sharing a mesh are *linked duplicates* - edit one,
both change. This is the mechanism behind instancing, and behind a class of surprises.

## Why it matters

- **Linked duplicate** (Alt+D) shares mesh data. Cheap in memory. Editing one edits all.
- **Full duplicate** (Shift+D) copies the data. Independent, and costs memory.

Choosing the wrong one produces either "I edited one chair and all forty changed" or a scene that
is forty times heavier than it needs to be.

## Users and orphan data

A data-block with zero users is **orphaned**. It survives in the file until saved and reloaded, or
explicitly purged. This is why deleting objects does not shrink the file.

File > Clean Up > Purge removes unused data. Do it before shipping a file, not habitually
mid-project - purge is not undoable in a useful way.

The Outliner in **Blender File** or **Orphan Data** display mode shows what actually exists,
independent of what is visible in the viewport.

## The fake user

A data-block can be given a "fake user" so it survives purging even with no real users. Used for
materials and node groups you want to keep in a library file. Also a common reason a file will not
shrink.

## Common mistakes

- Using Shift+D everywhere and wondering why the scene is enormous
- Using Alt+D then being surprised that editing propagates
- Assuming deleting an object frees its mesh
- Purging without checking what is about to disappear

## Related

[[3D & Blender Knowledge/02 - Blender Fundamentals/Linking, Appending & Assets|Linking, Appending & Assets]] ·
[[3D & Blender Knowledge/15 - Optimization & Performance/Scene Weight|Scene Weight]]

## Sources

Blender Manual (CC-BY-SA 4.0) - data-blocks, users, orphan data and purging.
