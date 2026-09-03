---
name: review
description: "REVIEW session: run one agent from agents/ and record its findings. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "[scope]"
---
# REVIEW session

Declared: !`echo "REVIEW declared; the scope hook binds this session to its globs"`

Arguments: `$ARGUMENTS`, the scope (or the question).

Output exactly:

    SESSION: REVIEW
    SCOPE: $ARGUMENTS
    MAY MODIFY: `trace/findings.yaml`
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
- `agents/00-agent-index.md` (AGT-000)
- `agents/lens-determinism.md` (AGT-LNS-003)
- `agents/lens-numerical-integrity.md` (AGT-LNS-002)
- `agents/lens-partial-failure.md` (AGT-LNS-001)
- `agents/specification-review.md` (AGT-VAL-001)
- `agents/verification-review.md` (AGT-VER-001)
- `core/harness.md` (CORE-HRN-001)
- `core/reviews/00-review-taxonomy.md` (CORE-REV-001)
- `core/reviews/lens-reviews.md` (CORE-REV-003)
- `core/reviews/review-findings-handling.md` (CORE-REV-005)
- `core/traceability/trace-logs.md` (CORE-TRC-003)
- one agent file plus the inputs it permits, nothing else

## Must not modify

`modules/**`, `baseline/**`, `validation/**`, `docs/**` (append only).
A write outside `MAY MODIFY` is denied by the scope hook and rejected at commit (CORE-SES-001, CORE-HRN-001).

## Rules

Every change traces to a principle; one fact, one place; regenerate the registry and
the operating layer before finishing (HYP-002).
