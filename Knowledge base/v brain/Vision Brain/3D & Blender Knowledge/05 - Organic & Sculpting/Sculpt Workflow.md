---
type: note
domain: 3D & Blender Knowledge
section: 05 - Organic & Sculpting
created: 2026-09-03
---

# Sculpt Workflow

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/05 - Organic & Sculpting/00 - Organic & Sculpting|Organic & Sculpting]]

## What it is

Modelling by pushing surface rather than placing vertices. Right for forms you find rather than
forms you specify.

## The two topology strategies

| Strategy | Mechanism | Use |
| --- | --- | --- |
| **Dyntopo** | Adds and removes topology under the brush as you work | Early exploration, when the form is still changing |
| **Multiresolution** | Subdivision levels on a fixed base mesh | Later refinement, and required for clean displacement baking |
| **Voxel remesh** | Rebuilds uniform topology on demand | Resetting topology mid-sculpt when it has become stretched |

Typical sequence: block with dyntopo or voxel remesh, settle the form, retopologise or accept a
remesh as the base, then refine with multiresolution.

**Multiresolution requires clean base topology** - it subdivides what it is given. Sculpting
detail on a bad base means baking that badness into every level.

## Coarse to fine, always

1. **Primary forms** - the big masses and the silhouette. Low resolution, large brushes.
2. **Secondary forms** - the major structures within the masses.
3. **Tertiary detail** - pores, wrinkles, scratches. Last, and often better as a texture than as
   geometry.

Subdividing early is the classic error: high resolution makes large changes slow and encourages
detailing a form that is still wrong.

## Brushes that do the work

Most sculpting is done with a handful: Draw, Clay Strips, Grab, Move, Smooth, Crease, Flatten,
Pinch. Learning ten deeply beats knowing fifty superficially.

**Smooth is not a fix for bad form.** It removes noise; it does not correct proportion.

## Symmetry

Sculpt symmetric until the form is settled, then break symmetry deliberately. A perfectly
symmetric creature reads as artificial - see
[[3D & Blender Knowledge/03 - Modelling/Symmetry & Mirroring|Symmetry & Mirroring]].

## Common mistakes

- Subdividing before the primary form is right
- Detailing at high resolution over a proportion error
- Sculpting a form that is fully describable in dimensions - a bolt should be modelled
- Multiresolution on bad base topology
- Never checking the silhouette from the camera angle
- Expecting Smooth to fix structural problems

## Related

[[3D & Blender Knowledge/03 - Modelling/Retopology|Retopology]] ·
[[3D & Blender Knowledge/05 - Organic & Sculpting/Baking|Baking]]

## Sources

Blender Manual (CC-BY-SA 4.0) - sculpt mode, dyntopo, multiresolution, remesh. Workflow ordering
and brush guidance are practitioner judgement.
