"""Unit tests: model-written, model-maintained. Not read by the human and never
named in trace/ (they cannot verify a requirement)."""
import math

from baseline.units import Metres
from modules.atmosphere.src import exponential


def test_scale_height_gives_one_over_e():
    ratio = exponential.density(Metres(8_500.0)) / exponential.density(Metres(0.0))
    assert math.isclose(ratio, math.exp(-1), rel_tol=1e-12)
