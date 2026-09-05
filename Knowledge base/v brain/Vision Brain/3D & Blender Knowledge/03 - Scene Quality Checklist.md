---
type: note
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# Scene Quality Checklist

The validation gates. Run the relevant block before declaring a stage finished — each item exists
because skipping it costs more later than checking it now.

This is a checklist, not a tutorial. Each line is a question with a pass/fail answer.

## Geometry

- [ ] **Scale applied** (`Ctrl+A`) — object scale reads 1.0, 1.0, 1.0
- [ ] **Origins deliberate** — at the pivot the object actually rotates about, not wherever it landed
- [ ] **Normals outward** — Face Orientation overlay shows no red
- [ ] **No doubles** — Merge by Distance run, vertex count sane afterwards
- [ ] **Manifold** where it matters (booleans, solidify, 3D print) — no holes, no interior faces,
      no edges shared by more than two faces
- [ ] **No degenerate faces** — zero-area faces, edges of zero length
- [ ] **Topology appropriate to purpose** — quads where it deforms or subdivides; n-gons only on
      flat static surfaces
- [ ] **Edge loops where it bends**, if the model will deform
- [ ] **Shading correct** — smooth/flat assigned deliberately, not by accident

## Scale and units

- [ ] **Scene units set** before modelling, not after
- [ ] **Real-world dimensions** — a 2 m door measures 2 m
- [ ] **Consistent across imported assets** — the classic failure is a kit-bashed scene where one
      asset arrived in centimetres

## Modifiers

- [ ] **Stack order correct** — generate, then smooth, then deform
- [ ] **Viewport and render levels intentional** — subdivision at 1/3 is a decision, not a default
- [ ] **Nothing applied that should have stayed live**
- [ ] **Nothing live that should have been applied** before export

## UVs and textures

- [ ] **Unwrapped** if textured
- [ ] **No unintended overlaps** — overlapping UVs are correct for tiling and mirroring, wrong for
      baking
- [ ] **Texel density consistent** across objects sharing a shot
- [ ] **Texture paths resolve** — no missing images (magenta), paths packed or relative
- [ ] **Colour space correct** — base colour as sRGB; roughness, metallic, normal maps as
      **Non-Color**. This one is silently wrong more often than any other.

## Materials

- [ ] **Every material assigned deliberately** — no leftover default grey on a hero object
- [ ] **Roughness values plausible** — almost nothing in reality is 0.0 or 1.0
- [ ] **Metallic is 0 or 1**, not intermediate, except on genuinely layered surfaces
- [ ] **Named** — `Material.001` on a delivered asset is a defect

## Lighting

- [ ] **Something is actually emitting** — a black render usually means no light, not a bad material
- [ ] **No light trapped inside geometry**
- [ ] **Light sizes physically sensible** — a 2 m "bulb" produces impossible shadows
- [ ] **Exposure sane** — not compensating for wrong light intensity with film exposure
- [ ] **World/HDRI rotation deliberate**, not the default orientation by accident

## Camera

- [ ] **Focal length chosen** for the subject, not left at 50 mm by default
- [ ] **Clipping start/end** contain the scene — the near plane is a common cause of "the object
      vanished"
- [ ] **Composition checked** with the camera passepartout, at final aspect ratio
- [ ] **No unintended distortion** — a wide lens close to a face is a choice, not an accident

## Performance

- [ ] **Polygon count justified** by what the camera resolves
- [ ] **Subdivision render levels** not silently enormous
- [ ] **Texture resolution proportionate** — 4K maps on an object 40 pixels wide is waste
- [ ] **Scene fits in VRAM**, if rendering on GPU
- [ ] **No runaway modifiers** — check the statistics overlay

## Naming and organisation

- [ ] **Objects named meaningfully** — not `Cube.014`
- [ ] **Collections structured** by role, not by accident of creation order
- [ ] **Unused data purged** — orphaned meshes, materials, images
- [ ] **Materials, meshes and objects named consistently** with each other

## Output

- [ ] **Resolution and aspect** match the deliverable
- [ ] **Correct engine** for the purpose
- [ ] **Samples/denoise** settled — noise resolved without smearing detail
- [ ] **Colour management deliberate** — view transform chosen, not defaulted
- [ ] **File format fits the use** — EXR for compositing, PNG for delivery, and 16-bit where
      grading will follow
- [ ] **Render actually inspected at full size**, not judged from a thumbnail

## Before export

- [ ] Scale applied, transforms clean
- [ ] Modifiers applied or explicitly intended to travel
- [ ] Normals correct and custom normals handled
- [ ] UVs present and named
- [ ] Materials named and texture paths resolvable by the receiving application
- [ ] Units match the destination's expectation
- [ ] A test import performed — **export is not verified until something else has opened it**

## Related

[[3D & Blender Knowledge/01 - Modelling Method|Modelling Method]] ·
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]] ·
[[3D & Blender Knowledge/04 - Debugging Method (3D)|Debugging Method]]

## Sources

Practitioner synthesis, assembled from the failure modes each item prevents. The colour-space,
transform and modifier items follow documented Blender behaviour (Blender Manual,
docs.blender.org/manual, CC-BY-SA 4.0).
