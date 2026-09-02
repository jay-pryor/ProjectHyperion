---
id: TPL-001
title: "Template — Module Contract"
tier: templates
status: active
audience: [human, model]
load: on-task
sessions: [CONTRACT]
prevents: A contract that states signatures and omits the error conditions, promises, and tolerances people forget
reader: A CONTRACT session writing modules/<name>/CONTRACT.md
related: [CORE-CON-001, CORE-TRC-001]
---

# Template — Module Contract

Companion to the code contract file. Prose parts live here; parts 2–3 live in code.

```markdown
# Contract: <module-name>
Version: 1.0 · Status: draft | active | superseded

## 1. Purpose
<One sentence. If it needs "and", split the module or justify it in a decision record.>

## 2. Operations
<Signatures. In code; referenced here.>

## 3. Data shapes
<Types crossing the boundary. Units and frames in the type name.>

## 4. Error conditions
| Operation | Condition | Signalled as | Caller obligation |
|---|---|---|---|

## 5. Behavioural promises
- Ordering:
- Idempotency:
- Determinism:
- Null / empty semantics:
- Concurrency safety:
- Side effects:
- Tolerance / precision:

## 6. Performance envelope
<Complexity, latency budget, memory bound. Omit if genuinely unconstrained.>

## 7. Trace
<Requirement IDs this contract satisfies. The authoritative trace lives in
`trace/requirements.yaml` (allocated_to must name this module) and is checked by
`tooling/check_traces.py`. List IDs here for the reader; do not restate the mapping.>

- REQ-nnn, REQ-nnn

## Explicitly not promised
<Behaviour consumers must not depend on. This section prevents accidental coupling and is
worth writing even when it feels obvious.>
```
