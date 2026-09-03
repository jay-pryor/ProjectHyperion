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

A suite that cannot fail is assumed to be a control. For model-written code the conformance
suite is the primary control ([CORE-TST-001](test-strategy.md)), and a green run says
nothing about whether it discriminates: a suite that checks shape passes the real
implementation, a fixed-data stub, and a plausible wrong implementation equally.
[P8](../00-principles.md) makes the tests independent; this document makes them falsifiable.

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

The null double is not the stand-in stub of [CORE-LFC-005](../lifecycle/g3-contracts.md): a
stub stands in for an unbuilt module and **must pass** the suite, the null double stands in
for a wrong one and **must fail** it, and one file doing both proves nothing about either.

Enforced by `tooling/check_null_doubles.py <project_root>`: discovers every null double,
runs its module's `conformance/` under the variable, and fails on a module with `src/`
and no double, or on a required file with no failing test. CI runs it on every push.

## Rung 2 — the mutation score

At slice acceptance, the toolchain's mutation tool runs over `modules/<m>/src` for every
module the slice's `contracts:` names, with the test command restricted to that module's
`conformance/` plus `validation/`. `tests/` is excluded: a unit test written beside the
implementation can kill a mutant the conformance suite would miss, which is exactly the
masking [P8](../00-principles.md) forbids.

The score is killed / total, recorded per module in `mutation_score` on the slice
([CORE-TRC-002](../traceability/trace-records.md)), one entry per module in `contracts:`
and required at acceptance: without it a slice that never ran the tool is indistinguishable
from one whose suite killed everything. For the same reason a run finding no mutant is an
error rather than a score of zero, and the tool refuses a mutation toolchain whose major
version it has not been read against ([P2](../00-principles.md)).

Every survivor is a finding with `source: mutation`, `form: test`, `status: admitted`, and
a `ref` naming the mutant and its location. Severity follows the hazard register, not the
tool: a survivor says the suite cannot see the change, and whether that is a broken promise
or a behaviour nothing promised depends on whether a hazard rides on it — some
`mitigation_contract` resolving to `modules/<m>/CONTRACT.md`, which cannot move without
editing the register.

| | Hazard names the module | Every other module |
|---|---|---|
| Severity | S2 | S3, "defect not covered by any contract promise" |
| At acceptance | every survivor closed | the score did not fall |

That S3 row of [CORE-REV-005](../reviews/review-findings-handling.md) raises the question a
survivor deserves: should the contract have promised this? S1 is never assigned by the
tool — whether the gap lets silently wrong output through is read off the mutant, never off
its address — and minting one severity for every survivor empties the class it mints
([P5](../00-principles.md)).

There is no minimum score. A floor picked in advance is a number with no basis, which
[CORE-CON-001](../contracts/contract-definition.md) forbids of a tolerance, and equivalent
mutants give every module a different unreachable ceiling. A module's floor is instead the
highest score any previously accepted slice recorded for it: the first measurement sets its
own bar and after that it may not fall, derived at check time and never stored.

Triage is the ordinary pipeline (CORE-REV-005): killed by a conformance test written in a
CONFORMANCE session, at which point the finding is `fixed` and its ref is the killing test,
or `rejected` as equivalent with a reason. `survivors_triaged` is true only when no S2
mutation finding on the slice is open, and an `accepted` slice with one open is a trace
break; S3 rows are backlog and block nothing. On numerical code a survivor that only nudged
a constant is a tolerance that is too loose; the score is the number a human reads so that
the diffs need not be.

`tooling/mutation_score.py --slice SL-nn <project_root>` prints the scores and the survivor
rows; `--write` appends the S2 rows and sets the slice fields; `--triage <module>` appends
one module's rows on demand; `--check` measures again and fails on a score no longer
earned, one below its floor, or an S2 survivor with no row, which is the form CI runs.

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
