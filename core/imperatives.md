---
id: CORE-IMP-001
title: Imperatives
tier: core
status: active
version: 0.1
audience: [human, model]
load: on-task
related: [CORE-SES-001, CORE-PRN-001, HYP-002]
---

# Imperatives

`CLAUDE.md` carries imperatives and pointers; everything else lives in core. That split
only works if "imperative" is defined, so this document defines it.

## Definition

> An **imperative** is a directive that changes what a session does at a decision point it
> will actually reach, stated so that compliance can be judged without loading any other
> document.

## The three tests

An imperative passes all three. Failing any one means it belongs in core with a pointer,
or nowhere.

**1. Actionable.** It names a decision point the session will reach and says what to do
there. Not a state of the world, not a goal.

**2. Self-sufficient.** Compliance is judgeable from the sentence alone. If the model must
read another document to know whether it complied, that document is the rule and
`CLAUDE.md` should carry only a pointer to it.

**3. Non-default.** A competent model would not already do this. This is the pruning test
and the one to apply hardest: an imperative restating ordinary good practice costs context
in every session and prevents nothing ([P6](00-principles.md)).

Grammatical form is not sufficient. *"Follow good design practice"* is grammatically
imperative and fails tests 2 and 3.

## What is not an imperative

Each of these belongs in core. Most yield an imperative as their **behavioural residue** —
the thing a session must do differently at a specific decision point.

| Kind | Example | Derived imperative |
|---|---|---|
| Principle | Rigour follows reversibility | none directly |
| Definition | The contract is everything a consumer may depend on | Import only from `contract.*` |
| Procedure | Baseline change: impact assessment, migration plan, decision record, re-entry at G2 | Stop if a change would touch `baseline/` |
| Rationale | Models write for the case where everything works | none — it justifies an imperative written elsewhere |
| Description | The registry is generated from frontmatter | Run `build_registry.py` after any change |
| Taxonomy | Three change tiers exist | Stop if the slice cannot be built within existing contracts |

Note the pattern: a **procedure** yields a *trigger*, not a summary. `CLAUDE.md` says when
to stop; core says what happens next. Compressing the procedure into `CLAUDE.md` is the
most common way this layer bloats and drifts.

## Form

- One decision point each. If it contains "and", split it.
- Bounded, not aspirational. "Never edit a conformance test to make it pass" is checkable;
  "prefer clean interfaces" is not.
- **No rationale in the imperative.** The pointer carries the why. A model that needs to
  reason about a marginal case follows the pointer; a model in the clear-cut case does not
  pay for the explanation.
- Every imperative names its source document ID. An imperative with no source is a rule
  invented at the operating layer, which is a defect — either find its principle in core or
  delete it.

## Keeping the layers in sync

The operating layer duplicates nothing in substance, but it can drift: a rule changes in
core while `CLAUDE.md` keeps the old imperative, and the session obeys the stale one.

**Rule, both directions:**

> Changing a core document requires checking the imperatives derived from it. Changing an
> imperative requires confirming it still traces to its source. Neither is complete until
> both layers agree.

**Mechanical support.** `tooling/imperatives.json` records each imperative, its source
document, and a hash of that document's body. `tooling/check_imperatives.py` fails when a
source has changed since the imperative was last confirmed:

    python tooling/check_imperatives.py            # CI: fail on drift
    python tooling/check_imperatives.py --accept   # re-record after confirming

This does not prove the imperative is still correct — it forces someone to look. That is a
rung-3 check on the [lesson ladder](lessons/lesson-ladder.md), and it is the strongest
enforcement available for a rule about meaning rather than about form.

It will produce false positives when a source document changes in a way that does not
affect its imperatives. Clearing one is a single command, and the prompt to re-read the
source is usually worth the interruption. If it becomes noise, delete the script and keep
the written rule — do not weaken the rule to match the tool.
