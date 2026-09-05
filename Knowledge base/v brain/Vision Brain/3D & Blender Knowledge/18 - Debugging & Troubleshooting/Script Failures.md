---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Script Failures

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

A Python script errors, does nothing, or silently
does the wrong thing.

## The first rule

**Scripts do not fail silently. The traceback is in the System Console**, which is closed by
default on Windows.

**Window > Toggle System Console.** Almost every "the script did nothing" report ends here.

## Likely causes

1. **Operator poll failure** - wrong context, wrong mode, nothing selected
2. **Name lookup after creation** - the requested name was not granted
3. **Data created but never linked** to a collection, so it exists but is invisible
4. **Stale data reference** used after the underlying data was freed
5. **Wrong mode** - mesh data accessed in Edit Mode
6. **Context unavailable** in background mode
7. **Threading** - unsupported and crash-prone
8. **Add-on conflict**

## Diagnosis

1. **Open the System Console and read the traceback.** Everything else is secondary.
2. If the error is a poll failure, the operator was called from an unacceptable context - see
   [[3D & Blender Knowledge/17 - Python & Automation/Operators vs Direct Data|Operators vs Direct Data]].
3. If nothing appears to happen, check whether the object was **linked** to a collection.
4. Print intermediate state - object names actually returned, counts, types - rather than assuming.
5. Run the same code in the Python console interactively, one line at a time.
6. Test in Factory Settings to rule out add-on interference.

## Evidence to collect

- The full traceback from the System Console
- The actual names of created data, as returned - not the requested names
- Whether the object appears in `bpy.data` but not in the scene collection
- Whether it behaves differently in background mode

## Safest fix

- Replace `bpy.ops` calls with direct `bpy.data` manipulation wherever an equivalent exists
- Use returned references instead of name lookups
- Link created objects explicitly
- Re-acquire references rather than caching them
- Remove threading
- Switch to Object Mode before accessing mesh data

## Verification

**Run twice.** A script that works once and fails on the second run is depending on state - leftover
selection, an object that now exists, a name that is now taken. Idempotence is the test that
catches most latent script bugs.

Then verify the *scene*, not just the exit status - see
[[3D & Blender Knowledge/17 - Python & Automation/Scene Generation & Validation|Scene Generation & Validation]].

## Common mistakes

- Not opening the console
- Treating "no exception" as success
- Name lookups after creation
- Testing only once
- Assuming context in background mode

## Prevention

Prefer direct data access. Validate generated scenes rather than trusting completion. Keep scripts
idempotent.

## Related

[[3D & Blender Knowledge/17 - Python & Automation/Safe Scripting Practices|Safe Scripting Practices]]

## Sources

Blender Python API documentation (docs.blender.org/api) - *Troubleshooting Errors & Crashes*,
*Using Operators*, *Gotchas*. Diagnostic sequence is practitioner judgement.
