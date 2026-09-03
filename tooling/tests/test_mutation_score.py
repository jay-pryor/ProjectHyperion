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
    """A copy of the example wound back to the moment before rung 2 first ran: the small
    ORIGINAL above as its trajectory source, its mutation triage removed, and SL-01
    carrying no acceptance record. What is under test is the tool, not the example."""
    dst = tmp_path / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "results.xml"))
    (dst / "modules" / "trajectory" / "src" / "integrator.py").write_text(ORIGINAL, encoding="utf-8")
    findings = dst / "trace" / "findings.yaml"
    findings.write_text(findings.read_text(encoding="utf-8").split("- id: FND-004")[0], encoding="utf-8")
    slices = dst / "trace" / "slices.yaml"
    slices.write_text(slices.read_text(encoding="utf-8")
                      .replace("  mutation_score: {trajectory: 0.762}\n", "")
                      .replace("  survivors_triaged: true\n", ""),
                      encoding="utf-8")
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

def test_survivor_rows_are_admitted_findings(project, mutants):
    found = [mutation_score.describe(mutants, project, m) for m in mutation_score.parse_results(mutants, "trajectory")]
    survivors = [m for m in found if m.status in mutation_score.SURVIVED]
    rows, open_refs = mutation_score.survivor_rows(survivors, project, "SL-01", "2026-09-02")
    assert [r["id"] for r in rows] == ["FND-004", "FND-005", "FND-006"]     # continues after the example's FND-003
    assert {r["source"] for r in rows} == {"mutation"} and {r["form"] for r in rows} == {"test"}
    assert {r["status"] for r in rows} == {"admitted"}
    assert rows[1]["summary"] == ('Survived mutant at integrator.py:11 in simulate: '
                                  '"if not (0.0 < config.dt <= 0.1):" became "if not (0.0 <= config.dt <= 0.1):"')
    assert len(open_refs) == 3


def test_severity_is_s2_only_where_a_hazard_names_the_module(project):
    """The whole rule: the register decides, not the tool. HZ-002's mitigation_contract
    names trajectory, so its survivors block; a module no hazard names is S3 backlog
    (CORE-TST-002 rung 2). Nothing here can move a module between the two."""
    hazards = yaml.safe_load((project / "trace" / "hazards.yaml").read_text(encoding="utf-8"))
    named = mutation_score.hazard_named_modules(hazards)
    assert named == {"trajectory", "atmosphere"}
    assert mutation_score.severity_for("trajectory", named) == "S2"
    assert mutation_score.severity_for("range_table", named) == "S3"
    assert mutation_score.hazard_named_modules([{"mitigation_contract": "TBD"}]) == set()


def test_the_same_survivor_is_s2_or_s3_by_module_alone(project, mutants):
    survivors = [m for m in mutation_score.parse_results(mutants, "trajectory") if m.status in mutation_score.SURVIVED]
    s2, _ = mutation_score.survivor_rows(survivors, project, "SL-01", "2026-09-02", "S2")
    s3, _ = mutation_score.survivor_rows(survivors, project, "SL-01", "2026-09-02", "S3")
    assert {r["severity"] for r in s2} == {"S2"} and {r["severity"] for r in s3} == {"S3"}
    assert [r["ref"] for r in s2] == [r["ref"] for r in s3]     # the same mutants, either way


# ------------------------------------------------------------------ the floor

def test_the_floor_is_the_best_any_other_accepted_slice_earned():
    slices = [{"id": "SL-01", "status": "accepted", "mutation_score": {"trajectory": 0.7}},
              {"id": "SL-02", "status": "accepted", "mutation_score": {"trajectory": 0.8, "atmosphere": 0.5}},
              {"id": "SL-03", "status": "in_progress", "mutation_score": {"trajectory": 0.9}}]
    assert mutation_score.derived_floor(slices, "trajectory") == 0.8
    assert mutation_score.derived_floor(slices, "trajectory", exclude="SL-02") == 0.7
    assert mutation_score.derived_floor(slices, "atmosphere", exclude="SL-02") is None   # first measurement
    assert mutation_score.derived_floor(slices, "never_measured") is None
    assert mutation_score.derived_floor([{"id": "SL-01", "status": "accepted",
                                          "mutation_score": 0.9}], "trajectory") is None


def test_a_mutant_rejected_for_one_slice_is_raised_again_for_another(project, mutants):
    """Rejecting a mutant as equivalent settles it under the promises one slice claimed.
    SL-02 names trajectory too, and gets its own row rather than the earlier verdict."""
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    path = project / "trace" / "findings.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "  status: admitted\n  ref: modules/trajectory/src",
        "  status: rejected\n  reason: equivalent mutant\n  ref: modules/trajectory/src"), encoding="utf-8")
    survivors = [m for m in mutation_score.parse_results(mutants, "trajectory") if m.status in mutation_score.SURVIVED]
    assert mutation_score.survivor_rows(survivors, project, "SL-01", "2026-09-02")[0] == []
    rows, _ = mutation_score.survivor_rows(survivors, project, "SL-02", "2026-09-02")
    assert [r["slice"] for r in rows] == ["SL-02"] * 3


def test_rendered_row_round_trips_through_yaml():
    row = mutation_score.finding_row(
        mutation_score.Mutant("m.x_f__mutmut_1", "modules/m/src/f.py", "f", "survived", 3, 'a: "b"', "c: d"),
        4, "SL-01", "2026-09-02", "S2")
    loaded = yaml.safe_load(mutation_score.render_row(row))
    assert loaded == [dict(row, date=dt.date(2026, 9, 2))]      # YAML reads the date as a date


# ------------------------------------------------------------------ CLI, print and write

def test_print_mode_writes_nothing(project, mutants):
    before = {p: p.read_text(encoding="utf-8") for p in (project / "trace").glob("*.yaml")}
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants))
    assert out.returncode == 0, out.stderr
    assert "mutation_score SL-01/trajectory: 0.4  (2 killed, 3 survived, 0 other of 5)" in out.stdout
    assert "3 survivor(s) at S2, 3 new row(s)" in out.stdout
    assert "not written; pass --write" in out.stdout
    assert "- id: FND-004" in out.stdout
    assert {p: p.read_text(encoding="utf-8") for p in (project / "trace").glob("*.yaml")} == before


def test_write_appends_rows_sets_fields_and_is_idempotent(project, mutants):
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    assert out.returncode == 0, out.stderr
    findings = yaml.safe_load((project / "trace" / "findings.yaml").read_text(encoding="utf-8"))
    assert [f["id"] for f in findings[-3:]] == ["FND-004", "FND-005", "FND-006"]
    slices = {s["id"]: s for s in yaml.safe_load((project / "trace" / "slices.yaml").read_text(encoding="utf-8"))}
    assert slices["SL-01"]["mutation_score"] == {"trajectory": 0.4}
    assert slices["SL-01"]["survivors_triaged"] is False
    assert "mutation_score" not in slices["SL-02"]

    again = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    assert "0 new row(s)" in again.stdout
    assert len(yaml.safe_load((project / "trace" / "findings.yaml").read_text(encoding="utf-8"))) == 6


def test_write_records_nothing_for_a_module_no_hazard_names_but_triage_does(project, mutants):
    """The gate change, end to end: without a hazard on the module the survivors are S3
    and --write leaves them unfiled, so acceptance is not blocked by a script's output.
    They are still printed, and --triage files them when someone wants the worklist."""
    path = project / "trace" / "hazards.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "modules/trajectory/CONTRACT.md::C-103", "modules/atmosphere/CONTRACT.md::C-003"), encoding="utf-8")

    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    assert out.returncode == 0, out.stderr
    assert "3 survivor(s) at S3" in out.stdout and "backlog; --triage to record them" in out.stdout
    assert "- id: FND-004" in out.stdout                       # printed, never invisible
    findings = yaml.safe_load((project / "trace" / "findings.yaml").read_text(encoding="utf-8"))
    assert [f["id"] for f in findings] == ["FND-001", "FND-002", "FND-003"]
    slices = {s["id"]: s for s in yaml.safe_load((project / "trace" / "slices.yaml").read_text(encoding="utf-8"))}
    assert slices["SL-01"]["mutation_score"] == {"trajectory": 0.4}
    assert "survivors_triaged" not in slices["SL-01"]          # nothing here gates on it

    triaged = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--triage", "trajectory")
    assert triaged.returncode == 0, triaged.stderr
    findings = yaml.safe_load((project / "trace" / "findings.yaml").read_text(encoding="utf-8"))
    assert [f["id"] for f in findings[-3:]] == ["FND-004", "FND-005", "FND-006"]
    assert {f["severity"] for f in findings[-3:]} == {"S3"}
    assert "slice fields untouched" in triaged.stdout


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


# ------------------------------------------------------------------ a run that measured nothing

def test_a_run_with_no_mutant_is_an_error_not_a_score_of_zero(project, tmp_path):
    """The failure this prevents: a toolchain whose output this parser no longer
    understands yields no mutants, score() divides nothing by nothing and returns 0.0,
    and --write records a clean triaged slice for a measurement that never ran."""
    empty = tmp_path / "empty" / "modules" / "trajectory" / "src"
    empty.mkdir(parents=True)
    out = cli(project, "--slice", "SL-01", "--mutants", str(empty.parents[2]))
    assert out.returncode == 1
    assert "no mutant was found" in out.stderr
    slices = {s["id"]: s for s in yaml.safe_load((project / "trace" / "slices.yaml").read_text(encoding="utf-8"))}
    assert "mutation_score" not in slices["SL-01"]


def test_a_mutmut_major_this_parser_has_not_read_is_refused(monkeypatch):
    from importlib import metadata
    monkeypatch.setattr(metadata, "version", lambda name: "4.0.1")
    with pytest.raises(SystemExit) as e:
        mutation_score.check_mutmut_version()
    assert "mutmut 4.0.1 is installed" in str(e.value)
    monkeypatch.setattr(metadata, "version", lambda name: f"{mutation_score.MUTMUT_MAJOR}.7.0")
    assert mutation_score.check_mutmut_version().startswith(f"{mutation_score.MUTMUT_MAJOR}.")


# ------------------------------------------------------------------ --check

def score_of(project):
    slices = yaml.safe_load((project / "trace" / "slices.yaml").read_text(encoding="utf-8"))
    return {s["id"]: s for s in slices}["SL-01"]


def test_check_needs_a_recorded_score(project, mutants):
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--check")
    assert out.returncode == 1 and "carries no mutation_score" in out.stdout


def test_check_passes_once_the_record_matches_what_is_measured(project, mutants):
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--check")
    assert out.returncode == 0, out.stdout
    assert "trajectory measured 0.4, recorded 0.4, no floor yet" in out.stdout
    assert "every S2 survivor recorded" in out.stdout


def test_check_fails_when_the_recorded_score_is_no_longer_earned(project, mutants):
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    path = project / "trace" / "slices.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("{trajectory: 0.4}", "{trajectory: 0.9}"),
                    encoding="utf-8")
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--check")
    assert out.returncode == 1 and "trajectory measured 0.4, below the recorded 0.9" in out.stdout


def test_check_rejects_the_old_scalar_form(project, mutants):
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    path = project / "trace" / "slices.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("{trajectory: 0.4}", "0.4"), encoding="utf-8")
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--check")
    assert out.returncode == 1 and "records mutation_score as a single number" in out.stdout


def test_check_fails_below_the_floor_an_earlier_slice_earned(project, mutants):
    """The ratchet, which is the whole gate for a module no hazard names: SL-02 names
    trajectory too, and an accepted SL-02 at 0.9 is the bar SL-01 must now clear."""
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    path = project / "trace" / "slices.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace(
        "  status: in_progress\n", "  status: accepted\n  mutation_score: {trajectory: 0.9}\n", 1),
        encoding="utf-8")
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--check")
    assert out.returncode == 1
    assert "trajectory measured 0.4, below the 0.9 an accepted slice already earned" in out.stdout


def test_check_fails_on_a_survivor_with_no_findings_row(project, mutants):
    cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--write")
    path = project / "trace" / "findings.yaml"
    rows = path.read_text(encoding="utf-8").split("- id: FND-006")
    path.write_text(rows[0], encoding="utf-8")                 # drop the last survivor's row
    out = cli(project, "--slice", "SL-01", "--mutants", str(mutants), "--check")
    assert out.returncode == 1 and "1 S2 survivor(s) have no findings row" in out.stdout
