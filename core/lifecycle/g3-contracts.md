---
id: CORE-LFC-005
title: "G3 — Contracts & Slice Plan"
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-LFC-004, CORE-LFC-006, CORE-CON-001, CORE-CON-002]
---

# G3 — Contracts & Slice Plan

Answers: **what exactly does each module promise, and in what order do we build?**

Classic equivalent: CDR. This is the last gate before code.

## Contracts

Every module gets a contract file and a conformance suite. See
[CORE-CON-001](../contracts/contract-definition.md) for what a contract contains and
[CORE-CON-002](../contracts/conformance-suites.md) for how behavioural promises are
encoded.

**Conformance suites are written at this gate, before implementation, from the G1
acceptance criteria — not from the implementation, and ideally not in the same session
that will write the implementation.** This is [P8](../00-principles.md), and it is the
single highest-leverage rule in Hyperion. A model that writes code and tests together
produces tests that confirm its own misreading, and everything passes.

The tests may be model-written. The **acceptance criteria they are written from** are
human-written, and reviewing those criteria is the highest-value hour you will spend on
the project.

## Slice plan

An ordered list of vertical slices. Each slice:

- Cuts through every layer it needs, however thinly.
- Has acceptance criteria stated as observable behaviour.
- Names the requirement IDs it satisfies and the hazard mitigations it implements.
- Is small enough to complete and review in one sitting.

**Slice 1 is the walking skeleton: the riskiest end-to-end path, not the easiest one.**
The purpose of the first slice is to validate the architecture, and an easy slice
validates nothing you needed to know. If the architecture is wrong, you want that
finding in week one while the Baseline Change gate is cheap.

Order the remainder by risk, not by convenience.

## Stub policy

Modules not yet built are stubbed at their contract, returning fixed valid data. Stubs
are conformance-tested like real implementations, which means a stub cannot silently
violate the contract it stands in for.

## Outputs

| Artifact | Consumed by |
|---|---|
| Contract file per module | Implementation sessions, all reviews |
| Conformance suite per contract | CI, slice acceptance |
| Ordered slice plan with acceptance criteria | Slice loop |
| Updated hazard trace (mitigation → contract clause → test ID) | Slice acceptance |

Use [templates/contract.md](../../templates/contract.md) and
[templates/slice-definition.md](../../templates/slice-definition.md).

## Exit criteria

- [ ] Every module has a contract
- [ ] Every contract has a conformance suite that currently fails (nothing implemented)
- [ ] Slice 1 is the riskiest path
- [ ] Every hazard mitigation traced to a contract clause and a named test
- [ ] Acceptance criteria human-written and human-reviewed
