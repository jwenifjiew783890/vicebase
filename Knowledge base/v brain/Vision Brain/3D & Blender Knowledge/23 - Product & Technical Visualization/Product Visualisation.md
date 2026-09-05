---
type: note
domain: 3D & Blender Knowledge
section: 23 - Product & Technical Visualization
created: 2026-09-03
---

# Product Visualisation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/23 - Product & Technical Visualization/00 - Product & Technical Visualization|Product & Technical Visualization]]

## What it is

Presenting a manufactured object so it reads accurately and attractively - packshots, e-commerce
imagery, marketing renders, configurators.

## What makes it different

- **The object is the entire subject.** There is nowhere to hide a modelling error.
- **Accuracy is commercial.** A product that does not match what ships is a real problem, not an
  artistic choice.
- **Materials carry the image**, because form is usually simple and clean
- Often needs **many variants** - colours, configurations, angles - which makes the setup
  procedural rather than one-off

## Modelling requirements

- **Real dimensions**, from the specification or CAD
- **Bevels on every visible edge** - the single most important step, since products are
  manufactured objects and manufactured edges have radii. See
  [[3D & Blender Knowledge/04 - Hard Surface/Weighted Normals & Bevel Discipline|Weighted Normals & Bevel Discipline]].
- Correct **construction logic** - parting lines, draft, fasteners consistent with how the object
  is actually made
- **Separate parts**, not a merged mesh, so materials and variants are addressable

## Lighting

Covered in
[[3D & Blender Knowledge/08 - Lighting/Studio & Product Lighting|Studio & Product Lighting]]. The
essentials: large soft sources, arrangement of what reflective surfaces reflect, and a dedicated
light to produce edge highlights.

## Variants and configuration

When many colourways or configurations are needed, build for it from the start:

- materials driven by a small set of parameters rather than duplicated
- parts organised in collections so configurations are visibility switches
- camera and lighting fixed, so variants differ only in the product
- **script the variant renders** rather than doing them by hand - see
  [[3D & Blender Knowledge/17 - Python & Automation/Scene Generation & Validation|Scene Generation & Validation]]

Forty variants rendered by hand is forty chances to get one wrong.

## Presentation conventions

- Neutral background, or a context that does not compete
- Consistent framing and scale across a product family
- Shadow grounding the object - a floating product reads as a cut-out
- Consistent colour management across the set, since colour accuracy may be contractual

## Common mistakes

- No bevels, so the product looks like CG
- Colour not matched to the real product
- Merged mesh, making variants impossible
- Inconsistent framing across a family
- Rendering variants by hand
- Floating products with no contact shadow

## Related

[[3D & Blender Knowledge/08 - Lighting/Studio & Product Lighting|Studio & Product Lighting]] ·
[[3D & Blender Knowledge/04 - Hard Surface/00 - Hard Surface|Hard Surface]]

## Sources

Practitioner synthesis - standard product-visualisation practice.
