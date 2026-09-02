"""Exponential atmosphere. Internal; consumers import contract.py only."""
import math

from baseline.units import KgPerM3, Metres
from modules.atmosphere.contract import ENVELOPE_MAX, ENVELOPE_MIN, EnvelopeError

SEA_LEVEL_DENSITY_KG_M3 = 1.225   # ISA
SCALE_HEIGHT_M = 8_500.0          # ASM-001


def density(altitude: Metres) -> KgPerM3:
    if not (ENVELOPE_MIN <= altitude <= ENVELOPE_MAX):
        raise EnvelopeError(
            f"altitude {altitude} m outside validated envelope "
            f"[{ENVELOPE_MIN}, {ENVELOPE_MAX}] m"
        )
    return KgPerM3(SEA_LEVEL_DENSITY_KG_M3 * math.exp(-altitude / SCALE_HEIGHT_M))
