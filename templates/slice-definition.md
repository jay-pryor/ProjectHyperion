---
id: TPL-005
title: "Template — Slice Definition"
tier: templates
status: active
audience: [human, model]
load: on-task
sessions: [GATE, CONTRACT]
prevents: A slice without observable acceptance criteria, or one that grows past what can be reviewed in one sitting
reader: GATE and CONTRACT sessions writing docs/slices/SL-nn.md, and the human writing the criteria
related: [CORE-LFC-005, CORE-LFC-006, CORE-TRC-001, CORE-TRC-002]
---

# Template — Slice Definition

```markdown
# SL-nn: <name>
Order: <n> · Risk: high | medium | low

## Scope
<What this slice makes work, end to end. Name the layers it cuts through.>

## Acceptance criteria
<Observable behaviour. Human-written. This is the highest-value text in the project —
every conformance test inherits its reading.>
1.
2.

## Satisfies
<Mirror this into `trace/slices.yaml`, the authoritative record. Its schema is the Slice
section of CORE-TRC-002; the checker fails if a slice claims a requirement or hazard
that does not exist, and an accepted slice may claim only verified ones.>

## Contracts touched
<If any need to change, run the Interface or Baseline gate BEFORE starting.>

## Lenses to run
<Select per CORE-REV-003. Two to four.>

## Out of scope
<Explicit. Prevents scope creep mid-slice, which is the main way slices stop being
reviewable in one sitting.>

## Acceptance record
- Date:
- Findings raised / disposition:
- Lessons promoted:
- Decision records created:
- Hands-on use completed: yes/no
- Mutation score and survivors triaged: mirrored to `trace/slices.yaml` (CORE-TRC-002)
- Traces updated and `check_traces.py` green: yes/no
```

## Ordering rule

Slice 1 is the walking skeleton and the rest are ordered by risk:
[CORE-LFC-005](../core/lifecycle/g3-contracts.md#slice-plan).
