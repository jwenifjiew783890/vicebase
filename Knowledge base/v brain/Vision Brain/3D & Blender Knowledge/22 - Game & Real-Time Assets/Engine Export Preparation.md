---
type: note
domain: 3D & Blender Knowledge
section: 22 - Game & Real-Time Assets
created: 2026-09-03
---

# Engine Export Preparation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/22 - Game & Real-Time Assets/00 - Game & Real-Time Assets|Game & Real-Time Assets]]

## What it is

The specific preparation an asset needs before it will behave correctly in Unreal, Unity or a
similar engine.

## The recurring failures

| Problem | Cause | Fix |
| --- | --- | --- |
| Asset arrives 100x too large or small | Unit mismatch | Establish the engine's unit and export to it. Unreal works in centimetres; Unity in metres. |
| Asset lies on its side | Axis convention | Blender is Z-up; engines are commonly Y-up. Use the exporter's axis conversion deliberately. |
| Normals look inverted in surface detail | Normal map green channel | OpenGL vs DirectX convention - flip green for the target |
| Scale behaves oddly | Unapplied object scale | Apply scale before export |
| Smoothing wrong | Custom split normals lost or misread | Export normals explicitly; verify |
| Materials missing | Materials rarely transfer | Expect to rebuild in the engine; export maps, not shaders |
| Pivot in the wrong place | Origin not set | Set the origin where the engine needs it - usually base centre |

**Units and axis account for most import problems**, and both are settable at export.

## Before exporting

1. **Apply scale**, rotation where appropriate; transforms clean
2. **Origin at the correct point** - for a prop, usually the base centre so it sits on the ground
3. **Modifiers applied** or explicitly intended to travel
4. **Normals correct**; custom normals handled deliberately
5. **UVs present and named** - engines often expect a specific UV set order, with lightmap UVs as
   the second set
6. **Materials named**, texture maps exported separately
7. **Triangulate deliberately** rather than letting the exporter decide
8. **Name it** as the engine will show it

## Formats

- **FBX** - the long-standing default for engines; carries meshes, rigs and animation
- **glTF/GLB** - open, modern, well-suited to real-time and increasingly well-supported

Both are covered more generally in
[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Import, Export & Interchange|Import, Export & Interchange]];
this note is the engine-specific layer on top.

## Skinned meshes and animation

- Bone count limits may apply
- Keep the armature hierarchy clean - engines import what is there, including junk bones
- Bake animation where the rig uses constraints or drivers the engine cannot evaluate
- Test the deformation in the engine, not only in Blender

## Validate in the engine

**The export is not done until the engine has opened it.** Check scale against a known reference
object, orientation, smoothing, UV sets, and material slots. Every problem above is visible within
a minute of import and expensive to discover later.

## Common mistakes

- Not setting units for the target engine
- Wrong axis conversion
- Origin left at world centre
- Only one UV set on an asset needing a lightmap
- Expecting Blender materials to arrive intact
- Never opening the asset in the engine

## Related

[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Import, Export & Interchange|Import, Export & Interchange]] ·
[[3D & Blender Knowledge/19 - Production Workflows/Export Discipline|Export Discipline]]

## Sources

Practitioner synthesis. Exporter options, axis conversion and unit scaling are documented in the
Blender Manual (CC-BY-SA 4.0). Engine-specific unit conventions are those engines' documented
defaults and should be confirmed against the version in use.
