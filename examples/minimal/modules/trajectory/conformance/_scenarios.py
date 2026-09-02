"""Shared scenario builders for the trajectory conformance suite."""
import math

from modules.trajectory.contract import ScenarioConfig


def vacuum(speed=100.0, elevation_deg=45.0, dt=0.005, seed=1):
    return ScenarioConfig(speed=speed, elevation=math.radians(elevation_deg),
                          mass_kg=1.0, drag_area_m2=0.01, drag_coefficient=0.0,
                          dt=dt, seed=seed)


def closed_form_range(speed, elevation_deg):
    return speed ** 2 * math.sin(2 * math.radians(elevation_deg)) / 9.80665
