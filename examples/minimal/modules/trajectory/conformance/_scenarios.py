"""Shared scenario builders for the trajectory conformance suite."""
import math

from baseline.units import MetresPerSecond, Radians, Seconds
from modules.trajectory.contract import ScenarioConfig


def vacuum(speed: float = 100.0, elevation_deg: float = 45.0,
           dt: float = 0.005, seed: int = 1) -> ScenarioConfig:
    return ScenarioConfig(speed=MetresPerSecond(speed),
                          elevation=Radians(math.radians(elevation_deg)),
                          mass_kg=1.0, drag_area_m2=0.01, drag_coefficient=0.0,
                          dt=Seconds(dt), seed=seed)


def closed_form_range(speed: float, elevation_deg: float) -> float:
    return speed ** 2 * math.sin(2 * math.radians(elevation_deg)) / 9.80665
