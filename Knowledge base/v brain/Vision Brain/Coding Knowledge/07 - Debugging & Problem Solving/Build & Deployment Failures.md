---
type: note
domain: Coding Knowledge
section: 07 - Debugging & Problem Solving
created: 2026-09-03
---

# Build & Deployment Failures

"It does not build" and "it built but does not run there" - two different problems with two different sequences.

## Read the first error, not the last

Build tools cascade: one missing type produces forty downstream errors. **Scroll up.** The first
error is usually the only real one, and fixing it removes the rest.

Related: many build systems print a summary at the end that omits the actual message. The useful
text is in the middle of the output.

## "It builds locally, not in CI"

Almost always one of these, in order of likelihood:

1. **Uncommitted file.** It exists locally and is not in the repository. `git status`,
   and check `.gitignore`.
2. **Cache.** Local incremental build state hides a real error. Delete the build directory and
   rebuild clean - this is the single most informative test.
3. **Dependency versions.** CI installed from the lock file (or did not); local has drifted.
4. **Environment variables** present locally and absent in CI.
5. **Case sensitivity.** Windows and macOS are case-insensitive by default; Linux is not.
   `import Utils` from `utils.ts` works on one and fails on the other. Very common and easily
   missed.
6. **Toolchain version** - a different Node, Python, compiler or SDK.
7. **Path assumptions** - absolute paths, or a different working directory.
8. **Resource limits** - CI has less memory; a build OOMs where it did not locally.

## Compilation errors worth recognising

- **"undefined reference" / "unresolved external"** is a **linker** error: declared but not
  defined, library missing, or libraries in the wrong order.
- **"multiple definition"** - a definition in a header included from several translation units.
- **Type errors deep inside a library** - usually a version mismatch between the library and its
  type definitions.
- **"cannot find module"** - resolution, not existence. Check the path, the `exports` map, the
  ESM/CJS boundary and the working directory.
- **Out of memory during build** - common with large TypeScript projects and heavy bundlers.
  Raise the heap limit or split the build.

## "It built but does not run there"

1. **Is it the artefact you think?** Check the version, the build ID, the commit. Deploying an
   old artefact is more common than it should be.
2. **Configuration.** A missing or differently-named environment variable. Validating config at
   startup turns this from a mystery into a clear boot-time error.
3. **Missing runtime dependency** - present on the build machine, absent in the runtime image.
   The classic multi-stage build mistake.
4. **File permissions and ownership**, especially after copying into a container as a non-root
   user.
5. **Port already in use**, or bound to the wrong interface.
6. **Working directory** differs from development.
7. **Architecture mismatch** - an arm64 image on amd64, or a native module built for the wrong
   platform.
8. **Resource limits** - a memory limit lower than the process needs; exit code 137 is the tell.

## Migration and startup order

A deploy that starts the application before the migration completes, or runs a migration that
the old still-running version cannot tolerate, fails in confusing ways. Make migrations
backwards compatible for one release, and make startup wait for or verify the schema.

## Debugging a container that will not start

```
docker logs <container>
docker run --rm -it --entrypoint sh <image>
```

The second is the highest-value command here: get a shell **in the actual image** and look. Is
the file there? Does it run by hand? What is the working directory? What does the environment
contain? Most "it works in the build and not at runtime" problems are visible in thirty seconds
this way.

## Prevention

Reproducible builds (pinned everything), clean builds in CI, the same container image used
locally and in CI, configuration validated at startup, and a health check that reflects real
readiness.

---

## See also

- [[Coding Knowledge/07 - Debugging & Problem Solving/Dependency & Version Conflicts|Dependency & Version Conflicts]]
- [[Coding Knowledge/06 - DevOps & Infrastructure/Deployment|Deployment]]
- [[Coding Knowledge/01 - Software Engineering/CI-CD|CI/CD]]

## Sources

- Docker and CI platform documentation. Practitioner synthesis for the diagnostic ordering.
