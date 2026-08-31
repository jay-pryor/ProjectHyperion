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
150 lines; it is loaded into every session and every line costs budget.

---

```markdown
# <PROJECT> — Operating Instructions

This project is built under Hyperion. Framework docs are in `hyperion/`.
Follow this file over your defaults. Where they conflict, this file wins.

## Current state

- Gate reached: <G0 | G1 | G2 | G3 | slice loop>
- Active slice: <SL-nn, or none>
- Profile(s): <Simulation | Web | ...>
- Language / stack: <...>
- Baseline version: <...>

## Open the session with a declaration

Before reading or writing anything, output exactly:

    SESSION: <GATE | CONTRACT | CONFORMANCE | IMPLEMENT | REVIEW | INTEGRATE | LESSON>
    SLICE: <SL-nn or n/a>
    SCOPE: <the one thing this session will produce>
    MAY MODIFY: <explicit file globs>
    LOADED: <doc IDs read>

Then stop and wait for confirmation. Do not begin work in the same turn.

If the task I gave you does not fit one session type, say so and propose a split. Do not
silently span two.

## Session rules

| Type | May modify | Must not modify |
|---|---|---|
| GATE | gate artifacts, decision records | any code |
| CONTRACT | `contract.*` | `src/`, `conformance/` |
| CONFORMANCE | `conformance/` | `src/`, `contract.*` |
| IMPLEMENT | `src/`, `tests/` | `contract.*`, `conformance/`, `baseline/` |
| REVIEW | nothing | everything |
| INTEGRATE | integration code, fixtures | `contract.*`, `conformance/` |
| LESSON | lessons, lint rules, conformance | `src/` |

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
| IMP-09 | Stop if a change would touch `baseline/`. | CORE-CHG-002 |
| IMP-10 | Seed RNG per stochastic stream; iterate in order; no wall-clock time in logic. *(Simulation)* | SIM-DET-001 |
| IMP-11 | Never silently extrapolate outside a stated validity envelope. Detect and report. *(Simulation)* | SIM-VAL-001 |
| IMP-12 | Give every hard-coded tolerance a stated justification naming its basis. *(Simulation)* | SIM-RDS-001 |

Two more that are conventions rather than derived rules, and are marked as such:

- Do not create files I did not ask for. No README, no example, no summary document.
- When uncertain, say so in one line and take the conservative option. Do not write
  paragraphs of caveats, and do not silently take the ambitious one.

## Keeping this file honest

> If you change something in `hyperion/core/` that an imperative above derives from, you
> have not finished until you have checked that imperative and updated it or confirmed it
> still holds. The same applies in reverse: an imperative you edit must still trace to its
> source.

Run `python hyperion/tooling/check_imperatives.py` — it fails when a source document has
changed since its imperatives were last confirmed. Clear it with `--accept` after
re-reading the source, not before. See CORE-IMP-001.

## STOP conditions

Stop, state the condition, and end the session. Do not work around, and do not ask
permission to work around.

- The slice cannot be built within existing contracts.
- You need something a contract does not expose.
- A change would touch `baseline/`.
- An acceptance criterion is ambiguous or unfalsifiable.
- A conformance test appears to contradict its contract.
- A change would perturb existing RNG streams or existing persisted data.
- You have made more than <5> edits without a passing test run.
- You are about to write a second implementation of something that already exists.

Each of these is a gate in disguise. Hitting one is a normal outcome, not a failure.

## Context loadout

Load only what the session type needs.

| Session | Load |
|---|---|
| Always | this file, `hyperion/core/00-principles.md`, `hyperion/core/change-control/change-tiers.md`, `hyperion/core/contracts/boundary-enforcement.md` |
| GATE | the relevant `hyperion/core/lifecycle/g*.md` |
| CONTRACT | CORE-CON-001, CORE-CON-002, `templates/contract.md` |
| CONFORMANCE | CORE-CON-002, CORE-TST-001, the contract, the acceptance criteria |
| IMPLEMENT | the contract, the slice definition, the module `CLAUDE.md` |
| REVIEW | one agent file from `hyperion/agents/` and nothing else |
| LESSON | CORE-LSN-001, `templates/lesson.md` |

Do not load the whole framework. If you think you need a document not listed, say which
and why before loading it.

## Commands

    <test>              # full suite
    <conformance>       # conformance only
    <validation>        # validation suite — separate from tests
    <lint>              # includes boundary and token checks
    <registry>          # python hyperion/tooling/build_registry.py --check

Run `<lint>` and `<conformance>` before declaring any work complete.

## Definition of done for a slice

- [ ] Conformance passes for every contract touched
- [ ] Validation suite passes, or deviations are recorded with justification
- [ ] Lenses run: <list from the slice definition>
- [ ] Findings dispositioned; S1 and S2 closed
- [ ] Lessons recorded and promoted
- [ ] Decision records written for anything decided
- [ ] Slice acceptance record completed
```
