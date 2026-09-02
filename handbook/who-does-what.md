---
id: HBK-002
title: Who Does What
tier: handbook
status: active
version: 0.1
audience: [human]
load: never
sessions: []
related: [HBK-000, CORE-PRN-001, CORE-SES-001, CORE-LFC-006, CORE-REV-001, CORE-CHG-001]
---

# Who Does What

P10 says the human owns the problem and the model owns the solution, but a principle
does not tell a person at a keyboard whether the next step is theirs. Under time
pressure the line moves toward whoever is faster, which is the model, and the framework's
main failure follows. This is the line drawn across the whole lifecycle, with the check
that holds each step in place. Read by the human running a project; the checks column
is what makes the other two enforceable ([P2](../core/00-principles.md)).

| Phase | Human | Model session | Check |
|---|---|---|---|
| G0 | Works the five questions per function; writes never-statements; assesses severity | none | Hazard records resolve; failure mode is one of the five questions |
| G1 | Writes atomic requirements; names a validation class for each; records needs and assumptions | Specification review of the requirement set (fresh context) | Every requirement has method, class, source |
| G2 | Decomposes by what changes together; names the baseline; writes decision records with rejected alternatives | Drafts manifests and the module map from the human's decomposition | No cycles; every requirement allocated; diagram generated from manifests |
| G3 | Writes acceptance criteria per slice; reads every contract; orders slices by risk | CONTRACT sessions draft contracts; CONFORMANCE sessions write suites from the criteria | Suites fail on empty implementation; null double fails; gate row written |
| Select slice | Picks the next slice; confirms contracts unchanged | none | Slice claims only existing requirements and hazards |
| Implement | Does not read the code | IMPLEMENT session builds to contract; stops on any STOP condition | Scope hook denies writes outside `src/` and `tests/`; commit checker rejects paths outside the declared type |
| Verify | Reads the conformance suite once | none | Conformance passes; mutation survivors triaged |
| Review | Chooses two to four lenses; pastes only permitted inputs | One REVIEW session per lens, read-only, appends findings | Findings carry a test or a clause (`form`); else rejected with a reason |
| Read and validate | Targeted reads from the profile list; ten minutes of use; checks output against the validation basis | CONFORMANCE session writes the validation case the human specified | Validation results present and passed in `results.xml` |
| Accept | Writes the acceptance record; decides disposition of S3 and S4 | LESSON session promotes each finding to a check | Chain intact; accepted slice claims only verified requirements |
| Change | Declares the tier; writes the decision record for Baseline | CONTRACT then CONFORMANCE then IMPLEMENT, or BASELINE | Contract version bumped; change logged with its driver |
| G4 | Reads the console; signs the gate row | none | Every gate row passed, every claim verified, no open S1 or S2 |

The pattern to notice: the human's column is short at every step and never says "read
the implementation". The check column is never empty. Where the model column is empty,
it is because the work is judgement the framework refuses to delegate.

## Where each column is defined

- Human steps: the gate documents [CORE-LFC-002](../core/lifecycle/g0-hazard-context.md)
  to [CORE-LFC-005](../core/lifecycle/g3-contracts.md), the loop
  [CORE-LFC-006](../core/lifecycle/slice-loop.md), and
  [CORE-REV-004](../core/reviews/targeted-human-reads.md).
- Model sessions: the session-types block of [CORE-SES-001](../core/session-protocol.md),
  which is also what the scope hook and the commit checker read.
- Checks: `check_traces.py` ([CORE-TRC-001](../core/traceability/traceability.md)),
  `check_commit.py`, `check_null_doubles.py` and `mutation_score.py`
  ([CORE-TST-002](../core/testing/tests-are-tested.md)), and the boundary lint
  ([CORE-CON-003](../core/contracts/boundary-enforcement.md)).
