---
type: note
domain: 3D & Blender Knowledge
section: 06 - Procedural & Geometry Nodes
created: 2026-09-03
---

# Procedural Asset Design

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/00 - Procedural & Geometry Nodes|Procedural & Geometry Nodes]]

## What it is

Building node groups that other people - or you in three months - can actually use.

## What makes a group reusable

1. **A small, meaningful interface.** Expose the parameters that matter; hide the rest. Forty
   inputs is not flexibility, it is an unusable panel.
2. **Sensible defaults.** It should produce something reasonable with no adjustment.
3. **Named inputs with units and ranges.** "Density" with a min and max beats "Value.003".
4. **Predictable failure.** Zero, negative or extreme inputs should degrade, not crash or produce
   nothing.
5. **Documented assumptions** - does it expect a mesh, a curve, applied scale, specific attributes?

## Structure

- Build in **named sub-groups** rather than one flat graph. A graph of two hundred nodes is
  unmaintainable regardless of how well it works.
- Use **frames and labels**. A graph you understood while building is opaque a month later.
- Keep the top level readable: inputs, a handful of named stages, output.

## Parameterise the right things

Expose what a *user of the asset* would want to change - size, density, variation, seed. Do not
expose internal implementation values; they will be changed, break the asset, and generate support
questions.

**A seed input is almost always worth exposing.** It gives variation without any other change.

## Distribution

Mark node groups as assets so they appear in the Asset Browser with a preview and catalogue. A
group that lives in one .blend file that only you can find is not reusable, however good it is.

## When procedural is the wrong choice

- The object is made once and never varied - modelling it is faster
- The form is specific and artistic rather than rule-based
- The graph would take longer to build than the variations would take to model by hand

**Procedural pays off with repetition and iteration.** For a one-off, it is usually a slower route
to a worse result.

## Common mistakes

- Building procedurally out of principle rather than need
- Exposing every internal value
- One enormous unnamed graph
- No seed, so all instances are identical
- Assuming applied scale and breaking on objects that do not have it

## Related

[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Geometry Nodes Fundamentals|Geometry Nodes Fundamentals]] ·
[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Asset Libraries|Asset Libraries]]

## Sources

Practitioner synthesis. Node group and asset-marking mechanics are documented in the Blender Manual
(CC-BY-SA 4.0).
