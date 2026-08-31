---
id: CORE-LFC-002
title: "G0 — Hazard & Context"
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-LFC-001, CORE-LFC-003]
---

# G0 — Hazard & Context

The first gate, before requirements and before architecture. It answers: **what must
this software never do, and what happens when it fails?**

## Why this is gate zero

Hazard-driven requirements are the part of this work a model cannot do for you. A model
can write competent code all day; it cannot know what the payload is bolted to, what is
underneath it, or what else is on the RF spectrum at the time. This gate is where
systems-engineering discipline outperforms coding fluency, and it generates requirements
that all later gates inherit.

## Inputs

- Operational context: where this runs, who operates it, what it is connected to.
- The organisation's existing hazard management system. Hyperion does **not** replace it.
  Hazards are raised, assessed, and tracked in the organisational system; Hyperion holds
  the **trace** from hazard to module contract to test.
- Interfacing systems and their failure modes.

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
| Hazard register entry (org system) | Hazard, cause, severity, likelihood, mitigation | Org safety process |
| Hyperion hazard trace | Hazard ID → safety requirement → module contract → test ID | G1, G3, slice acceptance |
| Never-list | Plain-language statements of what the software must never do | G2, all lens reviews |

Use [templates/hazard-entry.md](../../templates/hazard-entry.md).

## The trace is the deliverable

A mitigation that is not traced to a specific contract clause and a specific test is a
statement of intent, not a control. At slice acceptance, every hazard whose mitigation
touches that slice must have a passing test named in the trace.

## Exit criteria

- [ ] Every function assessed against the five questions
- [ ] Hazards raised in the organisational system, IDs recorded
- [ ] Never-list written in language a non-programmer can check
- [ ] Trace table created (mitigations may point at `TBD` contracts until G3)
