---
id: SIM-DET-001
title: Determinism
tier: profile
status: draft
version: 0.1
audience: [human, model]
load: always
related: [SIM-000, SIM-VAL-001, CORE-CHG-001, CORE-SES-001]
---

# Determinism — Simulation

> **Without determinism you cannot distinguish a bug from noise, and you lose the ability
> to test at all.**

Determinism is a contract-level requirement in this profile, not a quality attribute.

## The requirement

Same config, same seed, same engine version → **bit-identical output**.

Not statistically similar. Identical. Anything weaker means a regression diff cannot
distinguish a real change from run-to-run variation, and every comparison becomes a
judgement call.

## What breaks it

| Cause | Control |
|---|---|
| Unseeded or globally-seeded RNG | Explicit RNG instances, seeded per stream |
| Iteration over unordered collections | Ordered collections at every point affecting numerics |
| Parallelism with non-deterministic reduction order | Deterministic reduction, or fixed partitioning |
| Wall-clock or system time in logic | Simulation time only; wall clock is output metadata |
| Floating-point associativity under reordering | Fixed operation order; no fast-math |
| Hash-order dependence | Ordered maps, or explicit sort before use |
| Uninitialised memory | Explicit initialisation of all state |

## RNG policy

Declared at G2 as baseline.

- **One RNG stream per stochastic process**, never a shared global. A shared generator
  means adding a stochastic feature changes the numbers everywhere else, which destroys
  regression comparison.
- Seeds derived from a single master seed by a documented, stable scheme.
- Master seed recorded in output provenance.
- Adding a new stochastic process must not perturb existing streams. Test this
  explicitly — it is easy to get wrong and silently invalidates every prior result.

## Determinism boundary

Some things cannot be deterministic — external data feeds, hardware in the loop, wall
time. Draw the boundary explicitly at G2 and state which modules sit outside it.

Modules outside the boundary must be **substitutable with a deterministic replay
implementation** at their contract, so the rest of the system remains testable. This is a
direct payoff from the contract discipline in the core.

## Regression fixtures

Determinism makes recorded scenarios into regression fixtures. A refactor either produces
identical output or it does not, and you know instantly.

```
fixtures/
  <scenario>/
    config.yaml
    seed
    expected/          # committed reference output
    tolerance.yaml     # exact by default; documented exceptions only
```

Exact-match by default. Any tolerance is a documented exception with a stated reason,
because tolerances are where determinism quietly erodes.

## Change tier and ownership of the regression net

Rows this profile contributes to the tier table ([CORE-CHG-001](../../core/change-control/change-tiers.md)),
rendered from `fragment.yaml`:

<!-- generated:tier-rows -->
| Path touched | Tier |
|---|---|
| `fixtures/**/expected/**` | Interface |
| `**/tolerance.yaml` | Interface |
| `validation/**` | Interface |
<!-- /generated -->

Ownership follows the session data ([CORE-SES-001](../../core/session-protocol.md)):
CONFORMANCE owns tolerances and validation cases, INTEGRATE owns recorded expected
output, IMPLEMENT touches none of them. A commit touching `expected/` or a tolerance file
carries a `Fixture-change: DEC-nnn | FND-nnn` trailer that resolves; the commit checker
rejects one without it (mechanically checked). Every such diff is a targeted human read
([SIM-RDS-001](targeted-reads.md)).

## Cross-platform

`OPEN:` Decide whether bit-identical output is required across platforms, or only within
one. Cross-platform bit-identity constrains the numerical stack significantly and should
be a conscious decision recorded at G2, not discovered later.
