---
id: CORE-REV-002
title: Gate Reviews
tier: core
status: active
version: 0.1
audience: [human]
load: on-task
sessions: []
related: [CORE-REV-001, CORE-LFC-001, CORE-CHG-001]
---

# Gate Reviews

Human review of gate artifacts. The question is always **is this the right thing,
decomposed the right way** — never whether the code is good, because at gate time there
is no code.

## Reviewer availability

For a single-operator project, most gate reviews are self-reviews. That is legitimate
and should be **recorded as such**, so the confidence level attached to each gate is
visible later when something goes wrong.

Where an external reviewer is available but does not read code, the gate artifacts are
specifically designed for them:

| Gate | Reviewable by a non-programmer systems engineer? | What they should be given |
|---|---|---|
| G0 Hazard | Yes — this is their strongest ground | Never-list, hazard register, five-question analysis |
| G1 Requirements | Yes | Requirements register, validation basis table, assumptions |
| G2 Architecture | Yes | Mermaid diagram, module responsibilities, decision records with rejected alternatives |
| G3 Contracts | Partially | Interface specs as prose tables; not the code |
| Slice acceptance | No | — |

A systems engineer who cannot read C can absolutely tell you that your subsystem
decomposition is wrong or that you have missed a failure mode. That review is worth more
than a line-by-line one and it is the review you can actually obtain.

## Self-review protocol

Self-review degrades into rubber-stamping unless it is structured. Two mechanisms:

**Delay.** Review gate artifacts at least one working day after producing them. Same-day
self-review reproduces the same reasoning.

**Adversarial prompt list.** Work a fixed checklist rather than reading freely:

- Which requirement is allocated to more than one module?
- Which module responsibility contains the word "and"?
- Which hazard mitigation has no named test?
- Which decision has no recorded rejected alternative?
- What would have to be true for this decomposition to be wrong?
- Which interface would be most expensive to change in three months?

**Then run the machine gate reviews** as a supplement:
[validation-review](../../agents/validation-review.md) pointed at the artifacts rather
than at code. Fresh instance, no priming.

## Recording

Each gate review is a row in `trace/reviews.yaml` — `kind: gate`, `gate: Gn`, date,
reviewer (including "self"), findings, disposition — with the schema in CORE-TRC-002. The
row with `disposition: passed` is what makes the gate passed; no line in `CLAUDE.md`
states gate state. The trace checker derives its strictness from that row, and change-tier
classification ([CORE-CHG-001](../change-control/change-tiers.md)) applies only after
G3's row exists. Two minutes; it is what lets you calibrate later whether self-review is
catching enough.
