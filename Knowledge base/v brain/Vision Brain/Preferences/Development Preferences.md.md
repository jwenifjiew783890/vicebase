# Development Preferences

## Development Philosophy

Build systematically rather than rushing.

Preferred process:

PLAN
→ REVIEW
→ APPROVE
→ IMPLEMENT
→ TEST
→ VERIFY
→ STOP

## Incremental Development

Complete one meaningful step at a time.

Every major implementation stage should leave the application
runnable.

## Mature Infrastructure

When a mature, well-maintained system already solves a difficult
problem, prefer integrating or adapting it rather than rebuilding
it from scratch.

Examples:

- model runtimes
- terminal infrastructure
- PTY systems
- agent protocols
- UI primitives
- 3D infrastructure

## Architecture

Prefer:

- clear interfaces
- modular services
- replaceable providers
- isolated integrations
- strong boundaries
- explicit capabilities

Avoid:

- unnecessary coupling
- giant monolithic services
- model-specific assumptions
- external integrations embedded directly into core

## Testing

Do not assume something works because the code compiles.

Verify:

- actual application startup
- actual user flows
- actual integration behavior
- failure cases
- regressions

When possible, reproduce a failure before changing code.

## Debugging

Prefer root-cause diagnosis over speculative fixes.

When a bug appears:

1. reproduce
2. isolate
3. identify cause
4. fix cause
5. test fix
6. test regressions

## Scope Control

Do not allow future features to derail the current implementation
step.

Record future ideas separately and implement them when their phase
arrives.

## Security

Treat:

- terminal execution
- filesystem access
- API credentials
- plugins
- agent actions

as privileged capabilities requiring appropriate boundaries.

## Documentation

Important architectural decisions should be recorded with the reason
for the decision, not only the final implementation.