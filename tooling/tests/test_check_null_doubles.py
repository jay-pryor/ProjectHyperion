"""check_null_doubles.py against examples/minimal, green and deliberately broken.

CORE-TST-002 rung 1. The example is the fixture (M5): both its modules ship a null
double and both suites fail against it. Each broken copy defeats exactly one rule.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "minimal"
SCRIPT = ROOT / "tooling" / "check_null_doubles.py"

sys.path.insert(0, str(SCRIPT.parent))
import check_null_doubles  # noqa: E402


@pytest.fixture
def project(tmp_path):
    dst = tmp_path / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "results.xml"))
    return dst


def run(root):
    return subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)


def test_env_name_uppercases_and_normalises():
    assert check_null_doubles.env_name("atmosphere") == "ATMOSPHERE_IMPL"
    assert check_null_doubles.env_name("range-table") == "RANGE_TABLE_IMPL"


def test_example_passes_per_module(project):
    out = run(project)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "atmosphere  (ATMOSPHERE_IMPL=null)" in out.stdout
    assert "trajectory  (TRAJECTORY_IMPL=null)" in out.stdout
    assert out.stdout.count("OK: suite discriminates") == 2
    assert out.stdout.strip().endswith("OK 2 module(s); every conformance suite fails against its null double")
    assert not (project / "trace" / "results.xml").exists()      # the real results file is untouched


def test_null_double_that_satisfies_the_suite_fails_the_check(project):
    # The double delegates to the real implementation: the suite passes, so it proves nothing.
    (project / "modules" / "atmosphere" / "null_double.py").write_text(
        "from modules.atmosphere.src.exponential import density  # noqa: F401\n", encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "test_errors      0 of 3 failed   FAIL: the null double passes this file" in out.stdout
    assert "FAIL 1 of 2 module(s): atmosphere" in out.stdout
    assert "trajectory  (TRAJECTORY_IMPL=null)" in out.stdout      # the other module still reported


def test_one_required_file_passing_is_enough_to_fail(project):
    # Make the double honour the envelope but nothing else: errors fail no longer, the rest still do.
    (project / "modules" / "atmosphere" / "null_double.py").write_text(
        "from baseline.units import KgPerM3, Metres\n"
        "from modules.atmosphere.contract import ENVELOPE_MAX, ENVELOPE_MIN, EnvelopeError\n\n"
        "def density(altitude: Metres) -> KgPerM3:\n"
        "    if not (ENVELOPE_MIN <= altitude <= ENVELOPE_MAX):\n"
        "        raise EnvelopeError(altitude)\n"
        "    return KgPerM3(1.225)\n", encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "test_errors      0 of 3 failed   FAIL" in out.stdout
    assert "test_invariants  1 of 2 failed   ok" in out.stdout


def test_module_with_src_and_no_null_double_is_an_error(project):
    (project / "modules" / "trajectory" / "null_double.py").unlink()
    out = run(project)
    assert out.returncode == 1
    assert "modules/trajectory/src exists but there is no null_double.*" in out.stdout


def test_double_not_selected_by_the_variable_fails(project):
    # contract.py ignores TRAJECTORY_IMPL: the real implementation runs and the suite passes.
    surface = project / "modules" / "trajectory" / "contract.py"
    surface.write_text(surface.read_text(encoding="utf-8").replace(
        'os.environ.get("TRAJECTORY_IMPL") == "null"', "False"), encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "FAIL 1 of 2 module(s): trajectory" in out.stdout


def test_outcomes_by_file_counts_failures_and_errors(tmp_path):
    junit = tmp_path / "r.xml"
    junit.write_text(
        '<testsuites><testsuite><testcase classname="modules.m.conformance.test_errors" name="a"><failure/></testcase>'
        '<testcase classname="modules.m.conformance.test_errors" name="b"><error/></testcase>'
        '<testcase classname="modules.m.conformance.test_errors" name="c"/>'
        '<testcase classname="modules.m.conformance.test_operations" name="d"/></testsuite></testsuites>',
        encoding="utf-8")
    assert check_null_doubles.outcomes_by_file(junit) == {"test_errors": (2, 3), "test_operations": (0, 1)}
