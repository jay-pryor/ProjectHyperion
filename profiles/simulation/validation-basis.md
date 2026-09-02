---
id: SIM-VAL-001
title: Validation Basis
tier: profile
status: draft
version: 0.1
audience: [human, model]
load: on-task
sessions: [GATE, CONFORMANCE]
related: [SIM-000, CORE-LFC-003, CORE-TST-001]
---

# Validation Basis — Simulation

Verification asks *does the code match the contract*. Validation asks *is the answer
right*. In simulation these diverge sharply, and only the second one matters to the
person using the output.

Defined at [G1](../../core/lifecycle/g1-requirements-validation-basis.md), before
architecture.

## Evidence classes, strongest first

### 1. Analytical cases
A closed-form solution the model must match within tolerance. Vacuum ballistics, constant
velocity intercept, two-body orbit, unattenuated free-space path loss. Every simulation
has some regime where the maths is exactly solvable; find it and pin it.

### 2. Conservation checks
Energy, momentum, mass, and count balance across a run. Cheap, run on every scenario, and
they catch integrator errors and state corruption that no unit test will.

### 3. Invariants and round-trips
Frame transform round-trips to identity. Unit conversions round-trip. Ordering is
preserved. Reversible operations reverse. Ideal property-test material.

### 4. Degenerate and limit cases
Zero input, stationary target, infinite range, single entity, empty scenario, zero
timestep. Known answers at the limits, and where most numerical defects surface first.

### 5. Dimensional analysis
Automated where the type system allows. Unit errors at module boundaries are a leading
defect class and are invisible to a model reviewing one module in isolation, because each
side is internally consistent.

### 6. Reference data
Trusted external dataset, prior tool, or published result. Record the source, its version,
and its own validity limits — reference data has an envelope too.

### 7. Convergence behaviour
Halve the timestep; the answer should converge, not wander. A result that changes
materially with step size is not a result. This is the check most often skipped.

### 8. Expert judgement
A named human inspects a named output. Legitimate and often the only option — record it
as such so the confidence level of the whole system stays visible.

## Validity envelope

Every model states the domain over which it has been validated: speed range, altitude
range, geometry, timestep bounds, entity count.

**Running outside the envelope must be detected and reported in the output**, not left to
the user to notice. An unflagged extrapolation is the highest-severity defect class in
this profile, because it produces confident wrong numbers with no signal at all.

## Validation suite

Separate from the test suite and run separately.

```
validation/
  analytical/     # closed-form comparisons with tolerances
  conservation/   # invariant checks across scenarios
  convergence/    # timestep refinement studies
  reference/      # external datasets, with provenance
  envelope/       # boundary-of-validity behaviour
```

Runs on every baseline change and before every release. Tolerances are declared, versioned,
and justified — a tolerance loosened to make a test pass is an S1 finding, and the review
prompt should say so.

## Reporting

Validation status is user-visible. A result presented without its validation status
invites the reader to assume more confidence than the evidence supports, and that is the
mechanism by which simulation output causes harm.
