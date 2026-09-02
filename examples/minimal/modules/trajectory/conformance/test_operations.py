"""Conformance: trajectory operations. Written from SL-01 acceptance criteria."""
from modules.trajectory import contract
from modules.trajectory.conformance._scenarios import closed_form_range, vacuum


def test_vacuum_range_matches_closed_form_C101():
    # 0.5 %: first-order ground-crossing interpolation at dt = 0.005 s is ~0.03 %;
    # the margin covers any conforming integrator (DEC-001).
    result = contract.simulate(vacuum(speed=100.0, elevation_deg=45.0))
    expected = closed_form_range(100.0, 45.0)
    assert abs(result.range_m - expected) / expected < 0.005


def test_provenance_present_C103():
    p = contract.simulate(vacuum()).provenance
    assert p.engine_version and p.config_hash and p.git_commit
    assert p.seed == 1
