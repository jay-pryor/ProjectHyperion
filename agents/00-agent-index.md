---
id: AGT-000
title: Agent Index
tier: agents
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-REV-003]
---

# Agent Index

Ready-to-use prompts for machine reviews. One file per review type, one lens per session.

## Usage rules

Governed by [CORE-REV-003](../core/reviews/lens-reviews.md). Summarised:

1. Fresh session, no history.
2. Paste **only** the permitted inputs. Never your suspicion or your reasoning.
3. One agent per session.
4. Findings without a reproducing test go to the rejected list.

## Core agents

| Agent | Question | Run when |
|---|---|---|
| [verification-review](verification-review.md) | Does the implementation satisfy the contract? | Every slice |
| [validation-review](validation-review.md) | Is the contract itself wrong? | Every slice, and on gate artifacts |
| [lens-partial-failure](lens-partial-failure.md) | Can state be left inconsistent mid-operation? | Slices with multi-step operations or external systems |

## Simulation profile agents

| Agent | Question | Run when |
|---|---|---|
| [lens-numerical-integrity](lens-numerical-integrity.md) | Are the numbers wrong in ways that still look plausible? | Any slice touching the numerical core |
| [lens-determinism](lens-determinism.md) | Can two identical runs differ? | Any slice touching state, RNG, iteration, or parallelism |

## To write

Error paths · Boundary and input · Resource exhaustion · Concurrency · Contract drift ·
Migration safety. Write these when a slice first needs them, not in advance.

## Anatomy of an agent file

Each file has: purpose, permitted inputs, prohibited inputs, the prompt (verbatim, ready
to paste), the output contract, and notes on known weaknesses of that lens.

The **prohibited inputs** section is not decoration. A primed model finds what you told it
to find and presents it as independent discovery, which manufactures false confidence and
is worse than running no review at all.
