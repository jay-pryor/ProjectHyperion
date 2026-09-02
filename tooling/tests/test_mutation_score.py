"""mutation_score.py: parsing, scoring, row generation, and --write, without mutmut.

CORE-TST-002 rung 2. A canned mutants/ directory in the shape mutmut 3.x writes (a
.meta file with exit_code_by_key beside the mutated source carrying the __mutmut_orig
twin) stands in for a run, so these tests need neither mutmut nor a slow run. The
example project is the fixture for the record-store half.
"""

import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "minimal"
SCRIPT = ROOT / "tooling" / "mutation_score.py"

sys.path.insert(0, str(SCRIPT.parent))
import mutation_score  # noqa: E402

ORIGINAL = '''"""Internal."""
import hashlib


def _config_hash(config):
    canonical = repr(sorted(vars(config).items()))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def simulate(config):
    if not (0.0 < config.dt <= 0.1):
        raise ValueError("dt")
    return _config_hash(config)
'''

MUTATED = '''"""Internal."""
import hashlib
from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


def _config_hash(config):
    canonical = repr(sorted(vars(config).items()))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def x__config_hash__mutmut_orig(config):
    canonical = repr(sorted(vars(config).items()))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def x__config_hash__mutmut_1(config):
    canonical = None
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def x__config_hash__mutmut_2(config):
    canonical = repr(sorted(vars(config).items()))
    return hashlib.sha256(canonical.encode()).hexdigest()[:17]


def simulate(config):
    if not (0.0 < config.dt <= 0.1):
        raise ValueError("dt")
    return _config_hash(config)


def x_simulate__mutmut_orig(config):
    if not (0.0 < config.dt <= 0.1):
        raise ValueError("dt")
    return _config_hash(config)


def x_simulate__mutmut_1(config):
    if not (0.0 <= config.dt <= 0.1):
        raise ValueError("dt")
    return _config_hash(config)


def x_simulate__mutmut_2(config):
    if not (0.0 < config.dt <= 0.1):
        raise ValueError(None)
    return _config_hash(config)


def x_simulate__mutmut_3(config):
    if not (0.0 < config.dt <= 0.1):
        raise ValueError("dt")
    return None
'''

META = {
    "exit_code_by_key": {
        "modules.trajectory.src.integrator.x__config_hash__mutmut_1": 1,     # killed
        "modules.trajectory.src.integrator.x__config_hash__mutmut_2": 0,     # survived
        "modules.trajectory.src.integrator.x_simulate__mutmut_1": 0,         # survived
        "modules.trajectory.src.integrator.x_simulate__mutmut_2": 36,        # timeout: counts as killed
        "modules.trajectory.src.integrator.x_simulate__mutmut_3": 33,        # no tests: counts as survived
    },
    "hash_by_function_name": {}, "type_check_error_by_key": {},
    "durations_by_key": {}, "estimated_durations_by_key": {},
}


@pytest.fixture
def project(tmp_path):
    """A copy of the example whose trajectory source is the small ORIGINAL above."""
    dst = tmp_path / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "results.xml"))
    (dst / "modules" / "trajectory" / "src" / "integrator.py").write_text(ORIGINAL, encoding="utf-8")
    return dst


@pytest.fixture
def mutants(tmp_path):
    """A canned mutants/ directory in mutmut's layout."""
    src = tmp_path / "mutants" / "modules" / "trajectory" / "src"
    src.mkdir(parents=True)
    (src / "integrator.py").write_text(MUTATED, encoding="utf-8")
    (src / "integrator.py.meta").write_text(json.dumps(META), encoding="utf-8")
    return tmp_path / "mutants"


def cli(root, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args, str(root)], capture_output=True, text=True)


# ------------------------------------------------------------------ parsing and scoring

def test_parse_results_reads_every_mutant_with_its_status(mutants):
    found = mutation_score.parse_results(mutants, "trajectory")
    assert [(m.function, m.status) for m in found] == [
        ("_config_hash", "killed"), ("_config_hash", "survived"), ("simulate", "survived"),
        ("simulate", "timeout"), ("simulate", "no tests")]
    assert found[0].file == "modules/trajectory/src/integrator.py"
    assert found[2].ref == "modules/trajectory/src/integrator.py::x_simulate__mutmut_1"


def test_score_counts_timeout_as_killed_and_no_tests_as_survived(mutants):
    killed, survived, value = mutation_score.score(mutation_score.parse_results(mutants, "trajectory"))
    assert (killed, survived, value) == (2, 3, 0.4)


def test_describe_locates_the_changed_line_in_the_original(project, mutants):
    found = mutation_score.parse_results(mutants, "trajectory")
    m = mutation_score.describe(mutants, project, found[2])
    assert (m.line, m.before, m.after) == (11, "if not (0.0 < config.dt <= 0.1):", "if not (0.0 <= config.dt <= 0.1):")
    m = mutation_score.describe(mutants, project, found[1])
    assert m.line == 7 and m.after.endswith("[:17]")


# ------------------------------------------------------------------ rows

def test_survivor_rows_are_findings_with_hazard_severity(project, mutants):
    found = [mutation_score.describe(mutants, project, m) for m in mutation_score.parse_results(mutants, "trajectory")]
    survivors = [m for m in found if m.status in mutation_score.SURVIVED]
    rows, open_refs = mutation_score.survivor_rows(survivors, project, "SL-01", {"trajectory"}, "2026-09-02")
    assert [r["id"] for r in rows] == ["FND-004", "FND-005", "FND-006"]     # continues after the example's FND-003
    assert {r["source"] for r in rows} == {"mutation"} and {r["form"] for r in rows} == {"test"}
    assert {r["status"] for r in rows} == {"admitted"} and {r["severity"] for r in rows} == {"S1"}
    assert rows[1]["summary"] == ('Survived mutant at integrator.py:11 in simulate: '
                                  '"if not (0.0 < config.dt <= 0.1):" became "if not (0.0 <= config.dt <= 0.1):"')
    assert len(open_refs) == 3


def test_severity_is_s2_outside_hazard_modules(project, mutants):
    survivors = [m for m in mutation_score.parse_results(mutants, "trajectory") if m.status in mutation_score.SURVIVED]
    rows, _ = mutation_score.survivor_rows(survivors, project, "SL-01", {"atmosphere"}, "2026-09-02")
    assert {r["severity"] for r in rows} == {"S2"}


def test_rendered_row_round_trips_through_yaml():
    row = mutation_score.finding_row(
        mutation_score.Mutant("m.x_f__mutmut_1", "modules/m/src/f.py", "f", "survived", 3, 'a: "b"', "c: d"),
        4, "SL-01", set(), "2026-09-02")
    loaded = yaml.safe_load(mutation_score.render_row(row))
    assert loaded == [dict(row, date=dt.date(2026, 9, 2))]      # YAML reads the date as a date


# ------------------------------------------------------------------ CLI, print and write

def test_print_mode_writes_nothing(project, mutants):
    before = {p: p.read_text(encoding="utf-8") for p in (project / "trace").glob("*.yaml")}
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants))
    assert out.returncode == 0, out.stderr
    assert "mutation_score SL-01: 0.4  (2 killed, 3 survived, 0 other of 5)" in out.stdout
    assert "not written; pass --write" in out.stdout
    assert "- id: FND-004" in out.stdout
    assert {p: p.read_text(encoding="utf-8") for p in (project / "trace").glob("*.yaml")} == before


def test_write_appends_rows_sets_fields_and_is_idempotent(project, mutants):
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    assert out.returncode == 0, out.stderr
    findings = yaml.safe_load((project / "trace" / "findings.yaml").read_text(encoding="utf-8"))
    assert [f["id"] for f in findings[-3:]] == ["FND-004", "FND-005", "FND-006"]
    slices = {s["id"]: s for s in yaml.safe_load((project / "trace" / "slices.yaml").read_text(encoding="utf-8"))}
    assert slices["SL-01"]["mutation_score"] == 0.4 and slices["SL-01"]["survivors_triaged"] is False
    assert "mutation_score" not in slices["SL-02"]

    again = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    assert "survivors: 3, new rows: 0, already recorded: 3" in again.stdout
    assert len(yaml.safe_load((project / "trace" / "findings.yaml").read_text(encoding="utf-8"))) == 6


def test_write_marks_triaged_once_every_survivor_is_closed(project, mutants):
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    path = project / "trace" / "findings.yaml"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("  status: admitted\n  ref: modules/trajectory/src",
                                 "  status: rejected\n  reason: equivalent mutant\n  ref: modules/trajectory/src"),
                    encoding="utf-8")
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    assert "survivors_triaged True" in out.stdout
    slices = {s["id"]: s for s in yaml.safe_load((project / "trace" / "slices.yaml").read_text(encoding="utf-8"))}
    assert slices["SL-01"]["survivors_triaged"] is True


def test_module_mode_prints_a_placeholder_slice(project, mutants):
    out = cli(project, "--module", "trajectory", "--mutants", str(mutants))
    assert out.returncode == 0 and "slice: <SL-nn>" in out.stdout


def test_write_requires_a_slice_and_unknown_slice_is_an_error(project, mutants):
    assert cli(project, "--module", "trajectory", "--mutants", str(mutants), "--write").returncode == 2
    out = cli(project, "--slice", "SL-09", "--mutants", str(mutants))
    assert out.returncode == 1 and "SL-09 is not in trace/slices.yaml" in out.stderr


def test_config_restricts_mutation_and_tests_to_the_module():
    cfg = mutation_score.mutmut_config("trajectory")
    assert "only_mutate=modules/trajectory/src/*" in cfg
    assert "modules/trajectory/conformance\n    validation" in cfg
    assert "tests" not in cfg.replace("pytest_add_cli_args_test_selection", "")
