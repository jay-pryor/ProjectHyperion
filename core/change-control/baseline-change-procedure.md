---
id: CORE-CHG-002
title: Baseline Change Procedure
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-CHG-001, CORE-LFC-004, CORE-DEC-001]
---

# Baseline Change Procedure

The heavyweight gate. Everything downstream inherits a baseline change, so this is the
one place where full ceremony is justified.

## What is baseline

Enumerated per project at [G2](../lifecycle/g2-architecture.md). Typically:

- Shared types and domain vocabulary
- Persisted data schemas
- Configuration schema
- Error and logging conventions
- The module dependency graph
- Build and distribution mechanism
- Design tokens, where the profile has a UI
- Authentication and authorisation model, where the profile has one

## Procedure

1. **State the driver.** What forced this? A requirement change, a hazard, a defect
   class, or an architectural mistake found in a slice.
2. **Impact assessment.** Which modules inherit the change, which contracts break, what
   persisted data exists in the old shape.
3. **Migration plan.** Explicitly including existing data. Models write clean forward
   migrations and forget that records already exist in the old shape; this is a named
   [targeted human read](../reviews/targeted-human-reads.md).
4. **Decision record**, with rejected alternatives. It is what the BASELINE session that
   makes the change cites in its declaration ([CORE-SES-001](../session-protocol.md)).
5. **Re-enter at G2** with scoped re-review — only the affected part of the module map,
   not the whole architecture.
6. **Update the hazard trace** if any mitigation was allocated to a changed contract.
7. **Validation re-run**, not just verification. A baseline change can invalidate results
   that still pass their tests.

## Batching

Baseline changes should be batched where possible. Three separate baseline changes in a
week is a signal that G2 was under-done, and the correct response is to stop and
re-examine the decomposition rather than to keep paying the gate three times.

## Recording the frequency

Log every baseline change with its date and driver. The rate is the best available
metric for whether your up-front gates are calibrated. Trending toward zero after the
first month means G2 and G3 are doing their job. Staying high means they are not.
