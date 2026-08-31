---
id: SIM-RDS-001
title: Targeted Human Reads — Simulation
tier: profile
status: draft
version: 0.1
audience: [human]
load: on-task
related: [CORE-REV-004, SIM-000]
---

# Targeted Human Reads — Simulation

Extends [CORE-REV-004](../../core/reviews/targeted-human-reads.md). These replace the
authorisation and destructive-operation items for engine code, which usually has neither.

Read these. Do not line-read the rest.

## 1. Units and reference frames at every module boundary

The highest-value read in this profile. Lens reviews are structurally poor at catching
this, because each module is internally consistent and the defect exists only in the
relationship between them.

Check: every quantity crossing a contract carries its unit in the type; frame conversions
happen exactly once; no conversion is applied twice; degrees and radians are never
interchangeable.

## 2. State initialisation

What is the state at t=0, and is every field explicitly set? Models initialise the fields
they are thinking about and leave the rest at language defaults. A zero that should have
been a configured value produces a plausible run.

## 3. The integrator and timestep handling

Step size, method, stability conditions, and behaviour when the step is changed. Check
that the stability condition is *enforced or reported*, not assumed. Also: does anything
depend on step size that should not?

## 4. Boundary and envelope handling

What happens at the edge of the validity envelope, and is leaving it detected and
reported? Silent extrapolation is the S1 defect of this profile.

## 5. Scenario configuration parsing

Config is user input. Check: unknown keys rejected rather than ignored, missing keys
either defaulted explicitly or rejected, ranges validated, and the loaded configuration
echoed into output provenance. A typo'd key silently ignored is a wrong answer with no
signal.

## 6. Anything with a tolerance in it

Every hard-coded epsilon, convergence threshold, and comparison tolerance. Where did the
number come from? Models produce plausible tolerances with no basis, and a tolerance is a
correctness claim.

## 7. Stochastic stream allocation

Per [SIM-DET-001](determinism.md). Check that a newly added stochastic process does not
perturb existing streams.

## Then: look at the output

Plot something. Run a scenario whose answer you know and look at the curve. This catches a
class of defect that no test in the suite will, and it is ten minutes.
