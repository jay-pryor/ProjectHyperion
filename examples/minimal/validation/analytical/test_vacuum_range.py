"""Validation, class: analytical and convergence (SIM-VAL-001).
Human-specified cases; expected values derived independently of the code."""
import pytest

from modules.trajectory import contract
from modules.trajectory.conformance._scenarios import closed_form_range, vacuum


@pytest.mark.parametrize("elevation_deg", [15.0, 45.0, 75.0])
def test_range_matches_closed_form(elevation_deg):
    result = contract.simulate(vacuum(speed=100.0, elevation_deg=elevation_deg, dt=0.005))
    expected = closed_form_range(100.0, elevation_deg)
    assert abs(result.range_m - expected) / expected < 0.005


def test_error_halves_when_step_halves():
    expected = closed_form_range(100.0, 45.0)
    coarse = abs(contract.simulate(vacuum(dt=0.01)).range_m - expected)
    fine = abs(contract.simulate(vacuum(dt=0.005)).range_m - expected)
    assert fine < coarse
