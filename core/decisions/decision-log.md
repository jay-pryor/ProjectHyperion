---
id: CORE-DEC-001
title: Decision Log
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
sessions: [GATE, CONTRACT, BASELINE]
related: [CORE-CHG-002, CORE-LFC-004]
---

# Decision Log

Append-only. One record per significant decision.

## What gets a record

- Every Baseline change
- Every tech stack choice
- Every architectural decision with a seriously considered alternative
- Every decision you expect to be questioned later, including by yourself

Not: internal implementation choices, anything reversible in an afternoon.

## The valuable part is the rejected alternatives

A record stating what you chose is a note. A record stating what you rejected and why is
what stops you relitigating the same decision at month four, and it is what makes the
decision reviewable by someone who was not there.

## Format

Template: [templates/decision-record.md](../../templates/decision-record.md).

```
ID · Date · Status (proposed / accepted / superseded by DEC-nnn)
Context      — what forced a decision now
Decision     — what was chosen, stated plainly
Alternatives — each with why it was rejected
Consequences — what this makes easy, what it makes hard, what it locks in
Reversal     — what it would cost to undo, and what would trigger doing so
```

The **reversal** field is Hyperion-specific and does real work: it is your
[P1](../00-principles.md) classification recorded at the time you had the most context.
Decisions with an expensive reversal deserve gate ceremony; decisions with a cheap one do
not, and writing the field forces the assessment.

## Superseding

Records are never edited or deleted. A superseded record has its status changed and
points forward. The history of how the architecture arrived where it is has real value
when the architecture is next challenged.
