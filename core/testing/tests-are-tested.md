---
id: CORE-TST-002
title: Tests Are Tested
tier: core
status: active
audience: [human, model]
load: on-task
sessions: [CONFORMANCE, IMPLEMENT, INTEGRATE]
prevents: A conformance suite that checks shape, not behaviour, and so passes a wrong implementation as readily as a right one
reader: The CONFORMANCE session writing a suite, the INTEGRATE session accepting a slice, and CI
related: [CORE-TST-001, CORE-CON-002, CORE-LFC-005, CORE-LSN-001, CORE-TRC-003]
---

# Tests Are Tested

A suite that cannot fail is assumed to be a control. For model-written code the
conformance suite is the primary control ([CORE-TST-001](test-strategy.md)), and a green
run says nothing about whether it discriminates: a suite that checks shape passes the
real implementation, a fixed-data stub, and a plausible wrong implementation equally.
[P8](../00-principles.md) makes the tests independent; this document makes them
falsifiable. Read by the CONFORMANCE session writing a suite, the INTEGRATE session
accepting a slice, and CI.

Three rungs, cheapest first. Each is a mechanical check ([P2](../00-principles.md)) and
each reports into `trace/` ([CORE-TRC-003](../traceability/trace-logs.md)).

## Rung 1 — the null double

Every module with a `src/` ships `modules/<m>/null_double.*`: a deliberately trivial
implementation that returns fixed, valid-looking data and enforces nothing. The contract
surface selects it when `<MODULE>_IMPL=null` is set (module name uppercased, `-` as
`_`), so the suite runs unchanged against it, which is the "any implementation" rule of
[CORE-CON-002](../contracts/conformance-suites.md) turned against the suite itself.

**The suite must fail against the null double** in each of `errors`, `invariants`, and
`boundaries` that exists, and may pass `operations`. A file the null double passes
checks shape, not behaviour: a weakness in the suite, fixed in a CONFORMANCE session by
adding the test that catches it, citing the clause it encodes ([P8](../00-principles.md)).

The null double is not the stand-in stub of [CORE-LFC-005](../lifecycle/g3-contracts.md).
A stub stands in for an unbuilt module and **must pass** the suite; the null double stands
in for a wrong one and **must fail** it. One file doing both jobs proves nothing about
either.

Enforced by `tooling/check_null_doubles.py <project_root>`: discovers every null double,
runs its module's `conformance/` under the variable, and fails on a module with `src/`
and no double, or on a required file with no failing test. CI runs it on every push.

## Rung 2 — the mutation score

At slice acceptance, the toolchain's mutation tool runs over `modules/<m>/src` for every
module the slice's `contracts:` names, with the test command restricted to that module's
`conformance/` plus `validation/`. `tests/` is excluded: a unit test written beside the
implementation can kill a mutant the conformance suite would miss, which is exactly the
masking [P8](../00-principles.md) forbids.

The score is killed / total, recorded as `mutation_score` on the slice
([CORE-TRC-002](../traceability/trace-records.md)). Every survivor is a finding with
`source: mutation`, `form: test`, `status: admitted`, and a `ref` naming the mutant and
its location: S2, or S1 when the mutated module is named by any hazard's
`mitigation_contract`, because a survivor there means the mitigation test cannot tell
the mitigation from its absence. Triage runs through the ordinary pipeline
([CORE-REV-005](../reviews/review-findings-handling.md)): killed by a conformance test
written in a CONFORMANCE session, at which point the finding is `fixed` and its ref is
the killing test, or `rejected` as equivalent with a reason. `survivors_triaged` is true
only when no mutation finding on the slice is still open, and an `accepted` slice with
open survivors is a trace break. On numerical code a survivor that only nudged a constant
is a tolerance that is too loose; the score is the number a human reads so that the
diffs need not be ([P5](../00-principles.md)).

`tooling/mutation_score.py --slice SL-nn <project_root>` runs the tool and prints the
score and the survivor rows; `--write` appends the rows and sets the slice fields.

## Rung 3 — the fault-point harness

`fault_point("name")` is a named point in an operation that does nothing in production
and raises when a test has called `arm("name")`. A conformance test arms one, forces the
failure at step N of a multi-step operation, asserts it propagates cleanly, and asserts
the module serves its contract afterwards. That is the reproducing test a partial-failure
finding ([AGT-LNS-001](../../agents/lens-partial-failure.md)) must carry to be admitted;
without the harness those findings are rejected by construction, and a finding that
cannot be recorded cannot become a lesson ([P9](../00-principles.md)).

The harness is baseline substrate ([CORE-LFC-004](../lifecycle/g2-architecture.md)),
copied from `templates/baseline/faults.py`. Points are placed by the IMPLEMENT session at
the steps a partial-failure finding names, after a call that can fail and before state is
committed, never speculatively. Every point in code must be armed by a passing
conformance test; the rule and its checker are in
[CORE-TRC-003](../traceability/trace-logs.md#fault-points).

## The fourth rung, not yet built

Review drills, a planted defect of a known class with the lens reviews run blind and the
result recorded under `source: drill`, measure what the lenses miss rather than what they
find; they plug in beside these three once the findings log has a quarter of data, and
nothing here links to them yet.
