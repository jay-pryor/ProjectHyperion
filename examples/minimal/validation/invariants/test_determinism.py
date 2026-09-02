"""Validation, class: invariant. Bit-identical repeat runs across scenarios."""
import pytest

from modules.trajectory import contract
from modules.trajectory.conformance._scenarios import vacuum


@pytest.mark.parametrize("elevation_deg", [10.0, 45.0, 80.0])
def test_repeat_run_identical_across_scenarios(elevation_deg):
    cfg = vacuum(speed=300.0, elevation_deg=elevation_deg, dt=0.01)
    assert contract.simulate(cfg) == contract.simulate(cfg)
