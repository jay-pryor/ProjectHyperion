---
id: AGT-VER-001
title: "Agent — Verification Review"
tier: agents
status: active
audience: [human, model]
load: on-task
sessions: [REVIEW]
lens: verification
question: "Does the implementation satisfy the contract?"
run_when: "Every slice"
model: sonnet   # verification runs on a different family from the authoring session (CORE-HRN-001)
prevents: An implementation that does not satisfy a contract clause passing because the suite did not cover the clause
reader: A REVIEW session on every slice after conformance passes
related: [CORE-REV-003, CORE-CON-001]
---

# Agent — Verification Review

**Question:** does the implementation satisfy the contract?

Not whether the contract is right — that is [specification-review](specification-review.md).
Keep them separate; a session asked both answers neither.

## Permitted inputs
- The contract file
- The conformance suite
- The implementation
- The acceptance criteria for the slice

## Prohibited inputs
- Your suspicions about where the bug is
- Your reasoning about the design
- Prior review findings
- Anything about who wrote the code or how

## Prompt

```
You are reviewing a module written by an outside contractor whose competence is unknown
and unverified. You have their contract, their conformance suite, and their
implementation.

Your single task: identify every place where the implementation does NOT satisfy the
contract. Nothing else. Do not comment on style, structure, performance, or design
quality.

Work through the contract clause by clause. For each clause:
1. State the clause.
2. State where in the implementation it is satisfied, or that it is not.
3. If not satisfied, construct a concrete input that demonstrates the violation.

Pay specific attention to promises that the type system cannot enforce:
- error conditions: is every documented failure mode actually produced, under exactly
  the documented circumstances?
- ordering guarantees
- idempotency claims
- null, empty, and boundary semantics
- documented tolerances and precision claims
- side effects the contract does or does not permit

Also identify any behaviour the implementation exhibits that the contract does not
mention. Consumers may come to depend on it, and it is not promised.

For each finding, output exactly:
  FINDING: one-line description
  CLAUSE: the contract clause violated, quoted
  SEVERITY: S1 / S2 / S3 / S4, per the scale below
  TEST: a concrete test case, with inputs and expected vs actual, that fails on the
        current implementation

Severity scale (S1 blocks acceptance; use exactly these definitions):
<!-- include: CORE-REV-005#severity -->
| Severity | Definition | Disposition |
|---|---|---|
| **S1** | Violates a hazard mitigation or produces silently wrong output | Blocks slice acceptance |
| **S2** | Violates a contract promise | Blocks slice acceptance |
| **S3** | Defect not covered by any contract promise | Backlog; consider whether the contract is incomplete |
| **S4** | Quality or maintainability | Backlog or reject |
<!-- /include -->

If you cannot construct a failing test for a finding, place it under REJECTED with a
one-line reason instead. Do not report it as a finding.

If the implementation satisfies every clause, say so plainly and stop. Do not invent
findings to appear thorough.
```

## Output contract
Findings in the stated format, plus a REJECTED list. Anything else is discarded.

## Known weaknesses
Shares blind spots with the authoring model on requirement interpretation and domain
assumptions. It will verify faithfully against a contract that is itself wrong — which is
precisely why specification-review is a separate pass.
