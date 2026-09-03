"""check_units.py against examples/minimal, green and deliberately broken.

CORE-CON-001. A unit in a NewType is erased at runtime, so the gate is the type check
and the question is whether that check is really running. Each broken copy defeats one
half: the clean run, or the probe that proves the run discriminates.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "minimal"
SCRIPT = ROOT / "tooling" / "check_units.py"

sys.path.insert(0, str(SCRIPT.parent))
import check_units  # noqa: E402

pytestmark = pytest.mark.skipif(
    subprocess.run([sys.executable, "-m", "mypy", "--version"], capture_output=True).returncode != 0,
    reason="mypy is not installed; CI installs it for the checks this file covers")


@pytest.fixture
def project(tmp_path):
    dst = tmp_path / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns(
        "__pycache__", ".mypy_cache", "results.xml"))
    return dst


def run(root):
    return subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)


def test_example_passes_and_probes_every_unit(project):
    out = run(project)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "units      5 type(s): Metres, Seconds, MetresPerSecond, Radians, KgPerM3" in out.stdout
    assert "21 file(s) checked, exit 0" in out.stdout
    assert "probe      5 deliberate unit confusion(s)" in out.stdout
    assert "FAIL" not in out.stdout
    assert not (project / check_units.PROBE).exists()          # the probe is removed either way


def test_a_real_unit_confusion_in_the_project_fails(project):
    # The defect the whole mechanism exists for: seconds handed to something wanting metres.
    path = project / "modules" / "trajectory" / "src" / "integrator.py"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "rho = atmosphere.density(Metres(y))", "rho = atmosphere.density(config.dt)"),
        encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert 'incompatible type "Seconds"; expected "Metres"' in out.stdout


def test_a_type_check_that_ignores_errors_fails_the_probe(project):
    # Passes the clean half vacuously. The probe is what catches it.
    path = project / "mypy.ini"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "[mypy]\n", "[mypy]\nignore_errors = True\n"), encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "FAIL: accepted" in out.stdout
    assert "units are documented in the type but not enforced by one" in out.stdout


def test_a_configuration_that_checks_no_files_fails(project):
    # Excluding the sources is how a type-check step ends up proving nothing while
    # looking green in the log. mypy reports it, and the file count is reported too.
    (project / "mypy.ini").write_text("[mypy]\nexclude = .\n", encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "0 file(s) checked" in out.stdout


def test_a_clean_run_over_zero_files_proves_nothing(monkeypatch, project):
    # The same shape, but with mypy exiting 0: the count is the only thing separating a
    # real pass from a vacuous one, so the guard is asserted directly.
    monkeypatch.setattr(check_units, "mypy",
                        lambda root, targets: (0, "Success: no issues found in 0 source files"))
    lines = []
    assert check_units.check(project, lines.append) is False
    assert "  FAIL: the run checked no files, so it proved nothing" in lines


def test_plain_aliases_are_not_unit_types(project):
    # `Metres = float` reads like a unit type and enforces nothing; there is no NewType
    # to probe, so the script says so rather than passing.
    (project / "baseline" / "units.py").write_text(
        "Metres = float\nSeconds = float\n", encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "baseline/units.py defines no NewType" in out.stdout


def test_probe_covers_the_base_type_and_one_sibling_per_base():
    units = [("Metres", "float"), ("Seconds", "float"), ("Count", "int")]
    source, expected = check_units.probe_source(units)
    assert "from baseline.units import Metres, Seconds, Count" in source
    assert [what for _, what in expected] == [
        "bare float accepted where Metres was expected",
        "Seconds accepted where Metres was expected",
        "bare int accepted where Count was expected",
    ]
    for line, _ in expected:
        assert source.splitlines()[line - 1].startswith("_takes_")


def test_unit_types_reads_only_newtype_assignments(project):
    (project / "baseline" / "units.py").write_text(
        'from typing import NewType\n\n'
        'Metres = NewType("Metres", float)\n'
        'MAX = 10.0\n'
        'Alias = float\n', encoding="utf-8")
    assert check_units.unit_types(project) == [("Metres", "float")]
