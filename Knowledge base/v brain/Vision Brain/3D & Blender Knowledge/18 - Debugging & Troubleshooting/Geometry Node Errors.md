---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Geometry Node Errors

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

A geometry node graph produces nothing,
produces the wrong thing, or hangs Blender.

## Likely causes

1. **Realised instances** on a large count - the usual cause of a hang
2. **Field versus single-value mismatch** - the socket shapes differ
3. **Attribute lost** because it was never captured before an operation that dropped it
4. **Wrong domain** - an attribute read on points when it lives on faces
5. **Empty input geometry**
6. **Node evaluating on the wrong component** - mesh operation on a curve, or the reverse
7. **A count or density driven to an enormous value** by an unclamped input

## Diagnosis

1. **Attach a Viewer node** and step backwards through the graph. This is the single most effective
   technique and the equivalent of a print statement.
2. Open the **Spreadsheet** and look at actual data - counts, domains, attribute values. Most
   "it does nothing" turns out to be zero elements at some stage.
3. Check socket shapes where a connection is refused or behaves oddly - diamond is a field, circle
   is a single value.
4. **Mute nodes from the output backwards** until the problem disappears.
5. Check for a Realize Instances node upstream of something expensive.
6. Clamp any input that multiplies - a density or count field with no upper bound will eventually
   be set too high.

## Evidence to collect

- Element counts at each stage, from the spreadsheet
- Which domain each attribute lives on
- Where in the graph the count becomes zero, or becomes enormous
- Whether instances are realised, and where

## Safest fix

- Move Realize Instances as late as possible, or remove it
- Capture attributes before operations that would drop them
- Convert domains explicitly rather than relying on implicit interpolation
- Clamp counts and densities
- Split a large graph into named groups so each part can be verified independently

**If Blender is hanging, do not wait indefinitely** - a realised instance count in the millions
will not complete. End the process and reopen; unsaved work is the cost of not saving before
experimenting.

## Verification

Check the spreadsheet, not just the viewport. The viewport can look plausible while the underlying
data is wrong - wrong domain, wrong counts, attributes missing.

## Common mistakes

- No Viewer node, debugging by guessing
- Realising instances early
- Ignoring socket shape mismatches
- Building one enormous graph that cannot be bisected
- No clamping on values that multiply

## Prevention

Build in small named groups. Use the Viewer node continuously rather than only when something
breaks. Save before experimenting with instance counts.

## Related

[[3D & Blender Knowledge/06 - Procedural & Geometry Nodes/Geometry Nodes Fundamentals|Geometry Nodes Fundamentals]]

## Sources

Blender Manual (CC-BY-SA 4.0) - geometry nodes, fields, domains, spreadsheet and viewer.
Diagnostic approach is practitioner judgement.
