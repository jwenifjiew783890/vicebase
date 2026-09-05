---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Add-on & Dependency Problems

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

An add-on fails to enable,
breaks after an update, or destabilises Blender.

## Likely causes

1. **Version incompatibility** - the add-on targets a different Blender version. By far the most
   common.
2. **Missing Python dependency** not installed into Blender's bundled Python
3. **Conflict between two add-ons** registering the same keymap, property or handler
4. **Corrupted install** or a partial extraction
5. **Preferences carried over** from an older Blender version

## Diagnosis

1. **System Console** - registration errors appear there with a traceback
2. **Disable all third-party add-ons; retest.** If the problem disappears, re-enable one at a time.
3. Check the add-on's declared Blender version support
4. **Launch with Factory Settings** to eliminate preferences and add-ons entirely. If the problem
   persists there, it is not an add-on.
5. For import errors, confirm the dependency is installed into **Blender's** Python, not the system
   Python

## Evidence to collect

- Console traceback at enable time
- Add-on version and its stated Blender compatibility
- Whether the problem occurs in Factory Settings
- Which add-on, when disabled, resolves it

## Safest fix

- Update the add-on, or roll back Blender - **version mismatch is not fixable by configuration**
- Install missing dependencies into Blender's bundled Python
- Remove one of two conflicting add-ons
- Reinstall cleanly rather than over the top

## Verification

Restart Blender fully. Add-on registration happens at startup, so a fix that appears to work
without a restart may not survive one.

## Common mistakes

- Blaming Blender for an add-on fault
- Never checking the console
- Updating Blender mid-project without checking add-on compatibility
- Keeping add-ons enabled that are never used

## Prevention

Keep the enabled set small. Record which add-ons a project depends on. Do not update Blender in
the middle of a project.

## Related

[[3D & Blender Knowledge/16 - Add-ons & Pipelines/Add-ons & Extensions|Add-ons & Extensions]]

## Sources

Blender Manual (CC-BY-SA 4.0) - add-on installation, preferences, command-line options.
