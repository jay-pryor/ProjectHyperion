---
id: TPL-004
title: "Template — Hazard Trace Entry"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-LFC-002]
---

# Template — Hazard Trace Entry

Hyperion holds the **trace**, not the hazard assessment. The hazard itself is raised,
assessed, and tracked in the organisation's existing hazard management system; this
record links it to code.

```yaml
hyperion_id: HZ-nnn
org_hazard_id: <ID in the organisational system>
org_system: <which register>

function: <the software function assessed>
failure_mode: not_performed | performed_incorrectly | performed_wrong_time |
              performed_uncommanded | failed_silently
description: <what happens>

severity: <per organisational scale>

mitigation:
  description: <how the software prevents or limits this>
  contract: <module/contract.* and the specific clause>
  test: <conformance or validation test ID>
  status: proposed | traced | verified

never_statement: <plain language, checkable by a non-programmer>
```

## Rules

- `mitigation.test` may be `TBD` before G3 and must be populated by slice acceptance.
- A mitigation with no named test is a statement of intent, not a control.
- `never_statement` is written for the G0 reviewer who does not read code. If it cannot be
  written in plain language, the hazard is not yet understood.
