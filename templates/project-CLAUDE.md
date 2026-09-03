---
id: TPL-006
title: "Template — Project CLAUDE.md"
tier: templates
status: active
audience: [human, model]
load: on-task
sessions: [FRAMEWORK]
prevents: A project operating layer that restates core in its own words and drifts from it
reader: FRAMEWORK sessions changing the template; init_project.py instantiates it for every project
related: [CORE-SES-001, CORE-CHG-001, CORE-IMP-001]
---

# Template — Project CLAUDE.md

Instantiated by `init_project.py`, which fills every `generated` block for the chosen
profiles (this file shows the core-only rendering); `--upgrade` re-renders them and touches
nothing else. Replace every `<...>` by hand, keep it under 160 lines, write no state here.

---

```markdown
# <PROJECT> — Operating Instructions

Built under Hyperion; framework docs are in `hyperion/`. Follow this file over your
defaults; where they conflict, this file wins. Project state lives in `trace/`, never here.

## Open the session with a declaration

Type the session's skill (`/implement SL-02 <scope>`); it prints the declaration below and
records the type for the scope hook (CORE-HRN-001). Without it, output by hand, before anything else:

    SESSION: <GATE | CONTRACT | CONFORMANCE | IMPLEMENT | REVIEW | INTEGRATE | LESSON | BASELINE | QUERY>
    SLICE: <SL-nn or n/a>
    SCOPE: <the one thing this session will produce>
    MAY MODIFY: <explicit file globs from the session table>
    LOADED: <doc IDs read>

Then stop and wait for confirmation. Do not begin work in the same turn. REVIEW and QUERY
do not wait. A BASELINE declaration cites its decision record. If the task does not fit
one session type, say so and propose a split; never span two.

## Session rules

A write is permitted only if its path matches "May modify" and nothing in "Must not
modify". Full definition: `hyperion/core/session-protocol.md` (CORE-SES-001).

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

Each carries the core section it derives from; open the pointer only when a marginal case
needs the reasoning. An imperative with no source is invented here, not derived: a defect.
Never edit the table by hand; `check_imperatives.py` fails when a source section changed or the
table and `.hyperion/imperatives.json` disagree, and an `--upgrade` needs a re-read (CORE-IMP-001).

<!-- generated:imperatives -->
| # | Imperative | Source |
|---|---|---|
| IMP-01 | Import only from `modules/<name>/contract.*`; its conformance suite is importable from test code alone. | CORE-CON-003#the-rule |
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
<!-- /generated -->

Two conventions rather than derived rules, marked as such:

- Do not create files I did not ask for. No README, no example, no summary document.
- When uncertain, say so in one line and take the conservative option; no paragraphs of
  caveats, and never the ambitious option silently.

## STOP conditions

Stop, state the condition, and end the session. Do not work around it or ask permission to.

<!-- generated:stop-conditions -->
- The slice cannot be built within existing contracts.
- You need something a contract does not expose.
- A change would touch `baseline/` and this is not a BASELINE session.
- An acceptance criterion is ambiguous or unfalsifiable.
- A conformance test appears to contradict its contract.
- A change would alter the shape of existing persisted data.
- You have made more than five edits without a passing test run.
- You are about to write a second implementation of something that already exists.
<!-- /generated -->

## Context loadout

Load only what the session needs, plus this file; `loadout.py` lists the paths. Need more? Say why first.

<!-- generated:loadout -->
| Session | Load |
|---|---|
| every session | CORE-CHG-001, CORE-CON-003, CORE-LFC-001, CORE-LFC-006, CORE-PRN-001, CORE-SES-001 |
| GATE | CORE-DEC-001, CORE-HRN-001, CORE-LFC-002, CORE-LFC-003, CORE-LFC-004, CORE-LFC-005, CORE-REV-003, CORE-TRC-001, CORE-TRC-002, TPL-002, TPL-004, TPL-005, TPL-008, `docs/decisions/**`, `trace/**` |
| CONTRACT | CORE-CON-001, CORE-CON-002, CORE-DEC-001, CORE-HRN-001, CORE-TRC-002, TPL-001, TPL-002, TPL-005, `modules/<module>/CONTRACT.md`, `docs/slices/<slice>.md` |
| CONFORMANCE | CORE-CON-002, CORE-HRN-001, CORE-REV-005, CORE-TRC-002, CORE-TST-001, CORE-TST-002, `modules/<module>/CONTRACT.md`, `docs/slices/<slice>.md` |
| IMPLEMENT | CORE-HRN-001, CORE-TST-002, `modules/<module>/CONTRACT.md`, `modules/<module>/CLAUDE.md`, `docs/slices/<slice>.md` |
| REVIEW | CORE-HRN-001, CORE-REV-001, CORE-REV-003, CORE-REV-005, CORE-TRC-003, AGT-000, AGT-LNS-001, AGT-VAL-001, AGT-VER-001, one agent file plus the inputs it permits, nothing else |
| INTEGRATE | CORE-HRN-001, CORE-TRC-003, CORE-TST-002, `modules/*/CONTRACT.md`, `docs/slices/<slice>.md` |
| LESSON | CORE-HRN-001, CORE-LSN-001, CORE-REV-005, CORE-TRC-003, TPL-003, TPL-007, `docs/slices/<slice>.md`, `lessons/**` |
| BASELINE | CORE-CHG-002, CORE-DEC-001, CORE-HRN-001, CORE-TRC-003, TPL-002, `docs/decisions/<DEC-nnn>.md` |
| QUERY | whatever the question needs; the only type with no ceiling |
<!-- /generated -->

## Commands

    <test>              # full suite; writes trace/results.xml, which check_traces.py reads
    <conformance>       # conformance only; <validation> for the validation suite alone
    <lint>              # the language linter; boundaries and units have checks below

<!-- generated:commands-project -->
    python hyperion/tooling/check_traces.py                    # every trace/ record; --report prints the matrix
    python hyperion/tooling/build_console.py .                 # render console/index.html, the reviewer's artifact
    python hyperion/tooling/check_null_doubles.py .            # every suite must FAIL against its null double
    python hyperion/tooling/check_boundaries.py .              # the real import graph against modules/*/manifest.yaml
    python hyperion/tooling/check_units.py .                   # the type check runs clean and is proved to reject a unit confusion
    python hyperion/tooling/mutation_score.py --slice SL-nn .  # at acceptance; --write records the survivors, --check re-measures
    python hyperion/tooling/check_imperatives.py               # imperatives drifted from their source sections
    python hyperion/tooling/loadout.py --session <TYPE>        # the documents that session type loads
    python hyperion/tooling/init_project.py --upgrade .        # re-render generated blocks after a version bump
    python hyperion/tooling/check_commit.py <base>..HEAD       # paths must match the Session trailer
<!-- /generated -->

Run `<lint>`, `<conformance>`, and `check_traces.py` before declaring any work complete;
`trace/results.xml` is generated, never committed. Every commit carries a `Session: <TYPE>` trailer.

## Definition of done for a slice

- [ ] Conformance passes for every contract touched
- [ ] Validation suite passes, or deviations are recorded with justification
- [ ] Lenses run: <list from the slice definition>
- [ ] Findings dispositioned; S1 and S2 closed
<!-- generated:targeted-reads -->
- [ ] Targeted human reads done (CORE-REV-004)
<!-- /generated -->
- [ ] Lessons recorded and promoted
- [ ] Decision records written for anything decided
- [ ] `trace/` updated; `check_traces.py` green
- [ ] Slice acceptance record completed
```
