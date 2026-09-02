---
id: CORE-LFC-002
title: "G0 — Hazard & Context"
tier: core
status: active
audience: [human, model]
load: on-task
sessions: [GATE]
prevents: Hazards discovered after the architecture they should have driven exists, and silent wrong output never named as a hazard
reader: The human and a GATE session working G0, and the G0 reviewer who does not read code
related: [CORE-LFC-001, CORE-LFC-003]
---

# G0 — Hazard & Context

The first gate, before requirements and before architecture. It answers: **what must
this software never do, and what happens when it fails?**

## Why this is gate zero

Hazard-driven requirements are the part of this work a model cannot do for you
([P10](../00-principles.md)). A model can write competent code all day; it cannot know
what the payload is bolted to, what is underneath it, or what else is on the RF spectrum
at the time. This gate is where systems-engineering discipline outperforms coding fluency,
and it generates requirements that all later gates inherit.

## Inputs

- Operational context: where this runs, who operates it, what it is connected to.
- The organisation's existing hazard management system. Hyperion does **not** replace it.
  Hazards are raised, assessed, and tracked in the organisational system; Hyperion holds
  the **trace** from hazard to module contract to test.
- Interfacing systems and their failure modes.

## Without an organisational hazard system

A single-operator or early project has no organisational register. It records each hazard
with `register: local` and carries the assessment itself: `severity` and `likelihood` as
integers on the scale its profile defines (for simulation, [SIM-000](../../profiles/simulation/PROFILE.md#local-hazard-scale)).
The organisational fields are then forbidden, so a record cannot half-belong to a system
it was never entered in; `register: org` reverses both rules. The record and the checks on
it are in [CORE-TRC-002](../traceability/trace-records.md#hazard). Moving a hazard from
`local` to `org` when a register appears is a record edit, not a re-assessment.

## Method

For each function the software performs, ask:

1. What if it **does not happen**?
2. What if it happens **incorrectly**?
3. What if it happens **at the wrong time** (early, late, out of order)?
4. What if it happens **when not commanded**?
5. What if it happens and **nothing indicates that it failed**? (silent failure)

Question 5 is the one most often skipped and most often the real hazard. Undetected
wrong output is worse than a crash, particularly in simulation, where a wrong answer is
indistinguishable from a right one without a validation basis.

## Outputs

| Artifact | Contents | Consumed by |
|---|---|---|
| Hazard register entry (org system, or the `local` record) | Hazard, cause, severity, likelihood, mitigation | Org safety process, or the G0 reviewer |
| Hyperion hazard trace | Hazard ID → safety requirement → module contract → test ID | G1, G3, slice acceptance |
| Never-list | Plain-language statements of what the software must never do | G2, all lens reviews |

Use [templates/hazard-entry.md](../../templates/hazard-entry.md).

## The trace is the deliverable

A mitigation that is not traced to a specific contract clause and a specific test is a
statement of intent, not a control. At slice acceptance, every hazard whose mitigation
touches that slice must have a passing test named in the trace.

## Exit criteria

- [ ] Every function assessed against the five questions
- [ ] Hazards raised in the organisational system with IDs recorded, or assessed in `local` records
- [ ] Never-list written in language a non-programmer can check
- [ ] Trace table created (mitigations may point at `TBD` contracts until G3)
