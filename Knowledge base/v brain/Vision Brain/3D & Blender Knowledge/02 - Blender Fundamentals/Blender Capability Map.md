---
type: note
domain: 3D & Blender Knowledge
section: 02 - Blender Fundamentals
created: 2026-09-03
---

# Blender Capability Map

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals|Blender Fundamentals]]

## What it is

What Blender can actually do, and which subsystem does it. The purpose is **task routing**: given a
job, know immediately whether Blender covers it, which tool applies, and which note to read.

## The capability surface

| Need | Blender subsystem | Read |
| --- | --- | --- |
| Model an object | Mesh editing, modifiers | [[3D & Blender Knowledge/03 - Modelling/00 - Modelling\|Modelling]] |
| Mechanical / manufactured object | Poly + bevel + weighted normals | [[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface\|Hard Surface]] |
| Organic form | Sculpt, remesh, retopology | [[3D & Blender Knowledge/05 - Organic & Sculpting/00 - Organic & Sculpting\|Organic & Sculpting]] |
| Generate geometry from rules | Geometry Nodes | [[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/00 - Procedural & Geometry Nodes\|Procedural & Geometry Nodes]] |
| Surface appearance | Shader nodes, Principled BSDF | [[3D & Blender Knowledge/07 - Materials & Shaders/00 - Materials & Shaders\|Materials & Shaders]] |
| Light a scene | Light objects, world, HDRI | [[3D & Blender Knowledge/08 - Lighting/00 - Lighting\|Lighting]] |
| Photoreal image | Cycles | [[3D & Blender Knowledge/10 - Rendering/00 - Rendering\|Rendering]] |
| Fast / real-time image | EEVEE | [[3D & Blender Knowledge/10 - Rendering/Cycles vs EEVEE\|Cycles vs EEVEE]] |
| Animate anything | Keyframes, drivers, NLA | [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging\|Animation & Rigging]] |
| Deform a character | Armature, weights, shape keys | [[3D & Blender Knowledge/11 - Animation & Rigging/Skinning & Weight Painting\|Skinning & Weight Painting]] |
| Physics | Rigid body, cloth, soft body, fluid, gas | [[3D & Blender Knowledge/12 - Simulation/00 - Simulation\|Simulation]] |
| Post-process a render | Compositor nodes | [[3D & Blender Knowledge/20 - VFX & Compositing/Compositor Fundamentals\|Compositor Fundamentals]] |
| Track real camera motion | Motion tracker | [[3D & Blender Knowledge/20 - VFX & Compositing/Camera Tracking & Matchmoving\|Camera Tracking & Matchmoving]] |
| Green screen | Keying nodes | [[3D & Blender Knowledge/20 - VFX & Compositing/Keying & Green Screen\|Keying & Green Screen]] |
| Rotoscope / mask | Mask editor | [[3D & Blender Knowledge/20 - VFX & Compositing/Masking & Rotoscoping\|Masking & Rotoscoping]] |
| 2D drawing / animation | Grease Pencil | [[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/Grease Pencil Fundamentals\|Grease Pencil Fundamentals]] |
| Cut video, add audio | Video Sequencer | [[3D & Blender Knowledge/20 - VFX & Compositing/Video Sequence Editor & Audio\|Video Sequence Editor & Audio]] |
| Game asset | High-to-low, baking, LODs | [[3D & Blender Knowledge/22 - Game & Real-Time Assets/00 - Game & Real-Time Assets\|Game & Real-Time Assets]] |
| Building visualisation | Precision modelling, archviz lighting | [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization\|Architecture & Visualization]] |
| Product image | Studio lighting, hard surface | [[3D & Blender Knowledge/23 - Product & Technical Visualization/Product Visualisation\|Product Visualisation]] |
| Physical object | Mesh repair, 3D print toolbox | [[3D & Blender Knowledge/23 - Product & Technical Visualization/3D Printing Preparation\|3D Printing Preparation]] |
| Automate anything | `bpy`, headless mode | [[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation\|Python & Automation]] |

## Capabilities that are easy to overlook

Worth knowing exist, because not knowing means reaching for another application unnecessarily:

- **A full node compositor** - most "needs a re-render" adjustments do not
- **Motion tracking with camera *and* object solving**, plus plane tracks
- **A mask editor** whose masks can be driven by tracking data
- **A video editor with audio** - enough for assembly, animatics and timing
- **Grease Pencil as true 3D-space 2D** - storyboards, 2D animation, annotation
- **Headless operation** - `blender --background --python`, the basis of all automation
- **Drivers** - any property can drive any other, without scripting
- **Library linking and overrides** - real asset reuse across files
- **The Asset Browser** - a proper component library
- **Shadow catcher and holdout** objects - the mechanism for compositing CG into plates
- **Cryptomatte** - per-object mattes for free at render time
- **The 3D Print Toolbox** - bundled mesh validation

## Where Blender is weak or absent

Being accurate about this prevents wasted effort:

- **No built-in fracture system** in the core distribution - destruction is assembled from add-ons
  or nodes plus rigid bodies
- **No dedicated crowd system** - crowds are instancing plus animation, not a solver
- **CAD precision and parametric history** - Blender is a mesh modeller, not a CAD kernel. Exact
  boolean history, constraints-based sketching and NURBS solids are not its domain.
- **Complex multi-track video editing and grading** - the sequencer is capable but not a finishing
  tool
- **Very large scene management** compared with dedicated pipeline tools

## How to use this note

Given a task: find the row, read the linked section MOC, then the specific note. If the task is not
on this map, check the weakness list before assuming Blender covers it.

## Related

[[3D & Blender Knowledge/00 - 3D & Blender Knowledge|Domain index]] ·
[[3D & Blender Knowledge/01 - Modelling Method|Modelling Method]]

## Sources

Blender Manual (docs.blender.org/manual, CC-BY-SA 4.0) - the feature set described. Capability
assessments and the weakness list reflect the distribution as of **Blender 5.2 LTS** and are
practitioner judgement; re-check after major releases.
