#!/usr/bin/env python3
"""Require every conformance suite to fail against its module's null double.

A suite that cannot fail is assumed to be a control. Rung 1 of CORE-TST-002: every
module with a src/ ships modules/<m>/null_double.*, a trivial implementation returning
fixed valid-looking data, selected by <MODULE>_IMPL=null. The suite must fail against it
in every one of test_errors, test_invariants, test_boundaries that exists; it may pass
test_operations. A module with a src/ and no null double is an error.

Usage:
    python tooling/check_null_doubles.py <project_root>      # exit 1 on any module failing

Each module's suite runs in a subprocess with the variable set and a temporary JUnit
file, so the project's own trace/results.xml keeps the real run (CORE-TRC-003).
"""

import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

REQUIRED = ("test_errors", "test_invariants", "test_boundaries")   # must fail
OPTIONAL = ("test_operations",)                                     # may pass


def env_name(module):
    return module.upper().replace("-", "_") + "_IMPL"


def discover(root):
    """(module name, null double path or None) for every module with a src/ or a null double."""
    found = []
    for mdir in sorted(p for p in (root / "modules").glob("*") if p.is_dir()):
        doubles = sorted(mdir.glob("null_double.*"))
        if (mdir / "src").is_dir() or doubles:
            found.append((mdir.name, doubles[0] if doubles else None))
    return found


def run_suite(root, module, junit):
    """Run the module's conformance directory against the null double; return pytest's exit code."""
    env = dict(os.environ, **{env_name(module): "null"})
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           f"modules/{module}/conformance", f"--junitxml={junit}"]
    return subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True).returncode


def outcomes_by_file(junit):
    """{test file stem: (failed, total)} from a JUnit report."""
    counts = {}
    for case in ET.parse(junit).getroot().iter("testcase"):
        stem = case.get("classname", "").split(".")[-1]
        failed, total = counts.get(stem, (0, 0))
        broke = case.find("failure") is not None or case.find("error") is not None
        counts[stem] = (failed + (1 if broke else 0), total + 1)
    return counts


def files_present(root, module):
    conformance = root / "modules" / module / "conformance"
    return {p.stem for p in conformance.glob("test_*") if p.is_file()}


def check_module(root, module, double, out):
    """Print one block for the module; return True when the rule holds."""
    out(f"{module}  ({env_name(module)}=null)")
    if double is None:
        out("  FAIL: modules/%s/src exists but there is no null_double.* (every module ships one)" % module)
        return False
    present = files_present(root, module)
    with tempfile.NamedTemporaryFile(suffix=".null-double.xml", delete=False) as tmp:
        junit = Path(tmp.name)
    try:
        code = run_suite(root, module, junit)
        if code == 5 or not junit.exists() or junit.stat().st_size == 0:
            out(f"  FAIL: no conformance tests collected under modules/{module}/conformance (pytest exit {code})")
            return False
        counts = outcomes_by_file(junit)
    finally:
        junit.unlink(missing_ok=True)

    ok = True
    for stem in REQUIRED + OPTIONAL:
        if stem not in present:
            continue
        failed, total = counts.get(stem, (0, 0))
        if stem in OPTIONAL:
            verdict = "may pass"
        elif failed:
            verdict = "ok"
        else:
            verdict = "FAIL: the null double passes this file; it checks shape, not behaviour"
            ok = False
        out(f"  {stem:<16} {failed} of {total} failed   {verdict}")
    if not any(stem in present for stem in REQUIRED):
        out("  FAIL: none of test_errors, test_invariants, test_boundaries exists; nothing here can fail")
        ok = False
    out("  " + ("OK: suite discriminates" if ok else "FAIL: suite cannot fail against the null double"))
    return ok


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(argv[0]).resolve()
    modules = discover(root)
    if not modules:
        print(f"ERROR no modules with a src/ or a null double under {root / 'modules'}")
        return 1
    results = [check_module(root, m, d, print) for m, d in modules]
    bad = [m for (m, _), ok in zip(modules, results) if not ok]
    if bad:
        print(f"FAIL {len(bad)} of {len(modules)} module(s): {', '.join(bad)}")
        return 1
    print(f"OK {len(modules)} module(s); every conformance suite fails against its null double")
    return 0


if __name__ == "__main__":
    sys.exit(main())
