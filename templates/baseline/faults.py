"""Fault-point harness. Copy to baseline/faults.py; do not edit in place.

Rule (CORE-TST-002, rung 3): a fault point is a named point in an operation that
does nothing in production and raises when a test has armed it. It lets a
conformance test force failure at step N of a multi-step operation, which is the
reproducing test a partial-failure finding (AGT-LNS-001) must carry. Every
fault_point("name") in modules/*/src/ or baseline/ must be armed by at least one
passing test under modules/*/conformance/; check_traces.py enforces this
(CORE-TRC-003, Fault points). Place points where a partial-failure finding would
name a step, after a call that can fail and before state is committed, never
speculatively.

In an implementation:

    from baseline.faults import fault_point
    ...
    fault_point("orders.commit")        # C-nnn test hook; no-op unless armed

In a conformance test:

    from baseline import faults

    def test_no_residual_state_after_mid_run_failure_Cnnn():
        faults.arm("orders.commit")
        try:
            with pytest.raises(faults.InjectedFault):
                contract.place(order)
        finally:
            faults.disarm_all()
        assert contract.place(order) == contract.place(order)   # still serves its contract
"""


class InjectedFault(RuntimeError):
    """Raised at an armed fault point."""


_armed: dict[str, BaseException] = {}


def fault_point(name: str) -> None:
    """No-op in production; raises the armed exception when a test has armed `name`."""
    exc = _armed.get(name)
    if exc is not None:
        raise exc


def arm(name: str, exc: BaseException | None = None) -> None:
    """Make the next fault_point(name) raise `exc` (default InjectedFault(name))."""
    _armed[name] = exc or InjectedFault(name)


def disarm_all() -> None:
    """Clear every armed point. Call in the test's finally block."""
    _armed.clear()
