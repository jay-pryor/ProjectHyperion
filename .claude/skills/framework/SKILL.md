---
name: framework
description: "FRAMEWORK session: change the framework itself. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "[scope]"
---
# FRAMEWORK session

Declared: !`mkdir -p .hyperion && printf 'FRAMEWORK\n' > .hyperion/session && echo "FRAMEWORK written to .hyperion/session; the scope hook enforces its globs"`

Arguments: `$ARGUMENTS`, the scope (or the question).

Output exactly, then stop and wait for confirmation. Do not begin work in the same turn.

    SESSION: FRAMEWORK
    SCOPE: $ARGUMENTS
    MAY MODIFY: `core/**`, `profiles/**`, `agents/**`, `templates/**`, `tooling/**`, `examples/**`, `handbook/**`, `imperatives/**`, `.github/**`, `.claude/**`, `.devcontainer/**`, `.hyperion/**`, `.gitignore`, `CLAUDE.md`, `README.md`, `REGISTRY.md`
    PRINCIPLE: <which of P1-P10 this change serves>

## Load exactly

- `CLAUDE.md` (HYP-002)
- `README.md` (HYP-000)
- `core/00-principles.md` (CORE-PRN-001)
- `core/change-control/change-tiers.md` (CORE-CHG-001)
- `core/contracts/boundary-enforcement.md` (CORE-CON-003)
- `core/lifecycle/00-gates-overview.md` (CORE-LFC-001)
- `core/lifecycle/slice-loop.md` (CORE-LFC-006)
- `core/session-protocol.md` (CORE-SES-001)
- `profiles/simulation/PROFILE.md` (SIM-000)
- `profiles/simulation/determinism.md` (SIM-DET-001)
- `core/harness.md` (CORE-HRN-001)
- `core/imperatives.md` (CORE-IMP-001)
- `templates/project-CLAUDE.md` (TPL-006)
- `tooling/doc-frontmatter-schema.md` (TOOL-001)

## Must not modify

Nothing by path; every change traces to a principle (HYP-002).
A write outside `MAY MODIFY` is denied by the scope hook and rejected at commit (CORE-SES-001, CORE-HRN-001).

## Rules

Every change traces to a principle; one fact, one place; regenerate the registry and
the operating layer before finishing (HYP-002).
