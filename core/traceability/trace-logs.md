---
id: CORE-TRC-003
title: Trace Records — Logs and Results
tier: core
status: active
audience: [human, model]
load: on-task
sessions: [REVIEW, INTEGRATE, LESSON, BASELINE]
prevents: Findings, reviews, and changes living in prose where they cannot be counted, filtered, or checked, so gate state ends up in a human's head
reader: The session appending a finding, review, or change row, and tooling/check_traces.py
related: [CORE-TRC-001, CORE-TRC-002, CORE-REV-002, CORE-REV-004, CORE-REV-005, CORE-CHG-002, CORE-LFC-001]
---

# Trace Records — Logs and Results

Findings, reviews, and changes that live in prose cannot be counted, filtered, or checked,
so gate state ends up in a human's head and the rejected-findings list ends up nowhere.
This is the schema for the append-only logs in `trace/` and for the generated results
file. Registers are in [CORE-TRC-002](trace-records.md). Read by the session appending a
row and by `tooling/check_traces.py`.

## Finding

```yaml
- id: FND-nnn
  date: YYYY-MM-DD
  slice: SL-nn
  source: lens:<name> | specification | gate | mutation | human | hands-on   # specification: is the contract right (P7)
  form: test | clause
  severity: S1 | S2 | S3 | S4                         # CORE-REV-005
  status: admitted | rejected | fixed | reopened
  ref: <test id> | <contract path>::C-nnn | REQ-nnn | HZ-nnn | DEC-nnn
                                                      # source mutation, while open: modules/<m>/src/<file>::<mutant>
  summary: <one line>
  reason: <why>                                       # required when rejected
```

The rejected list is the rows with `status: rejected`. `form` records which admission
criterion applied ([CORE-REV-005](../reviews/review-findings-handling.md)): a `test` finding
names a test that fails on current code; a `clause` finding names the record it proposes
to change. A `fixed` S1 or S2 `test` finding must name a passing test under
`conformance/` or `validation/`, because those severities are hazard or contract
violations and their test is written in a CONFORMANCE session, not beside the fix. A
`fixed` `clause` finding on a contract clause must be cited by a `changes.yaml` row;
that row is the evidence the contract changed.

## Review

```yaml
- id: REV-nnn
  kind: gate | targeted_read | inspection | lens | specification
  gate: G0 | G1 | G2 | G3 | G4                        # when kind is gate
  slice: SL-nn                                        # optional
  ref: REQ-nnn | HZ-nnn | SL-nn | DEC-nnn | <path>    # optional: what was reviewed
  subject: <one line>
  date: YYYY-MM-DD
  reviewer: <person and/or model, e.g. jay, claude-opus-5, self>
  disposition: passed | failed | pending | no_findings | findings_raised
  notes: <one line>
```

**Gate state is derived from these rows.** A gate has passed when a row with
`kind: gate` and that gate records `passed`; gates pass in order
([CORE-LFC-001](../lifecycle/00-gates-overview.md)). The checker switches from warnings to
errors on TBDs and unclaimed requirements when G3 has passed, and nothing else grants that
state. A requirement verified by analysis, inspection, or demonstration, or validated by
expert judgement, points at one of these rows, so a review is as traceable as a test. A
`targeted_read` row naming a slice is also a condition of that slice's acceptance
([CORE-REV-004](../reviews/targeted-human-reads.md#recording)).

## Needs, assumptions, goals, changes

```yaml
- id: STK-nnn                     # trace/needs.yaml
  statement: <what a stakeholder needs>
  owner: <who can say whether it is met>
- id: ASM-nnn                     # trace/assumptions.yaml
  statement: <what is assumed>
  owner: <who owns the assumption>
  revisit_when: <the condition that invalidates it>
- id: GOAL-nnn                    # trace/goals.yaml; judged by a human, never tested
  statement: <intent>
- id: CHG-nnn                     # trace/changes.yaml
  date: YYYY-MM-DD
  tier: interface | baseline      # CORE-CHG-001
  driver: <one line>
  ref: DEC-nnn | FND-nnn          # the decision or finding that drove it
  contracts: [<module>]
```

The change log's rate is the calibration metric for G2 and G3
([CORE-CHG-002](../change-control/baseline-change-procedure.md)).

## Results

`trace/results.xml` is the JUnit report the test runner writes, generated immediately
before the check and never committed:

    pytest --junitxml=trace/results.xml       # in pytest.ini addopts for the example

A traced test id is a full node id (`path::name`) and must resolve to a case in this file
that **passed**. Skipped, expected-to-fail, and failed are trace breaks. Only tests under
`modules/*/conformance/` or `validation/` may be traced; a test under `tests/` is
rejected as model-owned ([CORE-TRC-001](traceability.md)). A parametrised family is
named without its brackets and is satisfied only if every collected member passed.

## Fault points

Every `fault_point("name")` literal under `modules/*/src/` or `baseline/` must be armed
by at least one test under `modules/*/conformance/` (`arm("name")`) that passed. A fault
point nothing exercises is dead code, not the control the partial-failure lens
([AGT-LNS-001](../../agents/lens-partial-failure.md)) needs.
