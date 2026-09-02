"""Conformance: atmosphere invariants. Plain loops stand in for property tests
so the example has no dependencies; a real project uses hypothesis."""
from baseline.units import Metres
from modules.atmosphere import contract


def test_monotonically_decreasing_C002():
    previous = contract.density(Metres(0.0))
    for h in range(500, 80_001, 500):
        current = contract.density(Metres(float(h)))
        assert current < previous, f"density not decreasing at {h} m"
        previous = current


def test_deterministic_C004():
    a = [contract.density(Metres(float(h))) for h in range(0, 80_001, 1000)]
    b = [contract.density(Metres(float(h))) for h in range(0, 80_001, 1000)]
    assert a == b
