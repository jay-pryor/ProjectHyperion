---
name: gate
description: "GATE session: produce or review g0-g3 artifacts and record gate passage. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "[SL-nn] [scope]"
---
# GATE session

Declared: !`echo "GATE declared; the scope hook binds this session to its globs"`

Arguments: `$ARGUMENTS`. The first token is the slice (`SL-nn`), the rest is the scope.

Output exactly, then stop and wait for confirmation. Do not begin work in the same turn.

    SESSION: GATE
    SLICE: <first token of the arguments, or n/a>
    SCOPE: <the rest of the arguments>
    MAY MODIFY: `docs/**`, `trace/**`
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
- `hyperion/core/decisions/decision-log.md` (CORE-DEC-001)
- `hyperion/core/harness.md` (CORE-HRN-001)
- `hyperion/core/lifecycle/g0-hazard-context.md` (CORE-LFC-002)
- `hyperion/core/lifecycle/g1-requirements-validation-basis.md` (CORE-LFC-003)
- `hyperion/core/lifecycle/g2-architecture.md` (CORE-LFC-004)
- `hyperion/core/lifecycle/g3-contracts.md` (CORE-LFC-005)
- `hyperion/core/reviews/lens-reviews.md` (CORE-REV-003)
- `hyperion/core/traceability/traceability.md` (CORE-TRC-001)
- `hyperion/core/traceability/trace-records.md` (CORE-TRC-002)
- `hyperion/profiles/simulation/validation-basis.md` (SIM-VAL-001)
- `hyperion/templates/decision-record.md` (TPL-002)
- `hyperion/templates/hazard-entry.md` (TPL-004)
- `hyperion/templates/slice-definition.md` (TPL-005)
- `hyperion/templates/module-map.md` (TPL-008)
- `docs/decisions/**`
- `trace/**`

## Must not modify

`modules/**`, `baseline/**`, `validation/**`.
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
