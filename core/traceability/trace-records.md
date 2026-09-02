---
id: CORE-TRC-002
title: Trace Records — Registers
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [GATE, CONTRACT, CONFORMANCE]
related: [CORE-TRC-001, CORE-TRC-003, CORE-LFC-002, CORE-LFC-003, CORE-LFC-005, CORE-CON-001, TPL-004, TPL-005]
---

# Trace Records — Registers

A record with no schema is validated by whoever last edited it. This is the single
schema for the three registers in `trace/`: requirements, hazards, slices. The logs and
the results file are in [CORE-TRC-003](trace-logs.md). Read by the session writing a
record and by `tooling/check_traces.py`, which enforces every rule here; rationale in
[CORE-TRC-001](traceability.md). Records are flat; IDs are `PREFIX-nnn`, unique, never
reused; every reference resolves or CI fails ([P2](../00-principles.md)).

## Where named artifacts live

An artifact the framework names must have a row here ([P6](../00-principles.md)).

| Artifact | Home |
|---|---|
| Requirements register | `trace/requirements.yaml` |
| Hazard trace (org or local register) | `trace/hazards.yaml`, by `register` |
| Slice plan and slice acceptance record | `trace/slices.yaml` status; prose in `docs/slices/` ([TPL-005](../../templates/slice-definition.md)) |
| Admitted and rejected findings | `trace/findings.yaml`, by `status` |
| Gate review, targeted read, inspection, lens records | `trace/reviews.yaml`, by `kind` |
| Stakeholder needs, assumptions, goals | `trace/needs.yaml`, `assumptions.yaml`, `goals.yaml` |
| Interface and baseline change log | `trace/changes.yaml`, each row citing a DEC or FND |
| Test results | `trace/results.xml`, generated |
| Module map (G2) | `docs/module-map.md` from the manifests |
| Decision records | `docs/decisions/DEC-nnn.md` ([CORE-DEC-001](../decisions/decision-log.md)) |

## Requirement

```yaml
- id: REQ-nnn
  statement: <shall-statement, one observable behaviour>
  kind: functional | cross-cutting
  source: HZ-nnn | STK-nnn | ASM-nnn | GOAL-nnn      # one or a list; all resolve
  allocated_to: <module>                              # functional: exactly one module
                                                      # cross-cutting: a list, or baseline
  verification_method: test | analysis | inspection | demonstration
  verified_by: [<test id>]                            # test: full ids under conformance/
                                                      # otherwise: REV-nnn
  validation_class: analytical | conservation | invariant | degenerate | reference | convergence | expert_judgement
  validated_by: <test id under validation/> | REV-nnn # REV only for expert_judgement
  status: proposed | traced | verified
```

Modules are discovered from `modules/*/contract.*` plus `baseline`; there is no list to
maintain. `verified` requires every verifying and validating reference to have passed
(a test in `results.xml`; a review with disposition `passed` or `no_findings`).
`TBD` is allowed only while `proposed`; once G3 has passed, `proposed` is an error, as is
a requirement no slice claims. Test-id rules are in [CORE-TRC-003](trace-logs.md).
Validation classes are those of [G1](../lifecycle/g1-requirements-validation-basis.md).

## Hazard

```yaml
- id: HZ-nnn
  register: org | local
  org_hazard_id: <ID in the organisational register>  # org only; forbidden for local
  org_system: <which register>                        # org only
  severity: <integer, profile scale>                  # local only; forbidden for org
  likelihood: <integer, profile scale>                # local only
  never_statement: <plain language, checkable by a non-programmer>
  failure_mode: not_performed | performed_incorrectly | performed_wrong_time | performed_uncommanded | failed_silently
  mitigation_contract: modules/<m>/CONTRACT.md::C-nnn # TBD only while proposed
  mitigation_test: <full test id under conformance/>  # TBD only while proposed
  mitigation_status: proposed | traced | verified
  requirement: REQ-nnn                                # one or a list; all resolve
```

`register: org` means assessment lives in the organisation's system and Hyperion holds
only the trace; `local` is the single-operator fallback and carries the assessment
itself. `failure_mode` is one of the five [G0](../lifecycle/g0-hazard-context.md)
questions, so the console can show which questions a function's hazards cover. Both
halves of `mitigation_contract` resolve: the path exists under that module and the
clause is a marked `C-nnn` in its `CONTRACT.md` ([CORE-CON-001](../contracts/contract-definition.md)).
`verified` requires the mitigation test to have passed.

## Slice

```yaml
- id: SL-nn
  name: <name>
  requirements: [REQ-nnn]
  hazards: [HZ-nnn]
  contracts: [<module>]                 # contracts this slice touches
  status: planned | in_progress | accepted
  mutation_score: <0 to 1>              # acceptance record; killed / total
  survivors_triaged: true | false       # every survivor has a findings row, source mutation
```

An `accepted` slice may claim only `verified` requirements and hazards, whatever the
gate state. The last two fields are optional until acceptance; they are the
mechanical half of the acceptance record in [TPL-005](../../templates/slice-definition.md).
