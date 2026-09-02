"""Contract: trajectory. Sole import surface. Clause IDs in CONTRACT.md."""
from dataclasses import dataclass, fields

from baseline.units import MetresPerSecond, Metres, Radians, Seconds

ENGINE_VERSION = "0.1.0"


class ConfigError(ValueError):
    """C-105, C-106."""


@dataclass(frozen=True)
class ScenarioConfig:
    speed: MetresPerSecond
    elevation: Radians
    mass_kg: float
    drag_area_m2: float
    drag_coefficient: float
    dt: Seconds
    seed: int

    @classmethod
    def from_dict(cls, d: dict) -> "ScenarioConfig":
        """C-105: unknown keys are an error, not a silently ignored typo."""
        expected = {f.name for f in fields(cls)}
        unknown = set(d) - expected
        missing = expected - set(d)
        if unknown or missing:
            raise ConfigError(f"unknown keys {sorted(unknown)}, missing keys {sorted(missing)}")
        return cls(**d)


@dataclass(frozen=True)
class Provenance:
    engine_version: str
    config_hash: str
    seed: int
    git_commit: str


@dataclass(frozen=True)
class Trajectory:
    times_s: tuple
    x_m: tuple
    y_m: tuple
    range_m: Metres
    provenance: Provenance


def simulate(config: ScenarioConfig) -> Trajectory:
    """C-101 to C-107."""
    from modules.trajectory.src import integrator
    return integrator.simulate(config)
