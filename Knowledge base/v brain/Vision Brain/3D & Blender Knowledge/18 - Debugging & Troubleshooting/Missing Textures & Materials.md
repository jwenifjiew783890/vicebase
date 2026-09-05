---
type: note
domain: 3D & Blender Knowledge
section: 18 - Debugging & Troubleshooting
created: 2026-09-03
---

# Missing Textures & Materials

**Up:** [[Vision Brain]] > [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] > [[3D & Blender Knowledge/18 - Debugging & Troubleshooting/00 - Debugging & Troubleshooting|Debugging & Troubleshooting]]

Magenta surfaces, black
materials, or textures that vanish after moving a file.

## Likely causes

1. **Broken file path** - the classic, and almost always after moving or renaming
2. **Absolute paths** that do not exist on this machine
3. **Textures never packed** before archiving or transferring
4. **Wrong material slot** assigned to the faces
5. **No UV map**, so an image texture has nowhere to project
6. **Node disconnected** from the shader output
7. **Colour space wrong**, giving a subtly wrong rather than missing result
8. **Linked material from a file that is no longer reachable**

## Diagnosis

**Magenta means Blender cannot find the image file.** That is unambiguous - it is a path problem,
not a material problem.

1. Open the **Image Editor** or the node, and read the path
2. **File > External Data > Report Missing Files** lists everything broken at once
3. For black surfaces: check lighting first, then normals, then node connections
4. Check the **material slot** assignment in Edit Mode
5. Check a UV map exists in Object Data Properties

## Evidence to collect

- The exact path the node is looking for
- Whether the file exists at that path
- Whether paths are relative or absolute
- Output of Report Missing Files

## Safest fix

- **File > External Data > Find Missing Files**, pointing at the texture directory - resolves in
  bulk
- Then **Make Paths Relative**, so the project survives moving
- Or **Pack Resources** to embed textures in the .blend, which is the safest option for archiving
  and transfer
- Assign the correct material slot
- Unwrap if UVs are absent

## Verification

Reopen the file, ideally from a different location, and confirm textures still resolve. A fix that
works only in the current session has not fixed the path.

## Common mistakes

- Re-linking each texture by hand instead of using Find Missing Files
- Leaving absolute paths after fixing, so it breaks again on the next move
- Packing everything including 4K textures, producing an enormous file, when relative paths would
  have done
- Assuming a black material is a missing texture when it is a lighting problem

## Prevention

Use relative paths from the start. Keep textures in a folder beside the .blend. Pack before
archiving or sending.

## Related

[[3D & Blender Knowledge/07 - Materials & Shaders/Texture Workflow|Texture Workflow]] ·
[[3D & Blender Knowledge/07 - Materials & Shaders/Shader Debugging|Shader Debugging]]

## Sources

Blender Manual (CC-BY-SA 4.0) - external data, path handling, packing.
