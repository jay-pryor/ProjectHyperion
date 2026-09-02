"""Fixed-step semi-implicit Euler integrator. Internal. DEC-001."""
import hashlib
import math
import os

from baseline.faults import fault_point
from baseline.units import Metres
from modules.atmosphere import contract as atmosphere
from modules.trajectory.contract import (ENGINE_VERSION, ConfigError, Provenance,
                                         ScenarioConfig, Trajectory)

G_M_S2 = 9.80665
MAX_STEPS = 50_000_000


def _config_hash(config: ScenarioConfig) -> str:
    canonical = repr(sorted(vars(config).items()))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _ground_crossing(x0, y0, x1, y1, t1, dt):
    frac = y0 / (y0 - y1)
    return x0 + (x1 - x0) * frac, t1 - dt + dt * frac


def simulate(config: ScenarioConfig) -> Trajectory:
    if not (0.0 < config.dt <= 0.1):
        raise ConfigError(f"dt {config.dt} s outside (0, 0.1]")   # C-106

    dt = float(config.dt)
    k = 0.5 * config.drag_coefficient * config.drag_area_m2 / config.mass_kg
    vx = config.speed * math.cos(config.elevation)
    vy = config.speed * math.sin(config.elevation)
    x = y = t = 0.0
    times, xs, ys = [0.0], [0.0], [0.0]

    for step in range(1, MAX_STEPS + 1):
        if step == 10:
            fault_point("trajectory.integrate")          # C-107 test hook
        rho = atmosphere.density(Metres(y))              # raises above envelope: C-104
        v = math.hypot(vx, vy)
        vx += -k * rho * v * vx * dt
        vy += (-G_M_S2 - k * rho * v * vy) * dt
        nx, ny, t = x + vx * dt, y + vy * dt, t + dt
        if ny < 0.0:
            x_ground, t_ground = _ground_crossing(x, y, nx, ny, t, dt)
            times.append(t_ground); xs.append(x_ground); ys.append(0.0)
            break
        x, y = nx, ny
        times.append(t); xs.append(x); ys.append(y)
    else:
        raise RuntimeError("projectile did not land within MAX_STEPS")

    provenance = Provenance(ENGINE_VERSION, _config_hash(config), config.seed,
                            os.environ.get("HYPERION_COMMIT", "unknown"))
    return Trajectory(tuple(times), tuple(xs), tuple(ys), Metres(xs[-1]), provenance)
