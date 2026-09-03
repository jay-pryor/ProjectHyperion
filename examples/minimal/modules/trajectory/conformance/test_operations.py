"""Conformance: trajectory operations. Written from SL-01 acceptance criteria."""
import os

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


def test_provenance_identifies_this_run_C103():
    # Present is not the same as informative: a constant hash and a commit nobody
    # captured satisfy "carries provenance" and reproduce nothing (HZ-002).
    a = contract.simulate(vacuum(speed=100.0)).provenance
    b = contract.simulate(vacuum(speed=101.0)).provenance
    assert a.config_hash != b.config_hash
    os.environ["HYPERION_COMMIT"] = "0123456789abcdef"
    try:
        assert contract.simulate(vacuum()).provenance.git_commit == "0123456789abcdef"
    finally:
        del os.environ["HYPERION_COMMIT"]
