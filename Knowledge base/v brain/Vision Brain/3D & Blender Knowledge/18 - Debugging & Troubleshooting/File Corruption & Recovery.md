---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# File Corruption & Recovery

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

Blender crashed, the file will
not open, or work was lost.

## Recovery options, in order

1. **File > Recover Last Session.** Blender writes a quit file on exit, including on crash. This is
   the first thing to try and it recovers more than people expect.
2. **File > Recover Auto Save.** Blender periodically writes autosaves to the temporary directory.
   Check the autosave interval in preferences - the default may be longer than you would like.
3. **The `.blend1` backup.** Saved alongside the file on each save, holding the previous version.
   Rename to `.blend` and open.
4. **Incremental versions**, if you kept them.
5. **Append from the damaged file.** Even a file that will not open fully can often have objects,
   materials and collections appended out of it into a new file. This recovers more than trying to
   repair the original.

## If the file opens but is wrong

- Check for **orphaned data** holding the real content
- Check whether collections are excluded rather than missing
- Try opening with **Load UI disabled**, in case a corrupted workspace layout is the problem

## Diagnosing repeated crashes

1. Does it crash on a specific action? That is a reproducible bug - note the steps.
2. Does it crash on a specific file only? The file is the problem.
3. Does it crash in Factory Settings? Then it is not add-ons or preferences.
4. Check the **System Console** for the last output before the crash.
5. Suspect: GPU drivers, out-of-memory, unsupported threading in a script, add-ons.

## Evidence to collect

- Whether the crash is reproducible
- Console output immediately before the crash
- Memory usage at the time
- Whether it happens in Factory Settings

## Prevention - the part that actually matters

Recovery is unreliable. Prevention is not:

- **Incremental saves.** File > Save Incremental, or manual `_v001`, `_v002`. Cheap, and the only
  thing that reliably survives everything.
- **Keep `.blend1` backups enabled.**
- **Shorten the autosave interval** if working on something valuable.
- **Save before**: long renders, applying destructive operations, running scripts, experimenting
  with high instance counts.
- **Back up the project directory**, not just the .blend - textures and caches matter too.

**A file with no version history is one crash away from a lost day.** This is the single most
important habit in this domain.

## Common mistakes

- No incremental saves
- Overwriting the only good version with a broken one
- Relying on autosave without knowing its interval
- Not trying Append from a file that will not open
- Deleting the `.blend1` as clutter

## Related

[[3D & Blender Knowledge/19 - Production Workflows/Versioning & Backups|Versioning & Backups]]

## Sources

Blender Manual (CC-BY-SA 4.0) - recovery, autosave, save versions, appending.
