"""Fault-point harness.

A named point in an operation that does nothing in production and raises when a
test has armed it. It lets a conformance test force failure at step N of a
multi-step operation, which is what a partial-failure finding needs in order to
carry a reproducing test (AGT-LNS-001). Every fault point named in code must be
exercised by at least one conformance test.
"""

class InjectedFault(RuntimeError):
    """Raised at an armed fault point."""


_armed: dict[str, BaseException] = {}


def fault_point(name: str) -> None:
    exc = _armed.get(name)
    if exc is not None:
        raise exc


def arm(name: str, exc: BaseException | None = None) -> None:
    _armed[name] = exc or InjectedFault(name)


def disarm_all() -> None:
    _armed.clear()
