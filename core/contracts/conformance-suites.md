---
id: CORE-CON-002
title: Conformance Suites
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [CONTRACT, CONFORMANCE]
related: [CORE-CON-001, CORE-TST-001, CORE-CHG-001]
---

# Conformance Suites

The executable half of a contract. A signature cannot express ordering, idempotency,
error conditions, or tolerance; the conformance suite can, and it runs.

## Role

1. **Encodes error conditions and behavioural promises** (contract parts 4 and 5,
   [CORE-CON-001](contract-definition.md)) so they are checked, not hoped for.
2. **Closes the change-tier loophole** — altering promised behaviour fails conformance,
   forcing the diff into `conformance/`, which classifies it as an Interface change
   ([CORE-CHG-001](../change-control/change-tiers.md)).
3. **Validates stubs** — a stub must pass the same suite as the real implementation, so a
   stub cannot silently lie about the contract it stands in for.

## Rules

**Written at G3, before implementation, from human-written acceptance criteria.**
[P8](../00-principles.md).

**Written in a separate session from the implementation.** Not merely a different
prompt — a different context. A model that has just designed an implementation will
write a suite shaped around it.

**Tests the contract, never the implementation.** No knowledge of internals, no mocking
of private collaborators, no assertions about how a result was reached. If a total
rewrite of the module would break a conformance test, that test is wrong.

**Runs against any implementation of the contract.** Real, stub, or a future replacement.
Parameterise the suite over the implementation where the language allows it.

## Structure

```
modules/<name>/
  contract.*
  conformance/
    operations.*      # signatures, happy path
    errors.*          # every documented error condition
    invariants.*      # property-based: round-trips, ordering, idempotency
    boundaries.*      # empty, null, min, max, degenerate
  src/                # implementation — private
  tests/              # unit tests — model-written, model-maintained, you do not read these
```

## Property-based testing

Anything with an invariant gets property tests rather than examples: round-trips,
ordering, idempotency, conservation, monotonicity, dimensional consistency. Models
generate these well, and they find the boundary cases example-based tests miss.

Fix the seed and record it. A property test that fails intermittently and cannot be
reproduced is worse than no test.

## Reading policy

**Conformance suites are the tests you personally read.** They are the encoded promise,
they are few, and a wrong conformance test silently invalidates everything downstream of
it. Unit tests are model-owned and you do not read them ([P5](../00-principles.md)).
