# Contract: atmosphere
Version: 1.1 · Status: active

## 1. Purpose
Report air density at a geometric altitude.

## 2. Operations
`density(altitude: Metres) -> KgPerM3` — in `contract.py`.

## 3. Data shapes
`Metres`, `KgPerM3` from `baseline/units`.

## 4. Error conditions
| Operation | Condition | Signalled as | Caller obligation |
|---|---|---|---|
| density | altitude below 0 m or above 80 000 m | `EnvelopeError` | Do not catch and substitute; stop the run |

## 5. Behavioural promises
- **C-001** Sea-level density is 1.225 kg/m³ exactly (ISA constant).
- **C-002** Density is strictly decreasing with altitude across the envelope.
- **C-003** Any altitude outside 0 to 80 000 m inclusive raises `EnvelopeError`. Never extrapolated.
- **C-004** Deterministic: identical input gives bit-identical output.
- Side effects: none. Concurrency: safe, no shared state.

## 6. Performance envelope
O(1) per call.

## 7. Trace
REQ-001, REQ-003 (see `trace/requirements.yaml`).

## Explicitly not promised
The functional form of the profile. Consumers must not assume exponential decay.
