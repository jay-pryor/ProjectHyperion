"""Contract: atmosphere. The module's sole import surface (CORE-CON-003).
Clause IDs (C-nnn) are defined in CONTRACT.md and cited by conformance tests."""
import os

from baseline.units import KgPerM3, Metres

ENVELOPE_MIN = Metres(0.0)
ENVELOPE_MAX = Metres(80_000.0)


class EnvelopeError(ValueError):
    """C-003: altitude outside the validated envelope."""


def density(altitude: Metres) -> KgPerM3:
    """C-001, C-002, C-003, C-004."""
    return _impl().density(altitude)


def _impl():
    # Selecting the implementation by environment lets the conformance suite run
    # unchanged against the real implementation and against the null double.
    if os.environ.get("ATMOSPHERE_IMPL") == "null":
        from modules.atmosphere import null_double as m
    else:
        from modules.atmosphere.src import exponential as m
    return m
