---
type: note
domain: 3D & Blender Knowledge
section: 06 - Procedural & Geometry Nodes
created: 2026-09-03
---

# Geometry Nodes Fundamentals

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/00 - Procedural & Geometry Nodes|Procedural & Geometry Nodes]]

## What it is

A node graph that takes geometry in and produces geometry out, evaluated as a modifier. Everything
in it is either **geometry**, a **field**, or a **single value**.

## The one concept that matters: fields

A **field** is a value that depends on context - it is computed *per element* rather than being one
number. Position is a field: every point has its own. A single float is not.

Sockets show this: a diamond socket takes a field; a circle takes a single value. **Most confusion
in geometry nodes is a field/value mismatch**, and the socket shape tells you immediately.

- **Capture Attribute** freezes a field onto geometry so it survives later operations
- **Named attributes** store per-element data on the geometry itself
- Field context matters: a field evaluated on points means something different from the same field
  evaluated on faces

## The data model

Geometry carries **domains** - points, edges, faces, face corners, curves, instances. An attribute
lives on a domain. Moving between domains (point to face, say) requires interpolation, and doing it
implicitly is a common source of surprise.

## The core operations

| Category | Nodes |
| --- | --- |
| Create | Mesh primitives, curve primitives |
| Read | Position, Normal, Index, Named Attribute |
| Select | Compare, Boolean maths, Separate Geometry |
| Distribute | Distribute Points on Faces, Instance on Points |
| Transform | Set Position, Transform Geometry, Rotate Instances |
| Combine | Join Geometry, Realize Instances |
| Utility | Map Range, Math, Random Value, Switch |

**Set Position** is the workhorse: nearly all procedural deformation is a field driving Set
Position.

## Instances versus realised geometry

Instances are references - cheap in memory, and many operations do not affect their contents.
**Realize Instances** converts them into actual geometry, which is expensive.

The rule: **stay instanced as long as possible, realise as late as possible, and only if you must.**
Realising ten thousand instances early is the standard cause of a geometry-node setup that hangs.

## Debugging a graph

- Use the **Viewer node** to see intermediate results. This is the equivalent of a print statement.
- Check the **spreadsheet** to see actual attribute values on actual domains.
- Check socket shapes when something will not connect - it is usually a field/value mismatch.
- Bisect: mute nodes from the end backwards until the problem disappears.

## Common mistakes

- Realising instances early and grinding the file to a halt
- Field/value confusion, then blaming the node
- Attributes lost because they were never captured before the operation that dropped them
- Building one enormous graph rather than named groups
- No Viewer node, so the graph is debugged by guessing

## Related

[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Instancing & Scattering|Instancing & Scattering]] ·
[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Geometry Node Errors|Geometry Node Errors]]

## Sources

Blender Manual (CC-BY-SA 4.0) - geometry nodes, fields, attributes, domains, instances. Debugging
approach is practitioner judgement.
