---
name: release
description: "RELEASE session: name what a run of framework changes was, and cut the version for it. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "[scope]"
---
# RELEASE session

Declared: !`echo "RELEASE declared; the scope hook binds this session to its globs"`

Arguments: `$ARGUMENTS`, the scope (or the question).

Output exactly, then stop and wait for confirmation. Do not begin work in the same turn.

    SESSION: RELEASE
    SCOPE: $ARGUMENTS
    MAY MODIFY: `CHANGELOG.md`, `VERSION`, `README.md`, `REGISTRY.md`, `examples/**/.hyperion/version`
    PRINCIPLE: P8 - the session that made a change is the wrong one to summarise it

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

## Must not modify

`core/**`, `profiles/**`, `agents/**`, `templates/**`, `tooling/**`, `imperatives/**`, `.github/**`.
A write outside `MAY MODIFY` is denied by the scope hook and rejected at commit (CORE-SES-001, CORE-HRN-001).

## Checklist

Steps 3 and 4 are the human's; the rest run unattended. Stop at the first step that fails.
`CHANGELOG.md` (HYP-003) is what this session writes; it is human-audience, so it is not in
the loadout above.

1. Merge the working branch into `main`. Stop and report if it conflicts.
2. Read `git log <last tag>..HEAD` and the diff over the same range.
3. Draft the `CHANGELOG.md` entry from that diff, newest heading first. **Show it and stop.**
4. Propose the version number, with the reason it is that one and not the next up. **Show it and stop.**
5. Write `VERSION` and `CHANGELOG.md`, then `build_registry.py`, `build_layer.py`, and both `--check`s.
6. Commit with `Session: RELEASE`, push, `git tag v$(cat VERSION)`, push the tag.

A framework change discovered on the way is a FRAMEWORK session after the tag, not a step here.
