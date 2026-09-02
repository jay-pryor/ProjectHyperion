---
id: TPL-006
title: "Template — Project CLAUDE.md"
tier: templates
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-SES-001, CORE-CHG-001]
---

# Template — Project CLAUDE.md

Copy to the project repository root as `CLAUDE.md`. Replace every `<...>`. Keep it under
160 lines; every line costs budget in every session. Blocks between `generated` markers
are rendered from the `session-types` block in CORE-SES-001; until the generator exists,
keep them identical to it by hand. Project state is never written here (records in `trace/`).

---

```markdown
# <PROJECT> — Operating Instructions

This project is built under Hyperion. Framework docs are in `hyperion/`.
Follow this file over your defaults. Where they conflict, this file wins.
Project state lives in `trace/`; never restate it here.

## Open the session with a declaration

Before reading or writing anything, output exactly:

    SESSION: <GATE | CONTRACT | CONFORMANCE | IMPLEMENT | REVIEW | INTEGRATE | LESSON | BASELINE | QUERY>
    SLICE: <SL-nn or n/a>
    SCOPE: <the one thing this session will produce>
    MAY MODIFY: <explicit file globs from the session table>
    LOADED: <doc IDs read>

Then stop and wait for confirmation. Do not begin work in the same turn. REVIEW and QUERY
have nothing to scope and do not wait. A BASELINE declaration cites its decision record.
If the task does not fit one session type, say so and propose a split; never span two.

## Session rules

A write is permitted only if its path matches "May modify" and nothing in "Must not modify".

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

Full definition: `hyperion/core/session-protocol.md` (CORE-SES-001).

## Imperatives

Each carries the core document it derives from. Follow the imperative; open the pointer
only when a marginal case needs the reasoning behind it.

An imperative with no source ID is a rule invented here rather than derived, which is a
defect — find its principle in core or delete it (CORE-IMP-001).

| # | Imperative | Source |
|---|---|---|
| IMP-01 | Import only from `modules/<name>/contract.*`. Never reach into another module's internals. | CORE-CON-003 |
| IMP-02 | Never make a failing conformance test pass by changing the test. Read the contract and decide which is wrong. | CORE-CON-002 |
| IMP-03 | Never resolve an ambiguity silently. Stop and state both readings. | CORE-PRN-001 |
| IMP-04 | Never loosen a tolerance, skip a test, or mark one expected-to-fail to get a green run. | CORE-REV-005 |
| IMP-05 | Put units and reference frames in type names, not comments. | CORE-CON-001 |
| IMP-06 | Do not add a dependency without an explicit instruction. | CORE-CHG-002 |
| IMP-07 | Declare session type, scope, and permitted files before touching anything. | CORE-SES-001 |
| IMP-08 | Stop if the slice cannot be built within existing contracts. | CORE-CHG-001 |
| IMP-09 | Outside a BASELINE session, stop if a change would touch `baseline/`. | CORE-CHG-002 |
| IMP-10 | Seed RNG per stochastic stream; iterate in order; no wall-clock time in logic. *(Simulation)* | SIM-DET-001 |
| IMP-11 | Never silently extrapolate outside a stated validity envelope. Detect and report. *(Simulation)* | SIM-VAL-001 |
| IMP-12 | Give every hard-coded tolerance a stated justification naming its basis. *(Simulation)* | SIM-RDS-001 |
| IMP-13 | Update `trace/` in the same session that changes the thing being traced. Never batch trace updates. | CORE-TRC-001 |
| IMP-14 | Never set `mitigation_status: verified` without a named test that exists and passes. | CORE-TRC-001 |

Two more that are conventions rather than derived rules, and are marked as such:

- Do not create files I did not ask for. No README, no example, no summary document.
- When uncertain, say so in one line and take the conservative option. Do not write
  paragraphs of caveats, and do not silently take the ambitious one.

## Keeping this file honest

If you change something in `hyperion/core/` that an imperative above derives from, you
have not finished until you have checked that imperative and updated it or confirmed it
still holds. Run `python hyperion/tooling/check_imperatives.py`; clear it with `--accept`
only after re-reading the source. See CORE-IMP-001.

## STOP conditions

Stop, state the condition, and end the session. Do not work around, and do not ask
permission to work around.

- The slice cannot be built within existing contracts.
- You need something a contract does not expose.
- A change would touch `baseline/` and this is not a BASELINE session.
- An acceptance criterion is ambiguous or unfalsifiable.
- A conformance test appears to contradict its contract.
- A change would perturb existing RNG streams or existing persisted data.
- You have made more than <5> edits without a passing test run.
- You are about to write a second implementation of something that already exists.

Each of these is a gate in disguise. Hitting one is a normal outcome, not a failure.

## Context loadout

Load only what the session type needs, plus this file, `hyperion/core/00-principles.md`,
`hyperion/core/change-control/change-tiers.md`, and `hyperion/core/contracts/boundary-enforcement.md`.
Do not load the whole framework; if you need a document not listed, say which and why first.

<!-- generated:loadout -->
| Session | Load |
|---|---|
| GATE | `hyperion/core/lifecycle/g<n>-*.md` |
| CONTRACT | CORE-CON-001, CORE-CON-002, TPL-001 |
| CONFORMANCE | CORE-CON-002, CORE-TST-001, `modules/<module>/CONTRACT.md`, `docs/slices/<slice>.md` |
| IMPLEMENT | `modules/<module>/CONTRACT.md`, `modules/<module>/CLAUDE.md`, `docs/slices/<slice>.md` |
| REVIEW | `hyperion/agents/<lens>.md`, plus the inputs that file permits, nothing else |
| INTEGRATE | `modules/*/CONTRACT.md`, `docs/slices/<slice>.md` |
| LESSON | CORE-LSN-001, TPL-003 |
| BASELINE | CORE-CHG-002, CORE-LFC-004, `docs/decisions/<DEC-nnn>.md` |
| QUERY | whatever the question needs; the only type with no ceiling |
<!-- /generated -->

## Commands

    <test>              # full suite; writes trace/results.xml, which check-traces reads
    <conformance>       # conformance only
    <validation>        # validation suite — separate from tests
    <lint>              # includes boundary and token checks
    <check-traces>      # python hyperion/tooling/check_traces.py — run AFTER <test>
    <trace-matrix>      # python hyperion/tooling/check_traces.py --report > trace/matrix.md
    <registry>          # python hyperion/tooling/build_registry.py --check

Run `<lint>`, `<conformance>`, and `<check-traces>` before declaring any work complete.
`trace/results.xml` is generated by the runner and never committed or hand-edited.

## Definition of done for a slice

- [ ] Conformance passes for every contract touched
- [ ] Validation suite passes, or deviations are recorded with justification
- [ ] Lenses run: <list from the slice definition>
- [ ] Findings dispositioned; S1 and S2 closed
- [ ] Lessons recorded and promoted
- [ ] Decision records written for anything decided
- [ ] `trace/` updated; `check_traces.py` green
- [ ] Slice acceptance record completed
```
