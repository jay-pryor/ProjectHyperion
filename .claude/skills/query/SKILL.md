---
name: query
description: "QUERY session: answer a question about the framework or the project. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "[scope]"
---
# QUERY session

Declared: !`mkdir -p .hyperion && printf 'QUERY\n' > .hyperion/session && echo "QUERY written to .hyperion/session; the scope hook enforces its globs"`

Arguments: `$ARGUMENTS`, the scope (or the question).

Output exactly:

    SESSION: QUERY
    SCOPE: $ARGUMENTS
    MAY MODIFY: nothing
    PRINCIPLE: <which of P1-P10 this change serves>

QUERY modifies nothing and may read anything, human-only documents included. It ends by
naming the session type that makes any change it uncovers (CORE-SES-001).

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
- `REGISTRY.md` (HYP-001)
- `agents/00-agent-index.md` (AGT-000)
- `agents/lens-determinism.md` (AGT-LNS-003)
- `agents/lens-numerical-integrity.md` (AGT-LNS-002)
- `agents/lens-partial-failure.md` (AGT-LNS-001)
- `agents/validation-review.md` (AGT-VAL-001)
- `agents/verification-review.md` (AGT-VER-001)
- `core/change-control/baseline-change-procedure.md` (CORE-CHG-002)
- `core/contracts/conformance-suites.md` (CORE-CON-002)
- `core/contracts/contract-definition.md` (CORE-CON-001)
- `core/decisions/decision-log.md` (CORE-DEC-001)
- `core/harness.md` (CORE-HRN-001)
- `core/imperatives.md` (CORE-IMP-001)
- `core/lessons/lesson-ladder.md` (CORE-LSN-001)
- `core/lifecycle/g0-hazard-context.md` (CORE-LFC-002)
- `core/lifecycle/g1-requirements-validation-basis.md` (CORE-LFC-003)
- `core/lifecycle/g2-architecture.md` (CORE-LFC-004)
- `core/lifecycle/g3-contracts.md` (CORE-LFC-005)
- `core/reviews/00-review-taxonomy.md` (CORE-REV-001)
- `core/reviews/lens-reviews.md` (CORE-REV-003)
- `core/reviews/review-findings-handling.md` (CORE-REV-005)
- `core/testing/test-strategy.md` (CORE-TST-001)
- `core/testing/tests-are-tested.md` (CORE-TST-002)
- `core/traceability/trace-logs.md` (CORE-TRC-003)
- `core/traceability/trace-records.md` (CORE-TRC-002)
- `core/traceability/traceability.md` (CORE-TRC-001)
- `profiles/simulation/validation-basis.md` (SIM-VAL-001)
- `templates/contract.md` (TPL-001)
- `templates/decision-record.md` (TPL-002)
- `templates/hazard-entry.md` (TPL-004)
- `templates/lesson.md` (TPL-003)
- `templates/module-CLAUDE.md` (TPL-007)
- `templates/module-map.md` (TPL-008)
- `templates/project-CLAUDE.md` (TPL-006)
- `templates/slice-definition.md` (TPL-005)
- `tooling/doc-frontmatter-schema.md` (TOOL-001)
- `whatever the question needs; the only type with no ceiling`

## Must not modify

everything.
A write outside `MAY MODIFY` is denied by the scope hook and rejected at commit (CORE-SES-001, CORE-HRN-001).

## Rules

Every change traces to a principle; one fact, one place; regenerate the registry and
the operating layer before finishing (HYP-002).
