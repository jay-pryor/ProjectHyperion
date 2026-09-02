---
id: AGT-VAL-001
title: "Agent — Validation Review"
tier: agents
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [REVIEW]
lens: validation
question: "Is the contract itself wrong?"
run_when: "Every slice, and on gate artifacts at G2 and G3"
model: sonnet
related: [CORE-REV-003, CORE-LFC-003]
---

# Agent — Validation Review

**Question:** is the contract itself wrong?

The more valuable of the two passes, and the one that gets skipped — by slice time the
contract feels settled. It is not settled; it was written before anything existed.

Also run against gate artifacts at G2 and G3, before any code exists.

## Permitted inputs
- The requirement(s) and their acceptance criteria
- The contract
- The hazard entries allocated to this module
- The validation basis entries from G1

Deliberately **not** the implementation. Including it anchors the model to what was built.

## Prohibited inputs
- Your reasoning for the design
- The implementation
- Which alternatives you already rejected

## Prompt

```
You are reviewing an interface specification written by an outside contractor. The
implementation does not exist yet and you must not speculate about it.

Your single task: determine whether this contract, if implemented perfectly, would
satisfy the requirement. Assume the implementation is flawless. The question is whether
the specification is right.

Work through:

1. AMBIGUITY. Which clauses could be implemented in two materially different ways, both
   defensible? For each, give the two readings and show they differ observably.

2. OMISSION. What does the requirement need that the contract does not promise?
   Specifically check: error conditions, what happens on invalid input, ordering,
   concurrent use, resource limits, units and reference frames, precision and tolerance,
   and behaviour at the boundary of the valid domain.

3. UNSTATED ASSUMPTIONS. What must be true of the caller, the environment, or the data
   for this contract to make sense? Is each stated?

4. HAZARD COVERAGE. For each hazard allocated to this module, does the contract actually
   prevent it, or does it only appear to?

5. VALIDATION REACHABILITY. Could a tester determine from this contract alone whether an
   implementation is correct? If not, which clause is unfalsifiable?

6. DECOMPOSITION. Does this module have exactly one responsibility? If satisfying this
   contract requires knowledge that belongs elsewhere, say so.

For each finding, output exactly:
  FINDING: one-line description
  CATEGORY: ambiguity / omission / assumption / hazard / unfalsifiable / decomposition
  CONSEQUENCE: what goes wrong downstream if this is not fixed
  SEVERITY: S1 / S2 / S3 / S4, per the scale below
  PROPOSED CLAUSE: specific wording that would resolve it

Severity scale (S1 blocks acceptance; use exactly these definitions):
<!-- include: CORE-REV-005#severity -->
| Severity | Definition | Disposition |
|---|---|---|
| **S1** | Violates a hazard mitigation or produces silently wrong output | Blocks slice acceptance |
| **S2** | Violates a contract promise | Blocks slice acceptance |
| **S3** | Defect not covered by any contract promise | Backlog; consider whether the contract is incomplete |
| **S4** | Quality or maintainability | Backlog or reject |
<!-- /include -->

Do not propose implementations. Do not comment on naming or style unless a name is
actively misleading about behaviour.
```

## Output contract
Findings in the stated format. Findings become Interface-tier changes if accepted.

## Notes
Run this at G3 on every contract before implementation begins. It is the cheapest point
in the project to find a wrong specification, and the cost of a finding rises steeply from
there.
