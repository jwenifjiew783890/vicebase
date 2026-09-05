---
type: note
domain: 3D & Blender Knowledge
section: 11 - Animation & Rigging
created: 2026-09-03
---

# Shape Keys & Drivers

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging|Animation & Rigging]]

## What it is

**Shape keys** store alternative vertex positions for one mesh and blend between them. **Drivers**
connect one property to another so a value moves automatically.

Together they are how non-skeletal deformation is authored - facial expressions, corrective fixes,
mechanical states, motion-graphics transitions.

## Shape keys

- The **Basis** key is the rest shape; every other key is a stored offset from it
- Keys blend additively, so several can be active at once
- The topology must not change - shape keys store per-vertex positions, so adding or deleting
  geometry after creating keys invalidates them

**This is the constraint that bites**: finish the topology *before* authoring shape keys. Changing
the mesh afterwards means rebuilding them.

## What shape keys are for

| Use | Why not bones |
| --- | --- |
| Facial expression | Faces deform in ways bones approximate badly |
| Corrective shapes | Fixing a joint that collapses at extreme rotation |
| Mechanical states | A panel that folds, a valve that opens |
| Blend transitions | Morphing between two authored forms |

## Corrective shape keys

The important professional use. A shoulder or elbow will collapse or crease at extreme rotation
regardless of weighting. A corrective shape key, **driven by the bone's rotation**, fixes the shape
exactly where it fails and contributes nothing elsewhere.

This is the standard solution to "the deformation is almost right but breaks at the extremes".

## Drivers

A driver makes a property a function of another - typically a bone rotation driving a shape key
value.

- Driven by: bone transforms, object properties, custom properties, or a scripted expression
- The usual pattern: a **custom property on a control bone** drives several shape keys, giving the
  animator one slider

**Drivers are what turn a rig into an interface.** An animator should move a control, not type
values into shape key sliders.

## Debugging drivers

- A driver that does nothing usually has an invalid variable path - check the target still exists
  and was not renamed
- Circular dependencies produce evaluation failures; the console reports them
- Renaming bones or objects breaks driver paths silently
- Expressions are evaluated in a restricted context; complex logic belongs in the rig, not the
  expression

## Common mistakes

- Editing topology after creating shape keys
- Sculpting a whole expression when a corrective key on the failing area would do
- Exposing raw shape key sliders instead of driving them from controls
- Renaming things and breaking driver paths
- Shape keys where a bone would be simpler and cheaper

## Related

[[3D & Blender Knowledge/11 - Animation & Rigging/Skinning & Weight Painting|Skinning & Weight Painting]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Facial Animation & Lip Sync|Facial Animation & Lip Sync]] ·
[[3D & Blender Knowledge/02 - Blender Fundamentals/Constraints|Constraints]]

## Sources

Blender Manual (docs.blender.org/manual, CC-BY-SA 4.0) - shape keys, drivers, driver variables and
expressions. Corrective-shape practice is standard rigging craft.
