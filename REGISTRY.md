---
id: HYP-001
title: Registry
tier: root
status: active
version: 0.1
audience: [human, model]
load: reference
related: [HYP-000]
---

# Registry

<!-- GENERATED FILE — do not edit. Run: python tooling/build_registry.py -->

Generated 2026-09-02 · 48 documents

## Standing context loadout

Documents tagged `load: always`. Keep this list short — every entry costs
context budget in every session.

- `HYP-002` [Framework Operating Instructions](CLAUDE.md)
- `HYP-000` [Hyperion](README.md)
- `CORE-PRN-001` [Principles](core/00-principles.md)
- `CORE-CHG-001` [Change Tiers](core/change-control/change-tiers.md)
- `CORE-CON-003` [Boundary Enforcement](core/contracts/boundary-enforcement.md)
- `CORE-LFC-001` [Gate Overview](core/lifecycle/00-gates-overview.md)
- `CORE-LFC-006` [Slice Loop](core/lifecycle/slice-loop.md)
- `CORE-SES-001` [Session Protocol](core/session-protocol.md)
- `SIM-000` [Simulation Profile](profiles/simulation/PROFILE.md)
- `SIM-DET-001` [Determinism](profiles/simulation/determinism.md)

## root

| ID | Title | Status | Load | Sessions | Path |
|---|---|---|---|---|---|
| `HYP-002` | Framework Operating Instructions | active | always |  | [CLAUDE.md](CLAUDE.md) |
| `HYP-000` | Hyperion | active | always |  | [README.md](README.md) |
| `HYP-001` | Registry | active | reference |  | [REGISTRY.md](REGISTRY.md) |

## core

| ID | Title | Status | Load | Sessions | Path |
|---|---|---|---|---|---|
| `CORE-PRN-001` | Principles | active | always |  | [core/00-principles.md](core/00-principles.md) |
| `CORE-CHG-002` | Baseline Change Procedure | active | on-task | BASELINE | [core/change-control/baseline-change-procedure.md](core/change-control/baseline-change-procedure.md) |
| `CORE-CHG-001` | Change Tiers | active | always |  | [core/change-control/change-tiers.md](core/change-control/change-tiers.md) |
| `CORE-CON-003` | Boundary Enforcement | active | always |  | [core/contracts/boundary-enforcement.md](core/contracts/boundary-enforcement.md) |
| `CORE-CON-002` | Conformance Suites | active | on-task | CONTRACT, CONFORMANCE | [core/contracts/conformance-suites.md](core/contracts/conformance-suites.md) |
| `CORE-CON-001` | Contract Definition | active | on-task | CONTRACT | [core/contracts/contract-definition.md](core/contracts/contract-definition.md) |
| `CORE-DEC-001` | Decision Log | active | on-task | GATE, CONTRACT, BASELINE | [core/decisions/decision-log.md](core/decisions/decision-log.md) |
| `CORE-IMP-001` | Imperatives | active | on-task | FRAMEWORK | [core/imperatives.md](core/imperatives.md) |
| `CORE-LSN-001` | Lesson Ladder | active | on-task | LESSON | [core/lessons/lesson-ladder.md](core/lessons/lesson-ladder.md) |
| `CORE-LFC-001` | Gate Overview | active | always |  | [core/lifecycle/00-gates-overview.md](core/lifecycle/00-gates-overview.md) |
| `CORE-LFC-002` | G0 — Hazard & Context | active | on-task | GATE | [core/lifecycle/g0-hazard-context.md](core/lifecycle/g0-hazard-context.md) |
| `CORE-LFC-003` | G1 — Requirements & Validation Basis | active | on-task | GATE | [core/lifecycle/g1-requirements-validation-basis.md](core/lifecycle/g1-requirements-validation-basis.md) |
| `CORE-LFC-004` | G2 — Architecture | active | on-task | GATE | [core/lifecycle/g2-architecture.md](core/lifecycle/g2-architecture.md) |
| `CORE-LFC-005` | G3 — Contracts & Slice Plan | active | on-task | GATE | [core/lifecycle/g3-contracts.md](core/lifecycle/g3-contracts.md) |
| `CORE-LFC-006` | Slice Loop | active | always |  | [core/lifecycle/slice-loop.md](core/lifecycle/slice-loop.md) |
| `CORE-REV-001` | Review Taxonomy | active | on-task | REVIEW | [core/reviews/00-review-taxonomy.md](core/reviews/00-review-taxonomy.md) |
| `CORE-REV-002` | Gate Reviews | active | on-task |  | [core/reviews/gate-reviews.md](core/reviews/gate-reviews.md) |
| `CORE-REV-003` | Lens Reviews | active | on-task | GATE, REVIEW | [core/reviews/lens-reviews.md](core/reviews/lens-reviews.md) |
| `CORE-REV-005` | Review Findings Handling | active | on-task | REVIEW, CONFORMANCE, LESSON | [core/reviews/review-findings-handling.md](core/reviews/review-findings-handling.md) |
| `CORE-REV-004` | Targeted Human Reads | active | on-task |  | [core/reviews/targeted-human-reads.md](core/reviews/targeted-human-reads.md) |
| `CORE-SES-001` | Session Protocol | active | always |  | [core/session-protocol.md](core/session-protocol.md) |
| `CORE-TST-001` | Test Strategy | active | on-task | CONFORMANCE | [core/testing/test-strategy.md](core/testing/test-strategy.md) |
| `CORE-TST-002` | Tests Are Tested | active | on-task | CONFORMANCE, IMPLEMENT, INTEGRATE | [core/testing/tests-are-tested.md](core/testing/tests-are-tested.md) |
| `CORE-TRC-003` | Trace Records — Logs and Results | active | on-task | REVIEW, INTEGRATE, LESSON, BASELINE | [core/traceability/trace-logs.md](core/traceability/trace-logs.md) |
| `CORE-TRC-002` | Trace Records — Registers | active | on-task | GATE, CONTRACT, CONFORMANCE | [core/traceability/trace-records.md](core/traceability/trace-records.md) |
| `CORE-TRC-001` | Traceability | active | on-task | GATE | [core/traceability/traceability.md](core/traceability/traceability.md) |

## profile

| ID | Title | Status | Load | Sessions | Path |
|---|---|---|---|---|---|
| `SIM-000` | Simulation Profile | draft | always |  | [profiles/simulation/PROFILE.md](profiles/simulation/PROFILE.md) |
| `SIM-DET-001` | Determinism | draft | always |  | [profiles/simulation/determinism.md](profiles/simulation/determinism.md) |
| `SIM-RDS-001` | Targeted Human Reads — Simulation | draft | on-task |  | [profiles/simulation/targeted-reads.md](profiles/simulation/targeted-reads.md) |
| `SIM-VAL-001` | Validation Basis | draft | on-task | GATE, CONFORMANCE | [profiles/simulation/validation-basis.md](profiles/simulation/validation-basis.md) |

## agents

| ID | Title | Status | Load | Sessions | Path |
|---|---|---|---|---|---|
| `AGT-000` | Agent Index | active | on-task | REVIEW | [agents/00-agent-index.md](agents/00-agent-index.md) |
| `AGT-LNS-003` | Agent — Determinism Lens | draft | on-task | REVIEW | [agents/lens-determinism.md](agents/lens-determinism.md) |
| `AGT-LNS-002` | Agent — Numerical Integrity Lens | draft | on-task | REVIEW | [agents/lens-numerical-integrity.md](agents/lens-numerical-integrity.md) |
| `AGT-LNS-001` | Agent — Partial Failure Lens | active | on-task | REVIEW | [agents/lens-partial-failure.md](agents/lens-partial-failure.md) |
| `AGT-VAL-001` | Agent — Validation Review | active | on-task | REVIEW | [agents/validation-review.md](agents/validation-review.md) |
| `AGT-VER-001` | Agent — Verification Review | active | on-task | REVIEW | [agents/verification-review.md](agents/verification-review.md) |

## templates

| ID | Title | Status | Load | Sessions | Path |
|---|---|---|---|---|---|
| `TPL-001` | Template — Module Contract | active | on-task | CONTRACT | [templates/contract.md](templates/contract.md) |
| `TPL-002` | Template — Decision Record | active | on-task | GATE, CONTRACT, BASELINE | [templates/decision-record.md](templates/decision-record.md) |
| `TPL-004` | Template — Hazard Trace Entry | active | on-task | GATE | [templates/hazard-entry.md](templates/hazard-entry.md) |
| `TPL-003` | Template — Lesson | active | on-task | LESSON | [templates/lesson.md](templates/lesson.md) |
| `TPL-007` | Template — Module CLAUDE.md | active | on-task | LESSON | [templates/module-CLAUDE.md](templates/module-CLAUDE.md) |
| `TPL-008` | Template — Module Map | active | on-task | GATE | [templates/module-map.md](templates/module-map.md) |
| `TPL-006` | Template — Project CLAUDE.md | active | on-task | FRAMEWORK | [templates/project-CLAUDE.md](templates/project-CLAUDE.md) |
| `TPL-005` | Template — Slice Definition | active | on-task | GATE, CONTRACT | [templates/slice-definition.md](templates/slice-definition.md) |

## tooling

| ID | Title | Status | Load | Sessions | Path |
|---|---|---|---|---|---|
| `TOOL-001` | Document Frontmatter Schema | active | on-task | FRAMEWORK | [tooling/doc-frontmatter-schema.md](tooling/doc-frontmatter-schema.md) |

## Draft documents

- `SIM-000` Simulation Profile
- `SIM-DET-001` Determinism
- `SIM-RDS-001` Targeted Human Reads — Simulation
- `SIM-VAL-001` Validation Basis
- `AGT-LNS-003` Agent — Determinism Lens
- `AGT-LNS-002` Agent — Numerical Integrity Lens

