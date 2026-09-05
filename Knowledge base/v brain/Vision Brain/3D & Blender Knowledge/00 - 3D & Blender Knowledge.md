---
type: MOC
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# 3D & Blender Knowledge

The 3D domain of the Vision Brain. What Vision consults when it models, textures, lights,
renders, automates or debugs anything in Blender.

Part of [[Vision Brain]].

> [!important] How this domain is meant to be used
> **Retrieval is on demand and scoped.** Nothing here is copied into Open WebUI Knowledge,
> embedded wholesale, or mirrored into a second store. It is reached live through the Obsidian
> MCP tools, and only the notes a task actually needs are read. The vault stays the source of
> truth.

## The two shelves

**The six notes at this level are the always-applicable ones.** They are deliberately the only
markdown files in the domain root, because Vision's n8n Knowledge Retriever lists a domain folder
non-recursively and takes at most six notes. Anything an agent should have *by default* lives
here; everything else is reached by search.

| | Note | Read it when |
| --- | --- | --- |
| 01 | [[3D & Blender Knowledge/01 - Modelling Method\|Modelling Method]] | Starting any 3D task — the order of operations and which technique to choose |
| 02 | [[3D & Blender Knowledge/02 - Blender Engineering Constraints\|Blender Engineering Constraints]] | Touching transforms, modifiers, normals, render engines or the Python API |
| 03 | [[3D & Blender Knowledge/03 - Scene Quality Checklist\|Scene Quality Checklist]] | Before declaring any stage finished, and before export |
| 04 | [[3D & Blender Knowledge/04 - Debugging Method (3D)\|Debugging Method (3D)]] | Something is wrong and the cause is unknown |
| 05 | [[3D & Blender Knowledge/05 - Failure Patterns (3D)\|Failure Patterns (3D)]] | Before committing to an approach |
| 99 | [[3D & Blender Knowledge/99 - Sources & Provenance\|Sources & Provenance]] | Checking where a claim came from, or how strong it is |

## Sections

Reached by search when a task needs them.

| # | Section | Holds |
| --- | --- | --- |
| 01 | [[3D & Blender Knowledge/01 - 3D Fundamentals/00 - 3D Fundamentals\|3D Fundamentals]] | Coordinates, transforms, meshes, normals, topology, UVs — true in any 3D application |
| 02 | [[3D & Blender Knowledge/02 - Blender Fundamentals/00 - Blender Fundamentals\|Blender Fundamentals]] | Objects and data, collections, modifiers, constraints, linking, the asset browser |
| 03 | [[3D & Blender Knowledge/03 - Modelling/00 - Modelling\|Modelling]] | Blockout, subdivision, booleans, retopology, symmetry, precision work |
| 04 | [[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface\|Hard Surface]] | Mechanical and manufactured objects, bevel discipline, weighted normals |
| 05 | [[3D & Blender Knowledge/05 - Organic & Sculpting/00 - Organic & Sculpting\|Organic & Sculpting]] | Sculpt workflow, remeshing, multiresolution, baking displacement |
| 06 | [[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/00 - Procedural & Geometry Nodes\|Procedural & Geometry Nodes]] | Node fundamentals, attributes, instancing, procedural assets |
| 07 | [[3D & Blender Knowledge/07 - Materials & Shaders/00 - Materials & Shaders\|Materials & Shaders]] | Principled BSDF, PBR values, texture workflow, shader debugging |
| 08 | [[3D & Blender Knowledge/08 - Lighting/00 - Lighting\|Lighting]] | Three-point, studio, natural, HDRI, volumetrics, mood |
| 09 | [[3D & Blender Knowledge/09 - Cameras & Composition/00 - Cameras & Composition\|Cameras & Composition]] | Focal length, perspective, framing, camera matching |
| 10 | [[3D & Blender Knowledge/10 - Rendering/00 - Rendering\|Rendering]] | Cycles, EEVEE, sampling, denoising, colour management, output |
| 11 | [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging\|Animation & Rigging]] | Keyframes, interpolation, armatures, constraints, IK/FK |
| 12 | [[3D & Blender Knowledge/12 - Simulation/00 - Simulation\|Simulation]] | Rigid body, cloth, particles, fluid, smoke — and why they explode |
| 13 | [[3D & Blender Knowledge/13 - Environment & Scene Design/00 - Environment & Scene Design\|Environment & Scene Design]] | Scene composition, scattering, modular kits, set dressing |
| 14 | [[3D & Blender Knowledge/14 - Architecture & Visualization/00 - Architecture & Visualization\|Architecture & Visualization]] | Plans to 3D, walls/openings, interiors, exteriors, archviz lighting and presentation |
| 15 | [[3D & Blender Knowledge/15 - Optimization & Performance/00 - Optimization & Performance\|Optimization & Performance]] | Polygon and texture budgets, VRAM, render time, scene weight |
| 16 | [[3D & Blender Knowledge/16 - Add-ons & Pipelines/00 - Add-ons & Pipelines\|Add-ons & Pipelines]] | Extensions, asset libraries, import/export, interchange formats |
| 17 | [[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation\|Python & Automation]] | `bpy`, safe scripting, batch operations, generated-scene validation |
| 18 | [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting\|Debugging & Troubleshooting]] | One procedure per failure class: cause, diagnosis, fix, verification, prevention |
| 19 | [[3D & Blender Knowledge/19 - Production Workflows/00 - Production Workflows\|Production Workflows]] | How experienced artists actually work: planning, versioning, hygiene, export discipline |
| 20 | [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing\|VFX & Compositing]] | Compositor nodes, plate preparation, camera tracking, keying, rotoscoping, CG integration, video and audio |
| 21 | [[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/00 - Grease Pencil & Motion Design\|Grease Pencil & Motion Design]] | 2D drawing in 3D space, storyboarding and previz, motion graphics and text animation |
| 22 | [[3D & Blender Knowledge/22 - Game & Real-Time Assets/00 - Game & Real-Time Assets\|Game & Real-Time Assets]] | High-to-low baking, LODs, real-time budgets, engine export and the conventions that differ per engine |
| 23 | [[3D & Blender Knowledge/23 - Product & Technical Visualization/00 - Product & Technical Visualization\|Product & Technical Visualization]] | Product imagery, technical and industrial illustration, and preparing meshes for 3D printing |

## What separates the sections

Sections **01** and **03–13** are transferable 3D knowledge — true in any package, though
expressed in Blender's terms. Section **02** is Blender-specific behaviour. Sections **14** and
**20–23** are output disciplines, each with its own conventions, deliverables and definition of
"finished": architecture, VFX, 2D and motion, real-time assets, and product or technical imagery.
Sections **17–19** are where an agent's mistakes actually happen, and are the most useful under
pressure.

If the task is not obviously in one section, start from
[[3D & Blender Knowledge/02 - Blender Fundamentals/Blender Capability Map|Blender Capability Map]],
which routes a job to the subsystem that does it — and says plainly where Blender is weak.

Never present a practitioner heuristic as documented behaviour. See
[[3D & Blender Knowledge/99 - Sources & Provenance|Sources & Provenance]].

## Rules for adding to this domain

1. **Actionable or absent.** A note earns its place by changing what an artist or agent would do.
   Restating what a button is called does not.
2. **Decisions, not button locations.** UI positions change between versions; the reason to pick
   one technique over another does not.
3. **Failure modes are the payload.** Knowing how something breaks is worth more than knowing how
   it works.
4. **Provenance.** Documented behaviour cites the manual. Judgement is labelled as judgement.
5. **Link, do not duplicate.** One concept, one note.
6. **Keep the root at six.** Adding a seventh always-on note means demoting one first.

## Related domains

[[Coding Knowledge/00 - Coding Knowledge|Coding & Engineering Knowledge]] — for the Python that
drives Blender, and for the general debugging discipline this domain's method mirrors.
