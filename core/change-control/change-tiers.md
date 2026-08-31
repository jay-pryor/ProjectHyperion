---
id: CORE-CHG-001
title: Change Tiers
tier: core
status: active
version: 0.1
audience: [human, model]
load: always
related: [CORE-PRN-001, CORE-CON-001, CORE-CHG-002]
---

# Change Tiers

Three tiers. Rigour follows reversibility ([P1](../00-principles.md)).

| Tier | Definition | Cost to unwind | Gate |
|---|---|---|---|
| **Internal** | Changes inside a module that leave its contract untouched | Minutes | None |
| **Interface** | Changes a module's contract | Hours to days | Light |
| **Baseline** | Changes shared substrate all modules inherit | Days to weeks | Heavy |

## Classification is mechanical, not a judgement call

Tier is determined by **file path**, so CI can classify any diff and so can a model.
There is no argument about which tier you are in.

| Path touched | Tier |
|---|---|
| `baseline/**` | Baseline |
| `modules/<name>/contract.*` | Interface |
| `modules/<name>/conformance/**` | Interface |
| anything else under `modules/<name>/` | Internal |

If a diff spans tiers, the highest tier applies to the whole change.

## The behavioural loophole, and how it is closed

A signature can stay identical while behaviour changes — error conditions, ordering,
idempotency, null semantics, tolerance. That is an interface change wearing internal
clothes.

The [conformance suite](../contracts/conformance-suites.md) encodes behavioural promises
as tests. Changing promised behaviour therefore fails conformance, which forces the diff
to touch `conformance/`, which classifies it as Interface. The loophole closes
mechanically rather than by asking people to be careful ([P2](../00-principles.md)).

## Internal change

No gate. Commit message only. Tests must pass. Refactor, rewrite, or replace the whole
implementation freely — that is the point of having a contract.

## Interface change

1. Update `contract.*` and its documented behavioural promises.
2. Update the conformance suite to match.
3. Identify consumers (the dependency manifest tells you who imports this module).
4. Update consumers, or version the interface if that is cheaper.
5. Write a decision record if an alternative was seriously considered.

Minutes, not hours. The gate exists to make you look at consumers, nothing more.

## Baseline change

See [CORE-CHG-002](baseline-change-procedure.md).

## What this buys you

Freedom inside modules is the reward for discipline at their edges. Most of your changes
will be Internal and will have no process attached at all — which is only safe because
the boundary is enforced rather than intended.
