---
type: note
domain: 3D & Blender Knowledge
section: 16 - Add-ons & Pipelines
created: 2026-09-03
---

# Add-ons & Extensions

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/16 - Add-ons & Pipelines/00 - Add-ons & Pipelines|Add-ons & Pipelines]]

## What it is

Python packages extending Blender. Some ship with Blender and are merely disabled; others are
third-party.

## The cost

Every add-on is code running inside Blender with full access. That means:

- **Version fragility** - an add-on written for one Blender version may break on the next. This is
  the single most common source of "Blender is broken".
- **Startup cost** - many add-ons slow launch
- **Conflicts** - two add-ons registering the same keymap or property interfere
- **Security** - an add-on is arbitrary code. Install only from sources you trust.
- **Portability** - a file that depends on an add-on may not open correctly elsewhere

## Practical policy

- Install deliberately, not speculatively
- Prefer bundled add-ons where they suffice
- Keep the enabled set small
- Record which add-ons a project depends on, in the project itself
- **Before blaming Blender, disable third-party add-ons and retest**

## Diagnosing add-on problems

1. Open the **System Console** - add-on errors appear there and nowhere else
2. Disable all third-party add-ons; retest
3. Re-enable one at a time to find the culprit
4. Check the add-on's stated Blender version compatibility
5. Test in **Factory Settings** to eliminate configuration as a cause

## Dependencies

Add-ons requiring external Python packages are a recurring problem - the package must be installed
into Blender's bundled Python, not the system one. Failures appear as import errors in the console.

## Common mistakes

- Installing many add-ons and never auditing them
- Blaming Blender for an add-on fault
- Not checking the console
- Depending on an add-on for a deliverable, then finding the recipient does not have it
- Updating Blender mid-project without checking add-on compatibility

## Related

[[3D & Blender Knowledge/18 - Debugging & Troubleshooting/Add-on & Dependency Problems|Add-on & Dependency Problems]] ·
[[3D & Blender Knowledge/17 - Python & Automation/00 - Python & Automation|Python & Automation]]

## Sources

Blender Manual (CC-BY-SA 4.0) - add-on installation and preferences. Diagnostic policy is
practitioner judgement.
