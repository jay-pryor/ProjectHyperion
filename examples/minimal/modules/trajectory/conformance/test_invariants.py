"""Conformance: trajectory invariants, including the fault-point test for C-107."""
import math

import pytest

from baseline import faults
from modules.trajectory import contract
from modules.trajectory.conformance._scenarios import vacuum


def test_bit_identical_repeat_C102():
    assert contract.simulate(vacuum()) == contract.simulate(vacuum())


def test_no_residual_state_after_mid_run_failure_C107():
    faults.arm("trajectory.integrate")
    try:
        with pytest.raises(faults.InjectedFault):
            contract.simulate(vacuum())
    finally:
        faults.disarm_all()
    # The module still serves its contract afterwards, identically.
    assert contract.simulate(vacuum()) == contract.simulate(vacuum())


def test_samples_run_from_launch_to_impact_C108():
    # The arrays are the answer, not decoration. Written from C-108 after mutation
    # triage found nothing in the suite that could tell a reversed clock, a dropped
    # sample, or a range read off the wrong point.
    r = contract.simulate(vacuum())
    assert len(r.times_s) == len(r.x_m) == len(r.y_m) >= 2
    assert all(math.isfinite(v) for v in r.times_s + r.x_m + r.y_m)
    assert (r.times_s[0], r.x_m[0], r.y_m[0]) == (0.0, 0.0, 0.0)
    assert all(b > a for a, b in zip(r.times_s, r.times_s[1:]))
    assert all(b > a for a, b in zip(r.x_m, r.x_m[1:]))
    assert max(r.y_m) > 0.0 and r.y_m[-1] == 0.0
    assert r.range_m == r.x_m[-1]
