---
type: note
domain: 3D & Blender Knowledge
section: root
created: 2026-09-03
---

# Sources & Provenance

Where this domain's claims come from, and how to tell one kind of claim from another.

## The three kinds of claim

Every note here mixes these, and they carry different weight. **Never present one as another.**

| Kind | Weight | How it is marked |
| --- | --- | --- |
| **Documented behaviour** | Highest. Blender does this; it is specified. | Cited to the Blender Manual or Python API docs |
| **Physical/optical fact** | High. True regardless of software. | Stated plainly (focal length, inverse-square falloff, conductor vs dielectric) |
| **Practitioner judgement** | Useful but weaker. A working professional's heuristic. | Labelled as practice, convention or heuristic |

A heuristic presented as a rule is the failure mode this table exists to prevent. "Quads
subdivide predictably" is documented behaviour. "Blockout before detail" is judgement — widely
held, but judgement.

## Primary sources

**Blender Manual** — <https://docs.blender.org/manual/en/latest/>
Version consulted: **Blender 5.2 LTS**, 2026-09-03.
Licence: **CC-BY-SA 4.0** (stated on the manual's copyright page).
Used for: transforms, modifiers, normals, mesh tools, render engines, linking/appending,
colour management, compositor and mask editor, motion tracking, keying, Grease Pencil, the video
sequencer, shape keys and drivers, weight painting, and the rigid body / cloth / soft body /
fluid / gas simulation systems.

**Blender Python API Documentation** — <https://docs.blender.org/api/current/>
Used for: the API constraints in
[[3D & Blender Knowledge/02 - Blender Engineering Constraints|Blender Engineering Constraints]]
and section 17. Specifically the *Best Practice* and *Gotchas* pages, which document:
Python threads are unsupported and cause crashes; operators depend on context and cannot take
data arguments; Python objects wrapping Blender data have limited lifetime; requested data names
are not guaranteed.

**Blender Foundation / developer documentation** — <https://developer.blender.org>
Consulted for release and behaviour questions where the manual is silent.

## How external material is used here

**Nothing is copied verbatim.** The Blender Manual is CC-BY-SA 4.0, which would permit
reproduction under share-alike terms — but reproducing it would make this domain a stale mirror
of a document that is better maintained upstream, and would defeat the purpose of a knowledge
base. Instead:

- documented behaviour is **restated in the context of a decision** ("stack order matters, and
  here is what each order produces"),
- the source is cited so the authoritative text can be checked,
- practitioner material is synthesised and labelled as such.

This follows the same rule as the rest of the vault: **synthesise and attribute, never paste.**
See [[Coding Knowledge/99 - Sources & Provenance|the Coding Knowledge equivalent]].

## Where this domain is thinner than the manual

Some areas are covered by judgement more than by documentation, because the documentation does
not address them:

- **Destruction.** Blender's core distribution has no fracture system, so the workflow described
  in [[3D & Blender Knowledge/12 - Simulation/Particles & Destruction|Particles & Destruction]]
  is assembled from documented parts (rigid bodies, constraints, geometry nodes) plus practice.
- **Crowds.** There is no crowd system to document. Deliberately not given its own note.
- **Engine export conventions.** Unit and axis expectations belong to the target engine, not to
  Blender, and are stated as *check against your engine's current documentation* rather than as
  fixed values. See
  [[3D & Blender Knowledge/22 - Game & Real-Time Assets/Engine Export Preparation|Engine Export Preparation]].
- **Capability boundaries.** The weakness list in
  [[3D & Blender Knowledge/02 - Blender Fundamentals/Blender Capability Map|Blender Capability Map]]
  is an assessment of the 5.2 LTS distribution, not a documented statement. Re-check it after
  major releases.

## What is deliberately not here

- **No tutorial transcripts.** Step-by-step button sequences date badly and do not help an agent
  decide anything.
- **No scraped site content.** No bulk import from any source.
- **No add-on-specific workflows** for paid or third-party add-ons, beyond naming what a category
  of add-on does. Those change without notice and cannot be verified here.
- **No claims about Blender versions not consulted.** Behaviour changes between releases; where a
  behaviour is version-sensitive the note says so.

## Reviewing a claim in this domain

If a note's claim matters to a decision and is not obviously documented:

1. Check whether it is labelled as documented, physical, or judgement.
2. If documented — follow the citation to the manual and confirm against the current version.
3. If judgement — treat it as a strong prior, not a rule, and let the specific task override it.
4. If it turns out to be wrong, correct the note and record what taught you. A corrected note is
   worth more than a cautious one.

## Related

[[3D & Blender Knowledge/00 - 3D & Blender Knowledge|Domain index]] ·
[[Coding Knowledge/99 - Sources & Provenance|Coding Knowledge provenance]]
