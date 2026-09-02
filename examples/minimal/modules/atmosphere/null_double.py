"""Null double: returns fixed valid-looking data and enforces nothing.

The conformance suite MUST fail against this. A suite this double passes checks
shape, not behaviour. CI runs the suite against it and requires failures in
errors, invariants, and boundaries (the stub-as-mutant rule)."""
from baseline.units import KgPerM3, Metres


def density(altitude: Metres) -> KgPerM3:
    return KgPerM3(1.225)
