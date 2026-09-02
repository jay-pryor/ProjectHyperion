"""Null double: returns a fixed valid-looking Trajectory and enforces nothing.

The conformance suite MUST fail against this (CORE-TST-002, rung 1). It never
validates dt, never calls the atmosphere, never reaches a fault point. Selected by
TRAJECTORY_IMPL=null; tooling/check_null_doubles.py requires failures in
test_errors and test_invariants."""
from baseline.units import Metres
from modules.trajectory.contract import (ENGINE_VERSION, Provenance, ScenarioConfig,
                                         Trajectory)


def simulate(config: ScenarioConfig) -> Trajectory:
    provenance = Provenance(ENGINE_VERSION, "0" * 16, config.seed, "unknown")
    return Trajectory(times_s=(0.0, 0.5, 1.0), x_m=(0.0, 50.0, 100.0), y_m=(0.0, 1.0, 0.0),
                      range_m=Metres(100.0), provenance=provenance)
