"""Conformance: trajectory invariants, including the fault-point test for C-107."""
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
