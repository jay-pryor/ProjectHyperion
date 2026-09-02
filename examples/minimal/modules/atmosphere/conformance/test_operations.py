"""Conformance: atmosphere operations. Written from SL-02 acceptance criteria
in a CONFORMANCE session, before implementation."""
from baseline.units import Metres
from modules.atmosphere import contract


def test_sea_level_density_C001():
    # Tolerance 1e-9: C-001 promises the ISA constant exactly; float repr only.
    assert abs(contract.density(Metres(0.0)) - 1.225) <= 1e-9


def test_density_is_positive_C001():
    assert contract.density(Metres(10_000.0)) > 0.0
