---
id: HBK-005
title: Glossary
tier: handbook
status: active
audience: [human]
load: never
sessions: []
prevents: Attention spent on words instead of the work by a systems engineer who already has a term for the thing
reader: Anyone meeting a Hyperion term for the first time, and anyone reading records written before 0.6.0
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
| Specification review (agent `specification-review`, finding source and review kind `specification`) | Requirements validation; specification review: is the contract right | [CORE-PRN-001](../core/00-principles.md) P7, [CORE-REV-001](../core/reviews/00-review-taxonomy.md), [AGT-VAL-001](../agents/specification-review.md) |
| Validation, `validation_class`, `validated_by`, `validation/` cases | Validation against reference truth; M&S validation: is the answer right | [CORE-PRN-001](../core/00-principles.md) P7, [CORE-LFC-003](../core/lifecycle/g1-requirements-validation-basis.md), [SIM-VAL-001](../profiles/simulation/validation-basis.md) |
| *Former:* "validation review", lens `validation`, finding source `validation` | Requirements validation | Renamed specification review in 0.6.0; the ID `AGT-VAL-001` is kept |
| *Former:* "validation" unqualified, meaning either of the above | — | Since 0.6.0 unqualified "validation" always means the results-side question |
| Module contract (`CONTRACT.md`, `contract.*`) | Interface control document (ICD); interface specification | [CORE-CON-001](../core/contracts/contract-definition.md) |
| Contract clause `C-nnn` | Numbered interface requirement | [CORE-CON-001](../core/contracts/contract-definition.md) |
| Conformance suite | Qualification test; acceptance test procedure for an interface | [CORE-CON-002](../core/contracts/conformance-suites.md) |
| Dependency manifest, boundary enforcement | Allocated interface list; architecture conformance check | [CORE-CON-003](../core/contracts/boundary-enforcement.md) |
| Baseline | Configuration baseline (allocated, then product) | [CORE-CHG-002](../core/change-control/baseline-change-procedure.md), [CORE-LFC-004](../core/lifecycle/g2-architecture.md) |
| Change tiers: Internal, Interface, Baseline | Change classification (Class I / Class II); engineering change proposal levels | [CORE-CHG-001](../core/change-control/change-tiers.md) |
| Decision record with reversal cost | Trade study record; architecture decision record | [CORE-DEC-001](../core/decisions/decision-log.md) |
| Slice | Increment; build; thread | [CORE-LFC-005](../core/lifecycle/g3-contracts.md), [TPL-005](../templates/slice-definition.md) |
| Walking skeleton | First integrated thread through every layer | [CORE-LFC-005](../core/lifecycle/g3-contracts.md) |
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

## The two former meanings of validation

Before 0.6.0 "validation" named both the requirements-side question, is the contract the
right one, and the results-side question, is the answer right against reference truth.
The first is now **specification review** everywhere: [P7](../core/00-principles.md), the
agent, the lens name, the finding source, and the review kind. The second keeps the word:
a `validation_class` on every requirement and a case under `validation/`. The two
*Former* rows above are the mapping for a reader of older records or notes.
