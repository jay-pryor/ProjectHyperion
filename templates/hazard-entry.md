---
id: TPL-004
title: "Template — Hazard Trace Entry"
tier: templates
status: active
version: 0.2
audience: [human, model]
load: on-task
related: [CORE-LFC-002, CORE-TRC-001]
---

# Template — Hazard Trace Entry

Hyperion holds the **trace**, not the hazard assessment. The hazard is raised, assessed,
and tracked in the organisation's existing hazard management system; this record links it
to code, and is checked by `tooling/check_traces.py`.

Records are **flat** — scalar and inline-list values only. Nested structures are rejected
by the parser rather than silently mis-parsed.

Append to `trace/hazards.yaml`:

```yaml
- id: HZ-nnn
  org_hazard_id: <ID in the organisational register>
  org_system: <which register>
  never_statement: <plain language, checkable by a non-programmer>
  failure_mode: not_performed | performed_incorrectly | performed_wrong_time | performed_uncommanded | failed_silently
  severity: <per organisational scale>
  mitigation_contract: modules/<name>/contract.<ext>::<clause>
  mitigation_test: <test id, or TBD while status is proposed>
  mitigation_status: proposed | traced | verified
  requirement: REQ-nnn
```

## Rules the checker enforces

- `mitigation_contract` and `mitigation_test` are mandatory. A mitigation with no control
  is a statement of intent.
- `mitigation_test: TBD` is permitted **only** while `mitigation_status: proposed`, which
  makes TBD self-expiring at G3 rather than quietly permanent.
- A named test must appear in `trace/tests.txt`, so renaming a test breaks the build
  instead of breaking the trace silently.
- `requirement` must resolve to a record in `trace/requirements.yaml`.

## Rule the checker cannot enforce

`never_statement` is written for the G0 reviewer who does not read code. If it cannot be
written in plain language, the hazard is not yet understood — and no tool can tell you
that.
