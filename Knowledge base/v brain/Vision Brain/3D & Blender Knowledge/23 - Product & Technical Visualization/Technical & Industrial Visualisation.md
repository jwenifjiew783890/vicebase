---
type: note
domain: 3D & Blender Knowledge
section: 23 - Product & Technical Visualization
created: 2026-09-03
---

# Technical & Industrial Visualisation

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/23 - Product & Technical Visualization/00 - Product & Technical Visualization|Product & Technical Visualization]]

## What it is

Imagery whose purpose is to **explain** rather than to sell - assembly instructions, exploded
views, cutaways, process diagrams, training material.

## The governing difference

Clarity beats realism. A photoreal render that does not explain the mechanism has failed; a plain
render with a clear exploded view has succeeded.

This inverts several defaults:

| Default in other work | Here |
| --- | --- |
| Photoreal materials | Often flat or simplified, to avoid distraction |
| Dramatic lighting | Even, shadow-controlled lighting so nothing is obscured |
| Shallow depth of field | Deep focus - everything must be legible |
| Realistic complexity | Simplified, with irrelevant detail removed |

## The techniques

**Exploded views** - parts separated along assembly axes, showing how they fit. Build them by
animating or offsetting along a consistent direction, ideally driven procedurally so the explosion
amount is one parameter.

**Cutaways and sections** - removing part of a volume to show inside. A boolean with a cutting
solid works, and keeping it live means the section plane can be moved. Consider showing the cut
face in a distinct colour, as engineering drawings do.

**Ghosting / transparency** - showing internal parts through a semi-transparent shell. Effective,
and easy to overdo into illegibility.

**Highlighting** - the part under discussion in colour, everything else desaturated. The most
effective single technique for directing attention.

**Callouts and annotation** - labels, leader lines, dimensions. Grease Pencil is well suited to
this, or text objects in 3D.

## Sequence and animation

Assembly and process visualisation is usually a sequence. Keep it legible:

- one action at a time
- hold on each state long enough to read
- consistent camera, or slow deliberate moves - fast cuts destroy comprehension
- motion that follows the actual assembly direction

## Accuracy

If it explains a real product, it must be **right**. An assembly sequence showing an impossible
order is worse than no visualisation, because it will be followed.

Verify against the actual specification or the engineering model, and mark anything simplified as
simplified.

## Common mistakes

- Photoreal treatment that obscures the mechanism
- Too much shown at once
- Excessive transparency, making everything ambiguous
- Inconsistent explosion directions
- No highlighting, so attention is undirected
- Assembly sequences that are not physically possible

## Related

[[3D & Blender Knowledge/23 - Product & Technical Visualization/Product Visualisation|Product Visualisation]] ·
[[3D & Blender Knowledge/21 - Grease Pencil & Motion Design/Grease Pencil Fundamentals|Grease Pencil Fundamentals]]

## Sources

Practitioner synthesis - standard technical-illustration practice. Boolean, Grease Pencil and
annotation mechanics are documented in the Blender Manual (CC-BY-SA 4.0).
