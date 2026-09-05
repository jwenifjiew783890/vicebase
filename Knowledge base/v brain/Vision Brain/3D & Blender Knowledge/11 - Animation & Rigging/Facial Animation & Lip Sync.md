---
type: note
domain: 3D & Blender Knowledge
section: 11 - Animation & Rigging
created: 2026-09-03
---

# Facial Animation & Lip Sync

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/11 - Animation & Rigging/00 - Animation & Rigging|Animation & Rigging]]

## What it is

Animating expression and speech. The most scrutinised animation there is, because humans read
faces expertly and notice error instantly.

## Two mechanisms, usually combined

| Mechanism | Strength | Weakness |
| --- | --- | --- |
| **Shape keys** | Exact authored shapes; ideal for expressions and visemes | Fixed set; combinations can conflict |
| **Bones** | Continuous control, good for jaw and broad movement | Approximates soft-tissue motion less well |

Most production rigs use **bones for the jaw and broad motion, shape keys for the detail**, both
driven from a control interface rather than exposed raw.

## Visemes, not phonemes

Lip sync is animated to **visemes** - the visually distinct mouth shapes - not to every phoneme.
Many phonemes look identical: `p`, `b` and `m` share a closed mouth; `f` and `v` share lip-to-teeth.

A workable viseme set is small - roughly: closed (`M/B/P`), `F/V`, wide (`E`), narrow (`O/U`),
open (`A`), `L`, teeth (`S/T`), and rest. More than about a dozen is rarely worth the authoring.

## Method

1. **Load the audio** and work against the waveform in the timeline - see
   [[3D & Blender Knowledge/20 - VFX & Compositing/Video Sequence Editor & Audio|Video Sequence Editor & Audio]].
2. **Identify the accents** - the stressed syllables. Key those first; they carry the
   intelligibility.
3. **Key the strong visemes** - closures (`M/B/P`) and the wide/narrow extremes. These are what the
   eye actually reads.
4. **Let the rest interpolate.** Animating every phoneme produces a chattering, over-articulated
   mouth.
5. **Jaw first, lips second.** The jaw carries most of the visible motion.
6. **Then the rest of the face** - brows and eyes carry the emotion; the mouth only carries the
   words.

## The part people get wrong

**Speech is not only the mouth.** A technically perfect lip sync on a static face is unwatchable.
Brows, eyelids, head motion and blinks carry meaning, and their absence reads as death.

Also: **animate slightly ahead of the audio.** Mouth shapes tend to form marginally before the
sound. A frame or two early usually reads better than exactly on.

## Eyes

The highest-value detail in the whole face:

- **Blinks** - regular, and often at changes of thought or head direction
- **Saccades** - small rapid eye movements. Perfectly still eyes read as dead.
- **Focus** - eyes should converge on something at a real distance
- Eye direction leads head turns

## Checking

- Play at **full speed with audio**. Frame-by-frame judgement is meaningless here.
- Watch it **without sound** - the mouth should still read as speech
- Watch a **silhouette or blurred version** to check broad motion
- Show it to someone else; you lose objectivity fast on faces

## Common mistakes

- One shape per phoneme, producing chatter
- Mouth animated in isolation, face otherwise static
- Exactly on the audio rather than slightly ahead
- No blinks or eye movement
- Judging frame by frame
- Shape keys exposed as raw sliders instead of driven controls

## Related

[[3D & Blender Knowledge/11 - Animation & Rigging/Shape Keys & Drivers|Shape Keys & Drivers]] ·
[[3D & Blender Knowledge/11 - Animation & Rigging/Character Animation Workflow|Character Animation Workflow]]

## Sources

Blender Manual (CC-BY-SA 4.0) - shape keys, drivers, audio in the timeline and dope sheet. Viseme
sets and lip-sync craft are long-established animation practice.
