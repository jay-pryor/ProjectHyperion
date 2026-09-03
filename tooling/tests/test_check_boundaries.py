"""check_boundaries.py against examples/minimal, green and deliberately broken.

CORE-CON-003. The example is the fixture (M5): two modules, one manifest each, one
real edge between them. Each broken copy defeats exactly one of the four rules, so a
rule that stops firing fails a test here rather than passing silently in a project.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "minimal"
SCRIPT = ROOT / "tooling" / "check_boundaries.py"

sys.path.insert(0, str(SCRIPT.parent))
import check_boundaries  # noqa: E402


@pytest.fixture
def project(tmp_path):
    dst = tmp_path / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "results.xml"))
    return dst


def run(root):
    return subprocess.run([sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True)


def edit(path, old, new):
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{path.name} no longer contains {old!r}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_example_passes_and_reports_every_edge(project):
    out = run(project)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "atmosphere  1 import(s): baseline/units" in out.stdout
    assert ("trajectory  3 import(s): baseline/faults, baseline/units, "
            "modules/atmosphere/contract") in out.stdout
    assert out.stdout.strip().endswith(
        "OK 2 module(s); the import graph matches the manifests and is acyclic")


def test_reaching_another_modules_src_fails(project):
    edit(project / "modules" / "trajectory" / "src" / "integrator.py",
         "from modules.atmosphere import contract as atmosphere",
         "from modules.atmosphere.src import exponential as atmosphere")
    out = run(project)
    assert out.returncode == 1
    assert "reaches into atmosphere's internals (src/exponential)" in out.stdout


def test_production_code_may_not_import_another_suite(project):
    edit(project / "modules" / "trajectory" / "src" / "integrator.py",
         "from modules.atmosphere import contract as atmosphere",
         "from modules.atmosphere import contract as atmosphere\n"
         "from modules.atmosphere.conformance import test_boundaries  # noqa: F401")
    out = run(project)
    assert out.returncode == 1
    assert "imports atmosphere's conformance suite from production code" in out.stdout


def test_test_code_may_import_another_suite(project):
    # validation/ already reuses trajectory's scenario builders; that is the promised half
    # of the contract (CORE-CON-001) and must stay legal.
    text = (project / "validation" / "envelope" / "test_envelope.py").read_text(encoding="utf-8")
    assert "from modules.trajectory.conformance._scenarios import vacuum" in text
    assert run(project).returncode == 0


def test_import_the_manifest_does_not_list_fails(project):
    manifest = project / "modules" / "trajectory" / "manifest.yaml"
    edit(manifest, "  - baseline/faults\n", "")
    out = run(project)
    assert out.returncode == 1
    assert "imports baseline/faults, which modules/trajectory/manifest.yaml does not list" in out.stdout


def test_manifest_entry_nothing_imports_fails(project):
    manifest = project / "modules" / "atmosphere" / "manifest.yaml"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "  - baseline/logging\n",
                        encoding="utf-8")
    out = run(project)
    assert out.returncode == 1
    assert "declares baseline/logging, which no file in the module imports" in out.stdout


def test_cycle_between_modules_fails(project):
    edit(project / "modules" / "atmosphere" / "src" / "exponential.py",
         "from baseline.units import KgPerM3, Metres",
         "from baseline.units import KgPerM3, Metres\n"
         "from modules.trajectory.contract import ScenarioConfig  # noqa: F401")
    edit(project / "modules" / "atmosphere" / "manifest.yaml",
         "  - baseline/units\n", "  - baseline/units\n  - modules/trajectory/contract\n")
    out = run(project)
    assert out.returncode == 1
    assert "circular dependency: atmosphere -> trajectory -> atmosphere" in out.stdout


def test_baseline_importing_a_module_fails(project):
    edit(project / "baseline" / "units.py", "from typing import NewType",
         "from typing import NewType\n"
         "from modules.atmosphere.contract import ENVELOPE_MAX  # noqa: F401")
    out = run(project)
    assert out.returncode == 1
    assert "baseline is the substrate every module inherits and cannot depend on one" in out.stdout


def test_module_without_a_manifest_fails(project):
    (project / "modules" / "atmosphere" / "manifest.yaml").unlink()
    out = run(project)
    assert out.returncode == 1
    assert "modules/atmosphere: no manifest.yaml" in out.stdout


def test_cycles_finds_every_component():
    uses = {"a": {"modules/b/contract": 1}, "b": {"modules/c/contract": 1},
            "c": {"modules/a/contract": 1},
            "x": {"modules/y/contract": 1}, "y": {"modules/x/contract": 1},
            "z": {"baseline/units": 1}}
    assert check_boundaries.cycles(uses) == ["a -> b -> c -> a", "x -> y -> x"]
    assert check_boundaries.cycles({"a": {"modules/b/contract": 1}, "b": {}}) == []


def test_from_package_import_module_resolves_to_the_module(project):
    imports = check_boundaries.internal_imports(
        project, project / "modules" / "trajectory" / "src" / "integrator.py")
    # `from modules.atmosphere import contract as atmosphere` is an import of the contract,
    # not of the package; resolving it as the package would hide every surface violation.
    assert "modules/atmosphere/contract" in imports
    assert "modules/atmosphere" not in imports
