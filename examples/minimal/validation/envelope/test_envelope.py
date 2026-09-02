"""Validation, class: degenerate / envelope. Leaving the validity envelope is
detected and reported, never silently extrapolated (IMP-11)."""
import pytest

from modules.atmosphere.contract import EnvelopeError
from modules.trajectory import contract
from modules.trajectory.conformance._scenarios import vacuum


def test_apex_beyond_envelope_is_rejected():
    with pytest.raises(EnvelopeError):
        contract.simulate(vacuum(speed=1500.0, elevation_deg=85.0, dt=0.01))


def test_apex_inside_envelope_is_accepted():
    contract.simulate(vacuum(speed=1000.0, elevation_deg=60.0, dt=0.01))   # apex ~38 km
