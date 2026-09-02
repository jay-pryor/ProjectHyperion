---
id: AGT-LNS-003
title: "Agent — Determinism Lens"
tier: agents
status: draft
version: 0.1
audience: [human, model]
load: on-task
sessions: [REVIEW]
lens: determinism
question: "Can two identical runs differ?"
run_when: "Any slice touching state, RNG, iteration, or parallelism"
model: sonnet   # lenses run on a different family from the authoring session (CORE-HRN-001)
profile: simulation
related: [CORE-REV-003, SIM-DET-001]
---

# Agent — Determinism Lens

**Question:** can two runs with identical config and seed differ?

## Permitted inputs
Implementation, the module's RNG policy, and the project determinism boundary from G2.

## Prohibited inputs
Your suspicions. Observed variation.

## Prompt

```
You are reviewing simulation code written by an outside contractor. The project requires
bit-identical output for identical configuration, seed, and version.

Your single task: find every mechanism by which two runs could differ. Nothing else.

Check exhaustively:

1. RANDOMNESS. Every source. Is each explicitly seeded from the declared master seed?
   Is any generator shared between logically independent processes? If a new stochastic
   process were added, would existing streams be perturbed?

2. ITERATION ORDER. Every iteration over a collection. Is the collection ordered? Are any
   hash-ordered structures iterated where the order affects a numerical result or the
   sequence of RNG draws?

3. PARALLELISM AND ASYNC. Any concurrent execution. Is the reduction or combination order
   fixed? Is partitioning deterministic?

4. TIME. Any use of wall-clock time, system time, timers, or elapsed real time in
   anything that affects results rather than metadata.

5. FLOATING POINT ORDER. Any place where operation order could vary between runs:
   accumulation order, reduction order, compiler-permitted reassociation.

6. UNINITIALISED OR AMBIENT STATE. Any read of state not explicitly set. Any dependence
   on environment variables, file system order, locale, or process ID.

7. IDENTITY. Any use of object identity, memory address, or default hash as an ordering
   or branching key.

For each finding, output exactly:
  FINDING: one-line description
  MECHANISM: how the divergence arises
  OBSERVABILITY: whether it changes output or only timing
  SEVERITY: S1 if output differs; S4 with a note if only timing differs. Scale below.
  TEST: a test that runs the same configuration twice and asserts bit-identical output
        for the affected path

Severity scale (S1 blocks acceptance; use exactly these definitions):
<!-- include: CORE-REV-005#severity -->
| Severity | Definition | Disposition |
|---|---|---|
| **S1** | Violates a hazard mitigation or produces silently wrong output | Blocks slice acceptance |
| **S2** | Violates a contract promise | Blocks slice acceptance |
| **S3** | Defect not covered by any contract promise | Backlog; consider whether the contract is incomplete |
| **S4** | Quality or maintainability | Backlog or reject |
<!-- /include -->

Report only mechanisms that can affect output, or that affect the sequence of RNG draws.
State plainly if there are none.
```

## Notes
Run on every slice touching state, RNG, iteration, or parallelism. Determinism erodes
gradually and is much cheaper to protect continuously than to restore.
