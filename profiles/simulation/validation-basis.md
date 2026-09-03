---
id: SIM-VAL-001
title: Validation Basis
tier: profile
status: draft
audience: [human, model]
load: on-task
sessions: [GATE, CONFORMANCE]
prevents: A simulation result presented with more confidence than its evidence supports, or run outside the envelope it was validated for
reader: GATE sessions at G1 naming evidence classes, and CONFORMANCE sessions writing validation cases
related: [SIM-000, CORE-LFC-003, CORE-TST-001]
---

# Validation Basis — Simulation

Verification asks *does the code match the contract*. Validation asks *is the answer
right* ([P7](../../core/00-principles.md)). In simulation these diverge sharply, and only
the second one matters to the person using the output.

Defined at [G1](../../core/lifecycle/g1-requirements-validation-basis.md), before
architecture.

## Evidence classes, strongest first

The classes themselves are the table in
[G1](../../core/lifecycle/g1-requirements-validation-basis.md); this section is what each
one means in simulation, ordered by the weight of the evidence it gives.

**`analytical`** — a closed-form solution the model must match within tolerance. Vacuum
ballistics, constant velocity intercept, two-body orbit, unattenuated free-space path
loss. Every simulation has some regime where the maths is exactly solvable; find it and
pin it.

**`conservation`** — energy, momentum, mass, and count balance across a run. Cheap, run on
every scenario, and they catch integrator errors and state corruption that no unit test
will.

**`invariant`** — frame transform round-trips to identity, unit conversions round-trip,
ordering is preserved, reversible operations reverse. Ideal property-test material.
Dimensional analysis records here: unit errors at module boundaries are a leading defect
class and are invisible to a model reviewing one module in isolation, because each side is
internally consistent, so automate the dimensional check where the type system allows and
record it as the invariant it is.

**`degenerate`** — zero input, stationary target, infinite range, single entity, empty
scenario, zero timestep. Known answers at the limits, and where most numerical defects
surface first.

**`reference`** — trusted external dataset, prior tool, or published result. Record the
source, its version, and its own validity limits — reference data has an envelope too.

**`convergence`** — halve the timestep; the answer should converge, not wander. A result
that changes materially with step size is not a result. This is the check most often
skipped.

**`expert_judgement`** — a named human inspects a named output. Legitimate and often the
only option — record it as such so the confidence level of the whole system stays visible.

## Validity envelope

Every model states the domain over which it has been validated: speed range, altitude
range, geometry, timestep bounds, entity count.

**Running outside the envelope must be detected and reported in the output**, not left to
the user to notice. An unflagged extrapolation is the highest-severity defect class in
this profile, because it produces confident wrong numbers with no signal at all.

## Validation suite

Separate from the test suite and run separately. Cases live under `validation/`, grouped
by whatever the project finds readable — `examples/minimal` groups by class
(`analytical/`, `invariants/`, `envelope/`) and adds directories as it earns them. Nothing
enforces the grouping: `validated_by` carries the path
([CORE-TRC-002](../../core/traceability/trace-records.md)), so a layout here would be a
rule no check could hold and the first project to diverge would make it a lie.

Runs on every baseline change and before every release. Tolerances are declared, versioned,
and justified — a tolerance loosened to make a test pass is an S1 finding, and the review
prompt should say so.

## Reporting

Validation status is user-visible. A result presented without its validation status
invites the reader to assume more confidence than the evidence supports, and that is the
mechanism by which simulation output causes harm.
