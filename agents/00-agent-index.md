---
id: AGT-000
title: Agent Index
tier: agents
status: active
audience: [human, model]
load: on-task
sessions: [REVIEW]
prevents: A lens run with the wrong inputs, on the wrong slice, or with a primed prompt because no one place lists the lenses and their rules
reader: The human choosing lenses for a slice, and the REVIEW session or /review skill selecting an agent
related: [CORE-REV-003, CORE-HRN-001]
---

# Agent Index

Ready-to-use prompts for machine reviews. One file per review type, one lens per session.

## Usage rules

Governed by [CORE-REV-003](../core/reviews/lens-reviews.md). Summarised:

1. Fresh session, no history.
2. Paste **only** the permitted inputs. Never your suspicion or your reasoning.
3. One agent per session.
4. Findings without a reproducing test go to the rejected list.

Tables are rendered by `build_layer.py` from each agent file's frontmatter (`lens`,
`question`, `run_when`, `model`, `profile`); edit the agent file, not the table. The same
files render the read-only subagents `/review` runs ([CORE-HRN-001](../core/harness.md)).

<!-- generated:agent-index -->
## Core agents

| Agent | Question | Run when | Model |
|---|---|---|---|
| [lens-partial-failure](lens-partial-failure.md) | Can state be left inconsistent mid-operation? | Slices with multi-step operations or external systems | sonnet |
| [specification-review](specification-review.md) | Is the contract itself wrong? | Every slice, and on gate artifacts at G2 and G3 | opus |
| [verification-review](verification-review.md) | Does the implementation satisfy the contract? | Every slice | sonnet |

## Simulation profile agents

| Agent | Question | Run when | Model |
|---|---|---|---|
| [lens-determinism](lens-determinism.md) | Can two identical runs differ? | Any slice touching state, RNG, iteration, or parallelism | sonnet |
| [lens-numerical-integrity](lens-numerical-integrity.md) | Are the numbers wrong in ways that still look plausible? | Any slice touching the numerical core | sonnet |

## Not yet written

Named in the selection block of CORE-REV-003 with no agent file: boundary-input, error-paths, migration, resource-exhaustion. Write one when a slice first needs it, not in advance.
<!-- /generated -->

## Anatomy of an agent file

Each file has: purpose, permitted inputs, prohibited inputs, the prompt (verbatim, ready
to paste), the output contract, and notes on known weaknesses of that lens.

The **prohibited inputs** section is not decoration. A primed model finds what you told it
to find and presents it as independent discovery, which manufactures false confidence and
is worse than running no review at all.
