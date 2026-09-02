# Contract: trajectory
Version: 1.2 · Status: active

## 1. Purpose
Integrate a point-mass projectile with drag from launch to ground impact.

## 2. Operations
`simulate(config: ScenarioConfig) -> Trajectory` — in `contract.py`.
`ScenarioConfig.from_dict(d)` — the only way to build a config from user input.

## 3. Data shapes
`ScenarioConfig`, `Trajectory`, `Provenance` in `contract.py`. Units in field types.

## 4. Error conditions
| Operation | Condition | Signalled as | Caller obligation |
|---|---|---|---|
| from_dict | unknown or missing key | `ConfigError` | Reject the scenario; do not default |
| simulate | `dt` outside (0, 0.1] s | `ConfigError` | Reject the scenario |
| simulate | trajectory leaves the atmosphere envelope | `EnvelopeError` | Report the run as invalid; no partial result |

## 5. Behavioural promises
- **C-101** With `drag_coefficient = 0` and `dt ≤ 0.01`, `range_m` is within 0.5 % of v² sin 2θ / g.
- **C-102** Deterministic: identical config gives bit-identical `Trajectory`.
- **C-103** Every `Trajectory` carries `Provenance` (engine version, config hash, seed, commit).
- **C-104** A trajectory that leaves the atmosphere envelope raises; density is never extrapolated.
- **C-105** `from_dict` rejects unknown keys and missing keys.
- **C-106** `dt` must be in (0, 0.1] s.
- **C-107** A failure mid-integration leaves no residual state; the next call is unaffected.
- Side effects: none. Wall-clock time is never read.

## 6. Performance envelope
O(flight time / dt).

## 7. Trace
REQ-002, REQ-004, REQ-005.

## Explicitly not promised
The integration method, or agreement with the closed form at any specific `dt` above 0.01 s.
