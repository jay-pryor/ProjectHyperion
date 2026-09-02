---
id: CORE-TST-001
title: Test Strategy
tier: core
status: active
audience: [human, model]
load: on-task
sessions: [CONFORMANCE]
prevents: Tests that agree with the implementation's misreading, and coverage chased as a percentage instead of by clause
reader: A CONFORMANCE session choosing what to write, and the human deciding which tests to read
related: [CORE-CON-002, CORE-TST-002, CORE-PRN-001]
---

# Test Strategy

For LLM-generated code, tests are the primary control. Models produce plausible-looking
wrong code with total confidence, and reading it does not scale. Automated verification
is what makes cheap rework safe.

## The founding constraint

> A model asked to write implementation and tests together writes tests that agree with
> its own misunderstanding.

Both artifacts inherit the same misreading, everything passes, and you learn nothing.
Hence [P8](../00-principles.md): contract-level tests are written from human-written
acceptance criteria, before implementation, in a separate session. Independence is not
enough; whether the suite can fail at all is checked by [CORE-TST-002](tests-are-tested.md).

## Layers

Ordered by value per unit of maintenance.

| Layer | Written when | Written by | Read by you | Purpose |
|---|---|---|---|---|
| **Conformance** | G3, pre-implementation | Model, from human criteria | **Yes** | Encodes the contract |
| **Property** | G3 or slice | Model | Skim | Invariants, edge discovery |
| **Unit** | During slice | Model | No | Internal correctness |
| **Integration** | Per slice | Model | No | Slice works end to end |
| **End-to-end** | Critical path only | Model | No | The system does its job |
| **Validation** | Per G1 basis | Human-specified | **Yes** | Output is *right*, not just consistent |

Keep end-to-end deliberately thin. It is the most expensive layer to maintain and the
slowest to run, and it duplicates coverage that conformance already provides.

## Property-based testing

Use wherever an invariant exists: round-trips, ordering, idempotency, conservation,
monotonicity, dimensional consistency, state machine reachability. Models generate these
well and they find boundary cases example-based tests miss.

Seeds are fixed and recorded. An intermittent failure that cannot be reproduced is worse
than no test.

## Validation is not a test layer in the usual sense

Verification asks whether the code matches the contract. Validation asks whether the
answer is correct. Software can pass every layer above and be wrong, and in simulation
that is the *expected* failure mode rather than an unusual one. Validation evidence is
defined at [G1](../lifecycle/g1-requirements-validation-basis.md) and executed per the
profile.

## Coverage

Coverage is a diagnostic, not a target. Useful reading: *which contract clauses have no
test*. Not useful: a percentage. Chase the first, ignore the second.

## Test maintenance

A failing conformance test is resolved by reading the contract, never by making the test
pass; the rule and the session that may not touch the test are in
[CORE-SES-001](../session-protocol.md#the-load-bearing-prohibitions).
