"""Unit tests: model-owned. Never cited in trace/."""
from modules.trajectory.src.integrator import _ground_crossing


def test_ground_crossing_interpolates_linearly():
    x, t = _ground_crossing(x0=0.0, y0=1.0, x1=2.0, y1=-1.0, t1=1.0, dt=1.0)
    assert x == 1.0 and t == 0.5
