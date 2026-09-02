"""Conformance: every documented error condition of atmosphere."""
import pytest

from baseline.units import Metres
from modules.atmosphere import contract


def test_above_envelope_raises_C003():
    with pytest.raises(contract.EnvelopeError):
        contract.density(Metres(80_000.5))


def test_below_envelope_raises_C003():
    with pytest.raises(contract.EnvelopeError):
        contract.density(Metres(-1.0))


def test_envelope_edges_are_inclusive_C003():
    contract.density(Metres(0.0))
    contract.density(Metres(80_000.0))
