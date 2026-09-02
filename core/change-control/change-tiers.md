---
id: CORE-CHG-001
title: Change Tiers
tier: core
status: active
audience: [human, model]
load: always
prevents: A behavioural interface change passing as an internal one, or a tier argued rather than classified by path
reader: Every session, standing, when a change touches a contract, a suite, or baseline/
related: [CORE-PRN-001, CORE-CON-001, CORE-CHG-002, CORE-SES-001]
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

Profiles contribute rows; the simulation profile adds fixture and validation paths
([SIM-DET-001](../../profiles/simulation/determinism.md)). If a diff spans tiers, the
highest tier applies to the whole change.

Classification applies only after G3 is recorded as passed in `trace/reviews.yaml`
(CORE-TRC-002). Before that row exists, contracts and their initial suites are gate work
([CORE-LFC-005](../lifecycle/g3-contracts.md)), not Interface changes.

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

A fixed sequence of three sessions ([CORE-SES-001](../session-protocol.md)), never one,
because no single session may touch contract, suite, and implementation together:

1. **CONTRACT** — increment the contract version, revise the acceptance criteria the
   change affects in the slice definition, and write a decision record if an alternative
   was seriously considered.
2. **CONFORMANCE** — bring the suite to the revised criteria. Written from the criteria,
   never from the diff ([P8](../00-principles.md)).
3. **IMPLEMENT** — the provider, then each consumer the dependency manifest names, one
   commit per module. Version the interface instead where two consumers cannot migrate
   together ([CORE-CON-001](../contracts/contract-definition.md)).

The gate is light because the sequence is short, not because it is one session. A diff
to `contract.*` must change the contract's version line; the commit checker rejects one
that does not (mechanically checked).

## Baseline change

See [CORE-CHG-002](baseline-change-procedure.md).

## What this buys you

Freedom inside modules is the reward for discipline at their edges. Most of your changes
will be Internal and will have no process attached at all — which is only safe because
the boundary is enforced rather than intended.
