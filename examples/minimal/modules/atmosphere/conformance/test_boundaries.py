"""Conformance: atmosphere at the edges of its envelope."""
from baseline.units import Metres
from modules.atmosphere import contract


def test_top_of_envelope_is_near_vacuum_C002():
    # At 80 km any credible profile is below 1e-3 kg/m3; a constant double fails this.
    assert contract.density(Metres(80_000.0)) < 1e-3
