"""Conformance: every documented error condition of trajectory."""
import math

import pytest

from modules.atmosphere.contract import EnvelopeError
from modules.trajectory import contract
from modules.trajectory.conformance._scenarios import vacuum


def test_unknown_config_key_rejected_C105():
    d = vars(vacuum()) | {"drag_coeficient": 0.3}   # typo'd key must not be ignored
    with pytest.raises(contract.ConfigError):
        contract.ScenarioConfig.from_dict(d)


def test_missing_config_key_rejected_C105():
    d = dict(vars(vacuum()))
    del d["seed"]
    with pytest.raises(contract.ConfigError):
        contract.ScenarioConfig.from_dict(d)


def test_bad_dt_rejected_C106():
    with pytest.raises(contract.ConfigError):
        contract.simulate(vacuum(dt=0.5))


def test_dt_bounds_are_exactly_C106():
    # (0, 0.1]: zero is out, 0.1 is in. An interval is two decisions, and a suite that
    # only tries 0.5 s makes neither of them.
    with pytest.raises(contract.ConfigError):
        contract.simulate(vacuum(dt=0.0))
    contract.simulate(vacuum(dt=0.1))


def test_leaving_envelope_raises_C104():
    # Apex of a 2000 m/s shot at 80 deg is ~198 km, far above the 80 km envelope.
    with pytest.raises(EnvelopeError):
        contract.simulate(vacuum(speed=2000.0, elevation_deg=80.0, dt=0.01))
