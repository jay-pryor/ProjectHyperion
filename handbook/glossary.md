---
id: HBK-005
title: Glossary
tier: handbook
status: active
version: 0.1
audience: [human]
load: never
sessions: []
related: [HBK-000, CORE-PRN-001, CORE-LFC-001, CORE-TRC-001, CORE-REV-001, CORE-CHG-001]
---

# Glossary

Hyperion names things its own way, and its stated audience, a systems engineer who does
not read code, already has a vocabulary for most of them. A reader who cannot map
"conformance suite" to "qualification test" spends attention on words instead of on the
work, and "validation" in particular means two things in the wider field. Read by anyone
meeting a Hyperion term for the first time. Each row names the nearest
systems-engineering term and the document that defines the Hyperion one; the definition
lives there, not here.

| Hyperion term | Nearest SE term | Defined in |
|---|---|---|
| G0 Hazard & Context | Functional hazard assessment (FHA) | [CORE-LFC-002](../core/lifecycle/g0-hazard-context.md) |
| G1 Requirements & Validation Basis | System requirements review (SRR) | [CORE-LFC-003](../core/lifecycle/g1-requirements-validation-basis.md) |
| G2 Architecture | Preliminary design review (PDR) | [CORE-LFC-004](../core/lifecycle/g2-architecture.md) |
| G3 Contracts & Slice Plan | Critical design review (CDR) | [CORE-LFC-005](../core/lifecycle/g3-contracts.md) |
| Gate row (`kind: gate` in `trace/reviews.yaml`) | Review board minute; milestone sign-off | [CORE-TRC-003](../core/traceability/trace-logs.md) |
| Never-statement, never-list | Safety requirement stated as a prohibition; hazard control | [CORE-LFC-002](../core/lifecycle/g0-hazard-context.md) |
| The five G0 questions (`failure_mode`) | Functional failure modes of an FHA | [CORE-LFC-002](../core/lifecycle/g0-hazard-context.md) |
| Hazard trace, `register: org` or `local` | Hazard log entry linking to the hazard tracking system | [CORE-TRC-002](../core/traceability/trace-records.md), [TPL-004](../templates/hazard-entry.md) |
| Requirements register | Requirements specification | [CORE-TRC-002](../core/traceability/trace-records.md) |
| Needs, assumptions, goals | Stakeholder needs; assumptions register; non-verifiable intents | [CORE-TRC-003](../core/traceability/trace-logs.md) |
| Requirements view, `--report` matrix | Verification cross-reference matrix (VCRM); requirements traceability matrix | [CORE-TRC-001](../core/traceability/traceability.md) |
| `verification_method`: test, analysis, inspection, demonstration | The four verification methods | [CORE-TRC-002](../core/traceability/trace-records.md) |
| Verification | Verification: does the implementation satisfy the contract | [CORE-PRN-001](../core/00-principles.md) P7 |
| Specification review (finding source `specification`) | Requirements validation; specification review: is the contract right | [CORE-REV-001](../core/reviews/00-review-taxonomy.md) |
| Validation, `validation_class`, `validation/` cases | Validation against reference truth; M&S validation: is the answer right | [CORE-LFC-003](../core/lifecycle/g1-requirements-validation-basis.md), [SIM-VAL-001](../profiles/simulation/validation-basis.md) |
| Module contract (`CONTRACT.md`, `contract.*`) | Interface control document (ICD); interface specification | [CORE-CON-001](../core/contracts/contract-definition.md) |
| Contract clause `C-nnn` | Numbered interface requirement | [CORE-CON-001](../core/contracts/contract-definition.md) |
| Conformance suite | Qualification test; acceptance test procedure for an interface | [CORE-CON-002](../core/contracts/conformance-suites.md) |
| Dependency manifest, boundary enforcement | Allocated interface list; architecture conformance check | [CORE-CON-003](../core/contracts/boundary-enforcement.md) |
| Baseline | Configuration baseline (allocated, then product) | [CORE-CHG-002](../core/change-control/baseline-change-procedure.md), [CORE-LFC-004](../core/lifecycle/g2-architecture.md) |
| Change tiers: Internal, Interface, Baseline | Change classification (Class I / Class II); engineering change proposal levels | [CORE-CHG-001](../core/change-control/change-tiers.md) |
| Decision record with reversal cost | Trade study record; architecture decision record | [CORE-DEC-001](../core/decisions/decision-log.md) |
| Slice | Increment; build; thread | [CORE-LFC-005](../core/lifecycle/g3-contracts.md), [TPL-005](../templates/slice-definition.md) |
| Walking skeleton | First integrated thread through every layer | [TPL-005](../templates/slice-definition.md) |
| Acceptance criteria, acceptance record | Acceptance test requirements; acceptance test report | [CORE-LFC-006](../core/lifecycle/slice-loop.md), [TPL-005](../templates/slice-definition.md) |
| Gate review | Design review; milestone review | [CORE-REV-002](../core/reviews/gate-reviews.md) |
| Lens review | Independent review scoped to one failure mode | [CORE-REV-003](../core/reviews/lens-reviews.md) |
| Targeted human read | Scoped inspection where automated checks cannot reach | [CORE-REV-004](../core/reviews/targeted-human-reads.md) |
| Finding, `form: test` or `clause`, S1 to S4 | Discrepancy report; problem report with severity class | [CORE-REV-005](../core/reviews/review-findings-handling.md) |
| Rejected-findings list | Review calibration record | [CORE-REV-005](../core/reviews/review-findings-handling.md) |
| Lesson ladder, catch count | Lessons learned, promoted to a control; control effectiveness | [CORE-LSN-001](../core/lessons/lesson-ladder.md) |
| Null double, mutation score, fault point | Test-of-the-test; mutation testing; fault injection | [CORE-TST-002](../core/testing/tests-are-tested.md) |
| Session, declaration, STOP condition | Work package with a permission boundary; hold point | [CORE-SES-001](../core/session-protocol.md) |
| Imperative | Operating rule carried into every session | [CORE-IMP-001](../core/imperatives.md) |
| Console, evidence bundle | Acceptance data package; certification evidence | [HBK-001](artifact-map.md) |

## The two validations

The word "validation" appears in two places and means one thing in each. The
requirements-side question, is the contract the right one, is a **specification review**:
finding source `specification`, review kind `specification`. The agent file that runs it
is still titled validation review ([AGT-VAL-001](../agents/validation-review.md)); the
record vocabulary already uses the new name. The results-side question, is the answer
right against reference truth, is **validation**: a `validation_class` on every
requirement and a case under `validation/`. Where a document uses "validation" without
qualification, it means the second.
