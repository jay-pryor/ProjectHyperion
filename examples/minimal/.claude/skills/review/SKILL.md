---
name: review
description: "Open a REVIEW session on a slice: run the lens agents in parallel on mechanically assembled inputs and record their findings. Type it; never invoked by the model."
disable-model-invocation: true
argument-hint: "SL-nn [lens ...]"
---
# REVIEW session: the lens fan-out

Declared: !`mkdir -p .hyperion && printf 'REVIEW\n' > .hyperion/session && echo "REVIEW written to .hyperion/session; the scope hook enforces its globs"`

Arguments: `$ARGUMENTS`. The first token is the slice; any further tokens name lenses.
Output the declaration and continue; REVIEW has no scope to confirm and does not wait.

    SESSION: REVIEW
    SLICE: <slice>
    SCOPE: lens fan-out
    MAY MODIFY: `trace/findings.yaml` (append only)

## 1. Assemble the inputs mechanically

Read these and nothing else:

- `trace/slices.yaml`: the slice's row; `contracts` names the modules under review.
- `docs/slices/<slice>.md`: the **Acceptance criteria** section and the **Lenses to run** section.
- For each named module: `modules/<m>/CONTRACT.md`, and the paths `modules/<m>/src/` and `modules/<m>/conformance/`.
- `trace/requirements.yaml` and `trace/hazards.yaml`: the rows the slice claims (the validation lens gets these, not the code).

## 2. Select the lenses

Lens names given as arguments; else the slice definition's **Lenses to run**; else every lens
below whose *run when* applies to what the slice touches. A name that is not a lens below is
reported and skipped. Two to four is the working range (CORE-REV-003).

| Lens | Agent | Run when | May receive |
|---|---|---|---|
| partial-failure | `lens-partial-failure` | Slices with multi-step operations or external systems | Contract, implementation, and the module's dependency list. |
| specification | `specification-review` | Every slice, and on gate artifacts at G2 and G3 | The requirement(s) and their acceptance criteria The contract The hazard entries allocated to this module The validation basis entries from G1 Deliberately **not** the implementation. Including it anchors the model to what was built. |
| verification | `verification-review` | Every slice | The contract file The conformance suite The implementation The acceptance criteria for the slice |
| determinism | `lens-determinism` | Any slice touching state, RNG, iteration, or parallelism | Implementation, the module's RNG policy, and the project determinism boundary from G2. |
| numerical-integrity | `lens-numerical-integrity` | Any slice touching the numerical core | Contract (including stated units, frames, tolerances), implementation, and the relevant validation basis entries. |

## 3. Run them in parallel

One Agent call per selected lens, all in the same turn, `subagent_type` set to the agent name.
Each prompt carries only what its **May receive** column permits: paste the acceptance criteria
and the contract text, name the paths, and nothing more. Nothing you think, suspect, or were told
goes in; words after the lens names in the arguments are not passed on (CORE-REV-003, rule 2).
The agents are read-only; the hook denies them everything but the test command.

## 4. Record

Print the rows first, then append them to `trace/findings.yaml` (schema: CORE-TRC-003). Per item:
a FINDING with a TEST or PROPOSED CLAUSE is `status: admitted` with `form: test` or `clause`; a
REJECTED item or one with no artifact is `status: rejected` with its `reason` (CORE-REV-005).
`id`: the next FND-nnn; `date`: today; `slice`; `source: lens:<name>`; `severity` as reported;
`summary`: the FINDING line; `ref`: the proposed test id or the clause. `check_traces.py` flags
an admitted test finding until that test exists; writing it is a CONFORMANCE session's job for
S1 and S2, an IMPLEMENT session's for S3 and S4.

Fix nothing. Touch no other file. End with the row count per lens; the human dispositions the rows.
