---
id: CORE-LFC-003
title: "G1 — Requirements & Validation Basis"
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [GATE]
related: [CORE-LFC-002, CORE-LFC-004, CORE-TST-001]
---

# G1 — Requirements & Validation Basis

Answers two questions together, deliberately: **what must it do**, and **how will we
know the answer is right?**

## Why these are one gate

Requirements written without a validation basis produce software that passes its tests
and is wrong. This is the dominant failure mode in simulation and analysis software,
where output is plausible-looking numbers rather than a crash.

Writing "how would I know this is correct?" next to every requirement, before any
architecture exists, forces the question while it is still cheap to answer. Where the
honest answer is *I could not tell*, that is a finding, and it is better found here than
after six weeks of implementation.

## Requirements

Each requirement is:

- **Atomic** — one testable statement.
- **Identified** — stable ID, referenced by contracts and tests.
- **Traced** — upward to a hazard, a stakeholder need, or an explicit assumption.
- **Verifiable** — states the observable, not the implementation.

Requirements that cannot be made verifiable are recorded as **goals** in a separate
section. Goals are legitimate and are not tested. Mixing them into requirements is what
produces untestable specifications.

## Validation basis

For each requirement, name the evidence that would establish correctness:

| Evidence class | Example |
|---|---|
| Analytical | Closed-form solution the output must match within tolerance |
| Conservation | Energy, momentum, mass, count balance across the run |
| Invariant | Round-trip identity, ordering, monotonicity, dimensional consistency |
| Degenerate case | Known answer at a limit (zero input, infinite range, stationary target) |
| Reference data | Trusted external dataset, prior tool, published result |
| Expert judgement | A named human inspects a named output |

Expert judgement is a legitimate entry and should be used where nothing better exists —
but it is recorded as such, so the confidence level of the whole system is visible.

Profile-specific expansion: [SIM-VAL-001](../../profiles/simulation/validation-basis.md).

## Outputs

| Artifact | Consumed by |
|---|---|
| Requirements register (IDs, statements, traces) | G2, G3, conformance suites |
| Validation basis table (requirement → evidence class → specific case) | Validation reviews, slice acceptance |
| Assumptions register | Lens reviews, later re-validation |
| Goals list (non-verifiable intents) | Human judgement at acceptance |

## Exit criteria

- [ ] Every requirement atomic, identified, traced, verifiable
- [ ] Every requirement has a named validation evidence class
- [ ] Requirements with no available evidence flagged explicitly as a risk
- [ ] Assumptions written down rather than held in your head
