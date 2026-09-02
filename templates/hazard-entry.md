---
id: TPL-004
title: "Template — Hazard Trace Entry"
tier: templates
status: active
version: 0.3
audience: [human, model]
load: on-task
sessions: [GATE]
related: [CORE-LFC-002, CORE-TRC-001, CORE-TRC-002]
---

# Template — Hazard Trace Entry

Hyperion holds the **trace**, not the hazard assessment. With `register: org` the hazard
is raised, assessed, and tracked in the organisation's hazard management system and
this record links it to code; with `register: local` the record carries a small
assessment itself. Either way it is checked by `tooling/check_traces.py`.

The record schema, its field values, and every rule the checker enforces on it live in
one place: the Hazard section of [CORE-TRC-002](../core/traceability/trace-records.md).
Append the record to `trace/hazards.yaml`.

## Writing the entry

- `never_statement` first. It is written for the G0 reviewer who does not read code; if
  it cannot be written in plain language, the hazard is not yet understood, and no tool
  can tell you that.
- `failure_mode` is the [G0](../core/lifecycle/g0-hazard-context.md) question that
  raised it. A function whose hazards all sit under one question is a gap for the
  reviewer.
- `mitigation_contract` and `mitigation_test` may be `TBD` only while the mitigation is
  `proposed`, which makes TBD self-expiring at G3. The contract half names a marked
  clause `C-nnn` in the module's `CONTRACT.md` ([TPL-001](contract.md)), so a clause
  finding, a conformance test, and this trace all cite the same anchor.
- `requirement` may be a list. One hazard commonly drives several safety requirements.
