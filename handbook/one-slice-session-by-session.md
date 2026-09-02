---
id: HBK-004
title: One Slice, Session by Session
tier: handbook
status: active
audience: [human]
load: never
sessions: []
prevents: A reader who has only the session table being unable to tell a stop from a failure
reader: A person about to run their first slice
related: [HBK-000, HBK-002, CORE-SES-001, CORE-LFC-006, CORE-CHG-001, CORE-REV-005, CORE-TST-002, CORE-TRC-002]
---

# One Slice, Session by Session

The session table is a table until it has been watched running, and a reader who has only
the table cannot tell a stop from a failure. This is SL-01 of `examples/minimal`, the
walking skeleton, from selection to acceptance; every declaration, stop, and record below
corresponds to a file in the example. Read by a person about to run their first slice.

## Human: select the slice

G3 orders SL-01 first because it is the riskiest end-to-end path: config in, trajectory with
provenance out, through the integrator and the atmosphere contract, drag off so the answer
has a closed form. The human reads `docs/slices/SL-01.md`, confirms both contracts are at
version 1.0 and unchanged, and checks that G3 is recorded as passed (REV-004).

## Model: CONFORMANCE session, trajectory

    SESSION: CONFORMANCE
    SLICE: SL-01
    SCOPE: conformance suite for trajectory contract 1.0 from SL-01 acceptance criteria
    MAY MODIFY: modules/trajectory/conformance/**

It has never seen an implementation. From criterion 1 it writes
`test_vacuum_range_matches_closed_form_C101`, deriving the expected value from
v² sin 2θ / g, not from any code. From criteria 2 to 4 it writes the provenance,
determinism, and unknown-key tests, each named for its clause. It runs the suite: every
test fails, because nothing is implemented. Commit trailer: `Session: CONFORMANCE`.

## Model: IMPLEMENT session, trajectory, which stops

    SESSION: IMPLEMENT
    SLICE: SL-01
    SCOPE: src/integrator.py satisfying trajectory contract 1.0
    MAY MODIFY: modules/trajectory/src/**, modules/trajectory/tests/**, trace/**

The session writes the integrator and reaches the density call. Atmosphere contract 1.0
says nothing about altitudes above its modelled range, and a steep shot will query 100 km.
Two readings are defensible, return a number or refuse, so IMP-03 applies:

    STOP: atmosphere contract 1.0 is ambiguous above its modelled range.
    Reading A: density(h) returns the extrapolated value for any h.
    Reading B: density(h) raises for h outside a validated envelope.
    SL-01 cannot proceed until the contract says which.

## Human: Interface change CHG-001, three sessions

The human chooses reading B, because HZ-001 already says the engine must never report a
range from density outside the validated envelope; a contract that extrapolates cannot be
that hazard's control. The Interface sequence ([CORE-CHG-001](../core/change-control/change-tiers.md))
runs: a **CONTRACT** session takes atmosphere 1.0 to 1.1, adding clause C-003, the error
row, and criterion 5 (the version line changed, so the commit checker accepts it); a
**CONFORMANCE** session writes `test_errors.py`, three tests named for C-003, from
criterion 5; an **IMPLEMENT** session makes `src/exponential.py` enforce the envelope, and
a second resumes the integrator. CHG-001 in `trace/changes.yaml` records the driver and the
decision it cites; HZ-001's `mitigation_contract` now points at a clause that exists.

## Check: conformance green, null double red

`pytest -q` passes all 27 tests and writes `trace/results.xml`. `check_null_doubles.py` runs
each suite against its null double: atmosphere fails 2 of 3 in `test_errors`, 1 of 2 in
`test_invariants`, 1 of 1 in `test_boundaries`, the three files [CORE-TST-002](../core/testing/tests-are-tested.md) requires.

## Model: four REVIEW sessions, each a fresh context

Each is read-only, with one agent file and the permitted inputs, nothing else. Findings are
appended to `trace/findings.yaml` with their `form` ([CORE-REV-005](../core/reviews/review-findings-handling.md)).

- **Verification**: every clause satisfied. No findings.
- **Specification review** (contract only): "C-101 promises accuracy for `dt ≤ 0.01` but
  nothing bounds `dt` above that; a step of 10 s returns a confident wrong range."
  FND-003, form `clause`, S2. The human accepts it; a second Interface sequence, CHG-002,
  adds C-106.
- **Numerical integrity**: "The integrator skips the density call when drag is zero, so
  the envelope check in C-003 is bypassed on exactly the vacuum shots SL-01 exercises."
  FND-001, form `test`, S1. A second finding claims the ground-crossing interpolation
  error exceeds tolerance, but its test derives the expected value by running this
  implementation, which the lens output contract forbids: FND-002, `rejected`, reason given.
- **Determinism**: no mechanism found. No findings.

FND-001 is S1, so its test is written in a CONFORMANCE session from the clause, not from
the defect: `test_leaving_envelope_raises_C104`, a 2000 m/s shot at 80° that must raise.
It fails. An IMPLEMENT session makes the integrator query density on every step. It
passes. FND-001 becomes `fixed` with the test as its `ref`, which the checker verifies.

## Human: targeted reads, validation, and ten minutes of use

The simulation profile's list, not the whole code. Units at the atmosphere-to-trajectory
boundary: both sides use `Metres` from baseline; REV-005, no findings, which also verifies
REQ-006 by inspection. Provenance fields present in a real result: REV-006, an inspection
row, which validates REQ-004's expert-judgement class. Then the validation check against
the G1 basis: the analytical and convergence cases in `validation/analytical/`, written in
a CONFORMANCE session from the human's specification. Finally the human plots two shots.

## Model: LESSON session and acceptance

`SESSION: LESSON`, scope: promote FND-001 to a check, complete the acceptance record,
update trace; may modify `lessons/**`, `trace/**`, `docs/slices/SL-01.md`. LSN-001, "an
envelope check must live in the module that owns the model and be exercised on every
path", is already at rung 2: the C-104 test is the check, so no prose lesson is written.
The acceptance record is filled in, SL-01 becomes `accepted` in `trace/slices.yaml`,
REQ-002, REQ-004, REQ-005, and REQ-006 become `verified`, and the checker runs clean.

## Check: what the trail now contains

One accepted slice; two interface changes, each with a driver; three findings, two fixed
and one rejected with a reason; six review rows. Every requirement the slice claimed is
verified and validated by a named test or inspection row, and a reviewer who does not read
code can confirm it from the console without opening a source file.
