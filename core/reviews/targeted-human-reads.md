---
id: CORE-REV-004
title: Targeted Human Reads
tier: core
status: active
audience: [human]
load: on-task
sessions: []
prevents: Human attention spread evenly over implementation code instead of concentrated where models are predictably weak
reader: The human before build (criteria and contracts) and after build (the profile's list), per slice
related: [CORE-REV-001, CORE-REV-003, CORE-REV-005, CORE-PRN-001, CORE-TRC-003]
---

# Targeted Human Reads

Where your attention goes. Short, specific, and profile-dependent
([P5](../00-principles.md)).

## The rule

> Do not line-read implementation code. It does not scale, and the tests exist so that
> it does not have to.

Read a named, narrow list where models are predictably weak and automated checks cannot
reach.

## Before build — the highest-value hour

**Acceptance criteria and contract design.** This is the most valuable human time in the
entire project. The model will faithfully build what it read, and every conformance test
inherits that reading. An ambiguous acceptance criterion produces an implementation and a
test suite that agree with each other and are both wrong.

Read for: ambiguity, unstated units and frames, missing error conditions, implicit
ordering assumptions, and the word "should".

## After build — core list

Applies to every profile.

1. **Authorisation and privilege**, where the profile has any. Happy-path bias is the
   model's most reliable failure. Everything the code does *on behalf of* someone.
2. **Destructive and irreversible operations.** Confirmation, idempotency, audit,
   reversal path. Anything that writes to a real system.
3. **Data migrations.** Models write clean forward migrations and forget that records
   already exist in the old shape.
4. **Partial-failure and concurrency behaviour.** What happens when step three of five
   fails, or two operations interleave. Models write for the case where everything works.

## After build — profile additions

Each profile defines its own additions. See
[SIM-RDS-001](../../profiles/simulation/targeted-reads.md) for simulation.

Embedded, when written, will add ISR boundaries, volatile qualification, atomicity of
shared access, stack sizing, and anything touching a peripheral register — because those
defects are timing- and hardware-state dependent, invisible to unit tests, and invisible
to review by a model that has never seen the errata.

## Then: use it

Hands-on time, per slice, before acceptance: [CORE-LFC-006](../lifecycle/slice-loop.md#hands-on-time).

## Recording

A read that leaves no record is, in the words of [CORE-LFC-002](../lifecycle/g0-hazard-context.md#the-trace-is-the-deliverable),
a statement of intent and not a control. So each read is a row in `trace/reviews.yaml`
with `kind: targeted_read` and the slice in its `slice` field
([CORE-TRC-003](../traceability/trace-logs.md#review)), and a slice is not accepted until
at least one such row names it with a disposition other than `pending`;
`tooling/check_traces.py` fails the slice otherwise. What is required is the artifact of
having read, on the same footing as every other acceptance condition. Whether the reading
was any good is not mechanically knowable and is not what is being checked.

`findings_raised` satisfies it — the read happened, and what it found is dispositioned
under [CORE-REV-005](review-findings-handling.md) and gated by the definition of done, not
here. `failed` is not a meaningful outcome for a read: a read does not fail, only the
thing being read does. `pending` is the normal state mid-slice and stays legal until the
slice is accepted.

## Time budget

If the list above takes more than about an hour per slice, the slice is too large or the
targeted list has grown beyond its purpose. Cut the slice, not the reading.
