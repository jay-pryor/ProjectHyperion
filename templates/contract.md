---
id: TPL-001
title: "Template — Module Contract"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-CON-001]
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
| Requirement ID | Hazard ID | Conformance test |
|---|---|---|

## Explicitly not promised
<Behaviour consumers must not depend on. This section prevents accidental coupling and is
worth writing even when it feels obvious.>
```
