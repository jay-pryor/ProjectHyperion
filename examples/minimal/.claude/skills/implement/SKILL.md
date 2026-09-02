---
name: implement
description: "IMPLEMENT session: build a slice to contract. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "[SL-nn] [scope]"
---
# IMPLEMENT session

Declared: !`mkdir -p .hyperion && printf 'IMPLEMENT\n' > .hyperion/session && echo "IMPLEMENT written to .hyperion/session; the scope hook enforces its globs"`

Arguments: `$ARGUMENTS`. The first token is the slice (`SL-nn`), the rest is the scope.

Output exactly, then stop and wait for confirmation. Do not begin work in the same turn.

    SESSION: IMPLEMENT
    SLICE: <first token of the arguments, or n/a>
    SCOPE: <the rest of the arguments>
    MAY MODIFY: `modules/*/src/**`, `modules/*/tests/**`, `trace/**`
    LOADED: <the IDs below, once read>

## Load exactly

- `hyperion/core/change-control/change-tiers.md` (CORE-CHG-001)
- `hyperion/core/contracts/boundary-enforcement.md` (CORE-CON-003)
- `hyperion/core/lifecycle/00-gates-overview.md` (CORE-LFC-001)
- `hyperion/core/lifecycle/slice-loop.md` (CORE-LFC-006)
- `hyperion/core/00-principles.md` (CORE-PRN-001)
- `hyperion/core/session-protocol.md` (CORE-SES-001)
- `hyperion/profiles/simulation/PROFILE.md` (SIM-000)
- `hyperion/profiles/simulation/determinism.md` (SIM-DET-001)
- `hyperion/core/harness.md` (CORE-HRN-001)
- `hyperion/core/testing/tests-are-tested.md` (CORE-TST-002)
- `modules/<module>/CONTRACT.md`
- `modules/<module>/CLAUDE.md`
- `docs/slices/<slice>.md`

## Must not modify

`modules/*/contract.*`, `modules/*/CONTRACT.md`, `modules/*/conformance/**`, `baseline/**`, `validation/**`, `fixtures/**`.
A write outside `MAY MODIFY` is denied by the scope hook and rejected at commit (CORE-SES-001, CORE-HRN-001).

## Stop conditions

- The slice cannot be built within existing contracts.
- You need something a contract does not expose.
- A change would touch `baseline/` and this is not a BASELINE session.
- An acceptance criterion is ambiguous or unfalsifiable.
- A conformance test appears to contradict its contract.
- A change would alter the shape of existing persisted data.
- You have made more than five edits without a passing test run.
- You are about to write a second implementation of something that already exists.
- A change would perturb an existing RNG stream. *(Simulation)*

Stop, state the condition, and end the session; do not work around it (CORE-SES-001).
