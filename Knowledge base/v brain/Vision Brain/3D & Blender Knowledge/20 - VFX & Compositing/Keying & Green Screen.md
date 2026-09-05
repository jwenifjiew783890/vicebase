---
type: note
domain: 3D & Blender Knowledge
section: 20 - VFX & Compositing
created: 2026-09-03
---

# Keying & Green Screen

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/20 - VFX & Compositing/00 - VFX & Compositing|VFX & Compositing]]

## What it is

Extracting a subject from a coloured backdrop by generating a matte from colour difference.

## The result is decided on set

Keying quality is mostly determined before any software is opened:

- **Even backdrop lighting.** Uneven green is the main cause of a matte that cannot be pulled
  cleanly.
- **Subject far from the backdrop**, to reduce spill and shadow.
- **Lit to match the intended final environment**, not just lit well.
- **Backdrop colour distinct from the subject** - green against green clothing is unrecoverable.
- **Sharp footage** - motion blur and compression damage edges irreparably.

**Heavily compressed footage keys badly** because chroma subsampling discards exactly the colour
information the key depends on. This is a real limit, not a technique problem.

## Workflow

1. Set the footage **colour space** correctly first.
2. Pull a **core matte** - solidly opaque in the interior of the subject.
3. Pull an **edge matte** - preserving hair, motion blur and semi-transparency.
4. Combine them; the interior comes from the core, the edges from the edge matte.
5. **Despill** - remove green light contaminating the subject, especially at edges and in hair.
6. Add **garbage masks** to remove parts of the frame outside the backdrop - stands, rigging,
   floor edges. See
   [[3D & Blender Knowledge/20 - VFX & Compositing/Masking & Rotoscoping|Masking & Rotoscoping]].
7. Composite over the new background, then match colour and grain.

**One key rarely does everything.** Layering a core key, an edge key and garbage mattes is normal
practice, not a sign of failure.

## Judging a matte

- View the **matte alone** - it should be solid white inside, solid black outside, with detail only
  at edges. Grey in the interior means an incomplete key.
- **Check edges against a bright background.** Dark fringing and residual green are obvious there
  and invisible against dark.
- **Play it at full speed.** Edges that chatter frame to frame are the most common failure and
  cannot be seen on a still.

## Despill

Green light bounces onto the subject; removing it is a separate step from the matte. Over-despilled
subjects turn magenta at the edges, which is as obvious as the spill was.

Consider what the subject would actually reflect from the *new* environment, and reintroduce that -
this is what makes a key look integrated rather than cut out.

## Common mistakes

- Trying to pull one perfect key instead of layering
- Ignoring despill, leaving a green edge
- Over-despilling into magenta
- Judging the matte only in the composite, never in isolation
- Not using garbage masks, and fighting the key to remove a light stand
- Keying compressed footage and blaming the technique

## Related

[[3D & Blender Knowledge/20 - VFX & Compositing/Masking & Rotoscoping|Masking & Rotoscoping]] ·
[[3D & Blender Knowledge/20 - VFX & Compositing/CGI & Live-Action Integration|CGI & Live-Action Integration]]

## Sources

Blender Manual (CC-BY-SA 4.0) - keying nodes, despill, matte nodes. On-set requirements, the
core/edge layering approach and the acceptance checks are standard VFX practice.
