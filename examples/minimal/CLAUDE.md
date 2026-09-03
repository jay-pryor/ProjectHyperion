# minimal — Operating Instructions

Built under Hyperion (vendored at `hyperion/`, version pinned in `.hyperion/version`).
Project state lives in `trace/`; never restate it here.

## Declaration
    SESSION: <GATE | CONTRACT | CONFORMANCE | IMPLEMENT | REVIEW | INTEGRATE | LESSON | BASELINE | QUERY>
    SLICE: <SL-nn>
    SCOPE: <one thing>
    MAY MODIFY: <globs from the session table>

## Session rules
<!-- generated:session-table -->
| Type | May modify | Must not modify |
|---|---|---|
| GATE | `docs/**`, `trace/**` | `modules/**`, `baseline/**`, `validation/**` |
| CONTRACT | `modules/*/contract.*`, `modules/*/CONTRACT.md`, `docs/slices/**`, `docs/decisions/**`, `trace/**` | `modules/*/src/**`, `modules/*/conformance/**`, `modules/*/tests/**`, `baseline/**`, `validation/**` |
| CONFORMANCE | `modules/*/conformance/**`, `validation/**`, `**/tolerance.yaml`, `trace/**` | `modules/*/src/**`, `modules/*/contract.*`, `modules/*/CONTRACT.md`, `modules/*/tests/**`, `baseline/**` |
| IMPLEMENT | `modules/*/src/**`, `modules/*/tests/**`, `trace/**` | `modules/*/contract.*`, `modules/*/CONTRACT.md`, `modules/*/conformance/**`, `baseline/**`, `validation/**`, `fixtures/**` |
| REVIEW | `trace/findings.yaml` (append only) | `modules/**`, `baseline/**`, `validation/**`, `docs/**` |
| INTEGRATE | `integration/**`, `fixtures/**`, `trace/**` | `modules/*/contract.*`, `modules/*/CONTRACT.md`, `modules/*/conformance/**`, `**/tolerance.yaml`, `baseline/**`, `validation/**` |
| LESSON | `lessons/**`, `lint/**`, `modules/*/CLAUDE.md`, `docs/slices/**`, `trace/**` | `modules/*/src/**`, `modules/*/contract.*`, `modules/*/conformance/**`, `baseline/**` |
| BASELINE | `baseline/**`, `docs/decisions/**`, `trace/**` | `modules/**`, `validation/**` |
| QUERY | nothing | everything |
<!-- /generated -->

## Imperatives
<!-- generated:imperatives -->
| # | Imperative | Source |
|---|---|---|
| IMP-01 | Import only from `modules/<name>/contract.*`. Never reach into another module's internals. | CORE-CON-003#the-rule |
| IMP-02 | Never make a failing conformance test pass by changing the test. Read the contract and decide which is wrong. | CORE-SES-001#the-load-bearing-prohibitions |
| IMP-03 | Never resolve an ambiguity silently. Stop and state both readings. | CORE-SES-001#declaration-stop-and-escalate |
| IMP-05 | Put units and reference frames in type names, not comments. | CORE-CON-001#units-and-frames |
| IMP-06 | Do not add a dependency without an explicit instruction. | CORE-LFC-004#baseline-definition |
| IMP-07 | Declare session type, scope, and permitted files before touching anything. | CORE-SES-001#declaration-stop-and-escalate |
| IMP-08 | Stop if the slice cannot be built within existing contracts. | CORE-SES-001#the-load-bearing-prohibitions |
| IMP-09 | Outside a BASELINE session, stop if a change would touch `baseline/`. | CORE-CHG-002#procedure |
| IMP-13 | Update `trace/` in the same session that changes the thing being traced. Never batch trace updates. | CORE-TRC-001#discipline |
| IMP-14 | Never set `mitigation_status: verified` without a named test that exists and passes. | CORE-TRC-001#results-not-collection |
| IMP-15 | Never skip a test or mark one expected-to-fail to get a green run. | CORE-TRC-001#results-not-collection |
| IMP-04 | Never loosen a tolerance to get a green run. *(Simulation)* | SIM-VAL-001#validation-suite |
| IMP-10 | Seed RNG per stochastic stream; iterate in order; no wall-clock time in logic. *(Simulation)* | SIM-DET-001#what-breaks-it |
| IMP-11 | Never silently extrapolate outside a stated validity envelope. Detect and report. *(Simulation)* | SIM-VAL-001#validity-envelope |
| IMP-12 | Give every hard-coded tolerance a stated justification naming its basis. *(Simulation)* | CORE-CON-001#tolerances |
<!-- /generated -->

## STOP conditions
<!-- generated:stop-conditions -->
- The slice cannot be built within existing contracts.
- You need something a contract does not expose.
- A change would touch `baseline/` and this is not a BASELINE session.
- An acceptance criterion is ambiguous or unfalsifiable.
- A conformance test appears to contradict its contract.
- A change would alter the shape of existing persisted data.
- You have made more than five edits without a passing test run.
- You are about to write a second implementation of something that already exists.
- A change would perturb an existing RNG stream. *(Simulation)*
<!-- /generated -->

## Context loadout
<!-- generated:loadout -->
| Session | Load |
|---|---|
| every session | CORE-CHG-001, CORE-CON-003, CORE-LFC-001, CORE-LFC-006, CORE-PRN-001, CORE-SES-001, SIM-000, SIM-DET-001 |
| GATE | CORE-DEC-001, CORE-HRN-001, CORE-LFC-002, CORE-LFC-003, CORE-LFC-004, CORE-LFC-005, CORE-REV-003, CORE-TRC-001, CORE-TRC-002, SIM-VAL-001, TPL-002, TPL-004, TPL-005, TPL-008, `docs/decisions/**`, `trace/**` |
| CONTRACT | CORE-CON-001, CORE-CON-002, CORE-DEC-001, CORE-HRN-001, CORE-TRC-002, TPL-001, TPL-002, TPL-005, `modules/<module>/CONTRACT.md`, `docs/slices/<slice>.md` |
| CONFORMANCE | CORE-CON-002, CORE-HRN-001, CORE-REV-005, CORE-TRC-002, CORE-TST-001, CORE-TST-002, SIM-VAL-001, `modules/<module>/CONTRACT.md`, `docs/slices/<slice>.md`, `fixtures/<scenario>/tolerance.yaml` |
| IMPLEMENT | CORE-HRN-001, CORE-TST-002, `modules/<module>/CONTRACT.md`, `modules/<module>/CLAUDE.md`, `docs/slices/<slice>.md` |
| REVIEW | CORE-HRN-001, CORE-REV-001, CORE-REV-003, CORE-REV-005, CORE-TRC-003, AGT-000, AGT-LNS-001, AGT-LNS-002, AGT-LNS-003, AGT-VAL-001, AGT-VER-001, one agent file plus the inputs it permits, nothing else |
| INTEGRATE | CORE-HRN-001, CORE-TRC-003, CORE-TST-002, `modules/*/CONTRACT.md`, `docs/slices/<slice>.md`, `fixtures/<scenario>/config.yaml`, `fixtures/<scenario>/seed` |
| LESSON | CORE-HRN-001, CORE-LSN-001, CORE-REV-005, CORE-TRC-003, TPL-003, TPL-007, `docs/slices/<slice>.md`, `lessons/**` |
| BASELINE | CORE-CHG-002, CORE-DEC-001, CORE-HRN-001, CORE-TRC-003, TPL-002, `docs/decisions/<DEC-nnn>.md` |
| QUERY | whatever the question needs; the only type with no ceiling |
<!-- /generated -->

## Definition of done for a slice
- [ ] Conformance passes; validation passes; lenses run; findings dispositioned
<!-- generated:targeted-reads -->
- [ ] Targeted human reads done (SIM-RDS-001): units and reference frames at every module boundary; state initialisation; the integrator and timestep handling; boundary and envelope handling; scenario configuration parsing; anything with a tolerance in it; stochastic stream allocation; every diff to recorded expected output or a tolerance file
<!-- /generated -->
- [ ] `trace/` updated; `check_traces.py` green; acceptance record completed

## Commands
    pytest -q  # full suite, writes trace/results.xml
<!-- generated:commands-project -->
    python hyperion/tooling/check_traces.py                    # every trace/ record; --report prints the matrix
    python hyperion/tooling/build_console.py .                 # render console/index.html, the reviewer's artifact
    python hyperion/tooling/check_null_doubles.py .            # every suite must FAIL against its null double
    python hyperion/tooling/mutation_score.py --slice SL-nn .  # at acceptance; --write records the survivors
    python hyperion/tooling/check_imperatives.py               # imperatives drifted from their source sections
    python hyperion/tooling/loadout.py --session <TYPE>        # the documents that session type loads
    python hyperion/tooling/init_project.py --upgrade .        # re-render generated blocks after a version bump
    python hyperion/tooling/check_commit.py <base>..HEAD       # paths must match the Session trailer
<!-- /generated -->
