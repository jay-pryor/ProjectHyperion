"""check_traces.py against examples/minimal, green and deliberately broken.

The example project is the fixture (M5). Each test below copies it, breaks exactly one
rule from CORE-TRC-002 or CORE-TRC-003, and asserts the checker names the break. A rule
with no test here is a rule the checker may silently stop enforcing.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "minimal"
CHECKER = ROOT / "tooling" / "check_traces.py"

sys.path.insert(0, str(CHECKER.parent))
import check_traces  # noqa: E402


# ------------------------------------------------------------------ fixtures

@pytest.fixture(scope="session")
def green(tmp_path_factory):
    """A copy of the example with a fresh trace/results.xml from its own test run."""
    dst = tmp_path_factory.mktemp("green") / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "results.xml"))
    run = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=dst, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert (dst / "trace" / "results.xml").exists()
    return dst


@pytest.fixture
def broken(green, tmp_path):
    """A private copy of the green project to mutate."""
    dst = tmp_path / "minimal"
    shutil.copytree(green, dst)
    return dst


def edit(root, rel, old, new, count=1):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert text.count(old) >= count, f"{rel}: {old!r} not found"
    path.write_text(text.replace(old, new), encoding="utf-8")


def errors(root):
    return [str(i) for i in check_traces.check(check_traces.load(root)) if i.level == "error"]


def cli(root, *args):
    return subprocess.run([sys.executable, str(CHECKER), "--root", str(root), *args],
                          capture_output=True, text=True)


def assert_error(root, *needles):
    errs = errors(root)
    for needle in needles:
        assert any(needle in e for e in errs), f"expected an error containing {needle!r}, got:\n" + "\n".join(errs)


# ------------------------------------------------------------------ green

def test_example_is_green(green):
    assert errors(green) == []
    run = cli(green)
    assert run.returncode == 0, run.stderr
    assert run.stdout.startswith("OK ")


def test_report_exits_zero_and_leads_with_verdict(green):
    run = cli(green, "--report")
    assert run.returncode == 0
    assert run.stdout.startswith("# Trace Matrix\n\nChain intact: 0 errors.")
    for heading in ("## Requirements", "## Hazards", "## Slices", "## Findings", "## Reviews"):
        assert heading in run.stdout


def test_strict_flag_is_deprecated_not_fatal(green):
    run = cli(green, "--strict")
    assert run.returncode == 0
    assert "strictness now comes from the gate record" in run.stderr


def test_parametrised_family_resolves_to_all_members(green):
    project = check_traces.load(green)
    members = project.find_tests("validation/analytical/test_vacuum_range.py::test_range_matches_closed_form")
    assert len(members) == 3 and set(members.values()) == {"passed"}


# ------------------------------------------------------------------ requirements (F-08, F-11, F-12)

def test_functional_requirement_allocated_to_unknown_module(broken):
    edit(broken, "trace/requirements.yaml", "allocated_to: atmosphere\n", "allocated_to: atmosfere\n")
    assert_error(broken, "allocated_to 'atmosfere' is not a module")


def test_functional_requirement_may_not_list_modules(broken):
    edit(broken, "trace/requirements.yaml", "allocated_to: atmosphere\n", "allocated_to: [atmosphere, trajectory]\n")
    assert_error(broken, "REQ-001: functional requirement must be allocated to exactly one module")


def test_proposed_requirement_is_an_error_after_g3(broken):
    edit(broken, "trace/requirements.yaml",
         "  validated_by: validation/envelope/test_envelope.py::test_apex_beyond_envelope_is_rejected\n  status: traced\n",
         "  validated_by: TBD\n  status: proposed\n")
    assert_error(broken, "REQ-003: still proposed after G3 passed")


def test_tbd_after_g3_is_a_warning_before_g3(broken):
    edit(broken, "trace/requirements.yaml",
         "  validated_by: validation/envelope/test_envelope.py::test_apex_beyond_envelope_is_rejected\n  status: traced\n",
         "  validated_by: TBD\n  status: proposed\n")
    edit(broken, "trace/reviews.yaml", "  gate: G3\n  date: 2026-08-16\n  reviewer: self; specification-review on opus\n  disposition: passed\n",
         "  gate: G3\n  date: 2026-08-16\n  reviewer: self; specification-review on opus\n  disposition: pending\n")
    # SL-02 is in_progress, so REQ-003 proposed is fine before G3; but SL-01 is accepted
    # and its claims are all verified, so the only errors must be none.
    issues = check_traces.check(check_traces.load(broken))
    assert [str(i) for i in issues if i.level == "error"] == []
    assert any("REQ-003: validated_by is TBD" in str(i) for i in issues if i.level == "warning")


def test_unit_test_cannot_verify_a_requirement(broken):
    edit(broken, "trace/requirements.yaml",
         "modules/atmosphere/conformance/test_operations.py::test_sea_level_density_C001",
         "modules/atmosphere/tests/test_internal.py::test_scale_height_gives_one_over_e")
    assert_error(broken, "REQ-001", "unit tests are model-owned and cannot verify")


def test_renamed_test_breaks_the_trace(broken):
    edit(broken, "trace/requirements.yaml", "test_sea_level_density_C001", "test_sea_level_density_C000")
    assert_error(broken, "REQ-001", "not in trace/results.xml")


def test_failed_traced_test_is_an_error(broken):
    results = broken / "trace" / "results.xml"
    text = results.read_text(encoding="utf-8")
    new, n = re.subn(r'(<testcase classname="modules.trajectory.conformance.test_operations" '
                     r'name="test_provenance_present_C103"[^>]*?)\s*/>',
                     r'\1><failure message="forced"/></testcase>', text)
    assert n == 1
    results.write_text(new, encoding="utf-8")
    assert_error(broken, "REQ-004: traced test did not pass", "HZ-002: traced test did not pass")


def test_parametrised_member_failure_breaks_the_family(broken):
    results = broken / "trace" / "results.xml"
    text = results.read_text(encoding="utf-8")
    new, n = re.subn(r'(<testcase classname="validation.analytical.test_vacuum_range" '
                     r'name="test_range_matches_closed_form\[45.0\]"[^>]*?)\s*/>',
                     r'\1><skipped type="pytest.xfail" message="x"/></testcase>', text)
    assert n == 1
    results.write_text(new, encoding="utf-8")
    assert_error(broken, "REQ-002: traced test did not pass", "[45.0] xfailed")


def test_missing_results_file_is_fatal(broken):
    (broken / "trace" / "results.xml").unlink()
    assert_error(broken, "trace/results.xml: missing")


def test_unclaimed_requirement_is_an_error_after_g3(broken):
    edit(broken, "trace/slices.yaml", "requirements: [REQ-001, REQ-003]", "requirements: [REQ-001]")
    assert_error(broken, "REQ-003: not claimed by any slice")


# ------------------------------------------------------------------ hazards (F-09, F-10, F-28)

def test_unresolved_contract_clause(broken):
    edit(broken, "trace/hazards.yaml", "CONTRACT.md::C-003", "CONTRACT.md::C-999")
    assert_error(broken, "HZ-001: clause 'C-999' is not a marked clause")


def test_unresolved_contract_path(broken):
    edit(broken, "trace/hazards.yaml", "modules/atmosphere/CONTRACT.md::C-003", "modules/weather/CONTRACT.md::C-003")
    assert_error(broken, "HZ-001: contract path 'modules/weather/CONTRACT.md' does not exist")


def test_hazard_without_requirement(broken):
    edit(broken, "trace/hazards.yaml", "  requirement: REQ-003\n", "")
    assert_error(broken, "HZ-001: missing required field 'requirement'")


def test_hazard_failure_mode_validated_against_g0(broken):
    edit(broken, "trace/hazards.yaml", "failure_mode: failed_silently", "failure_mode: silently_failed")
    assert_error(broken, "HZ-001: failure_mode 'silently_failed' invalid")


def test_org_register_requires_org_fields_and_forbids_assessment(broken):
    edit(broken, "trace/hazards.yaml", "- id: HZ-001\n  register: local\n", "- id: HZ-001\n  register: org\n")
    assert_error(broken, "HZ-001: register org requires 'org_hazard_id'", "HZ-001: register org requires 'org_system'",
                 "HZ-001: register org forbids 'severity'")


def test_verified_mitigation_needs_a_passing_test(broken):
    edit(broken, "trace/hazards.yaml", "test_above_envelope_raises_C003\n  mitigation_status: traced",
         "test_above_envelope_raises_C003\n  mitigation_status: verified")
    assert errors(broken) == []      # it passes, so verified is earned
    edit(broken, "trace/hazards.yaml", "mitigation_test: modules/atmosphere/conformance/test_errors.py::test_above_envelope_raises_C003",
         "mitigation_test: TBD")
    assert_error(broken, "HZ-001: mitigation_test is TBD; permitted only while proposed")


# ------------------------------------------------------------------ slices (F-11)

def test_accepted_slice_may_claim_only_verified(broken):
    edit(broken, "trace/slices.yaml", "requirements: [REQ-002, REQ-004, REQ-005, REQ-006]",
         "requirements: [REQ-002, REQ-003, REQ-004, REQ-005, REQ-006]")
    assert_error(broken, "SL-01: accepted but claims REQ-003, which is traced, not verified")


def test_acceptance_record_fields_are_typed(broken):
    edit(broken, "trace/slices.yaml", "  mutation_score: {trajectory: 0.762}\n  survivors_triaged: true\n",
         "  mutation_score: {trajectory: 87}\n  survivors_triaged: yes\n")
    errs = errors(broken)
    assert any("mutation_score[trajectory] must be a number from 0 to 1" in e for e in errs)
    assert not any("survivors_triaged" in e for e in errs)     # yaml `yes` is a bool


def test_the_score_is_a_mapping_of_module_to_score(broken):
    """A slice names several modules and rung 2 measures one at a time, so a single
    number cannot say which module earned it (CORE-TRC-002)."""
    edit(broken, "trace/slices.yaml", "  mutation_score: {trajectory: 0.762}\n", "  mutation_score: 0.762\n")
    assert_error(broken, "SL-01: mutation_score must be a mapping of module to score")
    edit(broken, "trace/slices.yaml", "  mutation_score: 0.762\n", "  mutation_score: {atmosphere: 0.9}\n")
    assert_error(broken, "SL-01: mutation_score names 'atmosphere', which contracts: does not")


def test_accepted_slice_without_a_mutation_score_is_an_error(broken):
    """CORE-TST-002 rung 2 is an acceptance record, not advice. Without this the absence
    of the field is indistinguishable from a suite that killed every mutant."""
    edit(broken, "trace/slices.yaml", "  mutation_score: {trajectory: 0.762}\n", "")
    assert_error(broken, "SL-01: accepted with no mutation_score")
    edit(broken, "trace/slices.yaml", "  status: accepted\n", "  status: in_progress\n")
    assert not any("mutation_score" in e for e in errors(broken))    # only acceptance demands it


def test_accepted_slice_needs_an_entry_for_every_module_it_names(broken):
    edit(broken, "trace/slices.yaml", "  contracts: [trajectory]\n  status: accepted\n",
         "  contracts: [trajectory, atmosphere]\n  status: accepted\n")
    assert_error(broken, "SL-01: accepted with no mutation_score for atmosphere, which its contracts: names")


def test_a_score_below_what_an_earlier_accepted_slice_earned_is_an_error(broken):
    """The ratchet. No constant is compared against: the bar is what this module already
    reached on an accepted slice, so a suite that weakens is visible (CORE-TST-002 rung 2)."""
    edit(broken, "trace/slices.yaml", "  contracts: [atmosphere, trajectory]\n  status: in_progress\n",
         "  contracts: [atmosphere, trajectory]\n  status: accepted\n"
         "  mutation_score: {atmosphere: 0.5, trajectory: 0.9}\n  survivors_triaged: true\n")
    assert_error(broken, "SL-01: mutation_score[trajectory] is 0.762, below the 0.9 an accepted "
                         "slice already earned for it")


def test_a_first_measurement_has_no_floor_to_clear(broken):
    # atmosphere has never been measured, so any score it records is its own bar.
    edit(broken, "trace/slices.yaml", "  contracts: [trajectory]\n  status: accepted\n",
         "  contracts: [trajectory, atmosphere]\n  status: accepted\n")
    edit(broken, "trace/slices.yaml", "  mutation_score: {trajectory: 0.762}\n",
         "  mutation_score: {trajectory: 0.762, atmosphere: 0.1}\n")
    assert errors(broken) == []


# ------------------------------------------------------------------ targeted reads (CORE-REV-004)

# REV-005 is SL-01's targeted read: kind targeted_read, slice SL-01, disposition no_findings.
# SL-02 is in_progress and its read (REV-007) sits at pending, which is legal and stays so.

def test_accepted_slice_with_no_targeted_read(broken):
    edit(broken, "trace/reviews.yaml", "  kind: targeted_read\n  slice: SL-01\n", "  kind: targeted_read\n")
    assert_error(broken, "SL-01: accepted with no completed targeted read",
                 "record a targeted_read review row naming the slice (CORE-REV-004)")


def test_accepted_slice_whose_targeted_read_is_still_pending(broken):
    edit(broken, "trace/reviews.yaml",
         "  subject: Units and frames at the atmosphere to trajectory boundary\n"
         "  date: 2026-08-21\n  reviewer: self\n  disposition: no_findings\n",
         "  subject: Units and frames at the atmosphere to trajectory boundary\n"
         "  date: 2026-08-21\n  reviewer: self\n  disposition: pending\n")
    assert_error(broken, "SL-01: accepted with no completed targeted read; REV-005 still pending")
    assert not any(e.startswith("SL-02") for e in errors(broken))     # in_progress, unaffected


def test_findings_raised_targeted_read_satisfies_acceptance(broken):
    edit(broken, "trace/reviews.yaml", "  disposition: no_findings\n", "  disposition: findings_raised\n")
    assert not any("targeted read" in e for e in errors(broken))


# ------------------------------------------------------------------ findings and reviews (F-03, F-06)

def test_fixed_s1_must_name_a_conformance_test(broken):
    edit(broken, "trace/findings.yaml",
         "ref: modules/trajectory/conformance/test_errors.py::test_leaving_envelope_raises_C104",
         "ref: modules/trajectory/tests/test_internal.py::test_ground_crossing_interpolates_linearly")
    assert_error(broken, "FND-001", "unit tests are model-owned")


def test_clause_finding_ref_must_resolve(broken):
    edit(broken, "trace/findings.yaml", "ref: modules/trajectory/CONTRACT.md::C-106", "ref: modules/trajectory/CONTRACT.md::C-160")
    assert_error(broken, "FND-003: clause 'C-160' is not a marked clause")


def test_fixed_clause_finding_needs_a_change_row(broken):
    edit(broken, "trace/changes.yaml", "ref: FND-003", "ref: DEC-001")
    assert_error(broken, "FND-003: fixed clause-form finding on a contract clause, but no changes.yaml row cites it")


def test_rejected_finding_needs_a_reason(broken):
    edit(broken, "trace/findings.yaml", "  reason: Proposed test derived", "  reason_removed: Proposed test derived")
    assert_error(broken, "FND-002: rejected without a reason")


def test_gate_state_is_derived_and_ordered(broken):
    edit(broken, "trace/reviews.yaml", "  gate: G2\n  date: 2026-08-14\n  reviewer: external systems engineer; specification-review on opus\n  disposition: passed",
         "  gate: G2\n  date: 2026-08-14\n  reviewer: external systems engineer; specification-review on opus\n  disposition: pending")
    assert_error(broken, "REV-004: G3 passed but G2 has no passed gate row")


def test_review_kind_and_reviewer_validated(broken):
    edit(broken, "trace/reviews.yaml", "kind: targeted_read\n  slice: SL-01", "kind: targeted-read\n  slice: SL-01")
    edit(broken, "trace/reviews.yaml", "reviewer: external systems engineer; specification-review on opus", "reviewer: ''")
    assert_error(broken, "REV-005: kind 'targeted-read' invalid", "REV-003: reviewer must name a person and/or a model")


# ------------------------------------------------------------------ model independence (CORE-HRN-001, F-48)

def test_gate_review_naming_no_model_is_a_warning(green):
    issues = check_traces.check(check_traces.load(green))
    assert any("REV-001: gate review names no model" in str(i) for i in issues if i.level == "warning")
    assert not any("REV-003" in str(i) or "REV-004" in str(i) for i in issues)


def test_review_on_the_authoring_model_is_an_error(broken):
    edit(broken, "trace/reviews.yaml",
         "  reviewer: self; specification-review on opus\n  disposition: passed\n  notes: Contracts 1.0",
         "  slice: SL-01\n  reviewer: self; specification-review on claude-sonnet-4-5\n  disposition: passed\n  notes: Contracts 1.0")
    assert_error(broken, "REV-004: gate review ran on the model that authored SL-01 (authored_by: sonnet)")


def test_authored_by_must_be_a_model_name(broken):
    edit(broken, "trace/slices.yaml", "  authored_by: sonnet\n", "  authored_by: ''\n")
    assert_error(broken, "SL-01: authored_by must name the implementing session's model")


def test_change_row_must_cite_decision_or_finding(broken):
    edit(broken, "trace/changes.yaml", "ref: DEC-001", "ref: DEC-002")
    assert_error(broken, "CHG-001: ref 'DEC-002' must cite a decision record")


# ------------------------------------------------------------------ fault points (F-43)

def test_unarmed_fault_point(broken):
    edit(broken, "modules/trajectory/conformance/test_invariants.py", 'faults.arm("trajectory.integrate")', 'faults.arm("trajectory.other")')
    assert_error(broken, 'fault_point("trajectory.integrate") is armed by no test')


# ------------------------------------------------------------------ mutation survivors (CORE-TST-002)

MUTATION_ROW = ("- id: FND-099\n  date: 2026-09-02\n  slice: SL-02\n  source: mutation\n  form: test\n"
                "  severity: S2\n  status: admitted\n  ref: modules/trajectory/src/integrator.py::x_simulate__mutmut_3\n"
                "  summary: Survived mutant\n")


def test_open_mutation_finding_names_its_mutant(broken):
    path = broken / "trace" / "findings.yaml"
    path.write_text(path.read_text(encoding="utf-8") + MUTATION_ROW, encoding="utf-8")
    assert errors(broken) == []                                   # SL-02 is in_progress: allowed
    edit(broken, "trace/findings.yaml", "ref: modules/trajectory/src/integrator.py::x_simulate__mutmut_3",
         "ref: modules/trajectory/src/integrater.py::x_simulate__mutmut_3")
    assert_error(broken, "FND-099", "does not exist")
    edit(broken, "trace/findings.yaml", "ref: modules/trajectory/src/integrater.py::x_simulate__mutmut_3",
         "ref: x_simulate__mutmut_3")
    assert_error(broken, "FND-099", "must be modules/<m>/src/<file>::<mutant id> while open")


def test_accepted_slice_may_not_carry_open_survivors(broken):
    path = broken / "trace" / "findings.yaml"
    path.write_text(path.read_text(encoding="utf-8") + MUTATION_ROW.replace("slice: SL-02", "slice: SL-01"), encoding="utf-8")
    assert_error(broken, "SL-01: survivors_triaged is true but FND-099 still open")
    assert_error(broken, "SL-01: accepted with untriaged S2 mutation survivors on trajectory")
    edit(broken, "trace/findings.yaml", "  status: admitted\n  ref: modules/trajectory/src/integrator.py::x_simulate__mutmut_3",
         "  status: rejected\n  reason: equivalent\n  ref: modules/trajectory/src/integrator.py::x_simulate__mutmut_3")
    assert errors(broken) == []


def test_an_open_s3_survivor_is_backlog_and_does_not_block(broken):
    """The S3 half of the rule: a survivor on a module no hazard names is recorded and
    left open without stopping acceptance, which is what makes the rung affordable (P5)."""
    path = broken / "trace" / "findings.yaml"
    path.write_text(path.read_text(encoding="utf-8")
                    + MUTATION_ROW.replace("slice: SL-02", "slice: SL-01").replace("severity: S2", "severity: S3"),
                    encoding="utf-8")
    assert errors(broken) == []


def test_accepted_slice_with_survivors_triaged_false_is_an_error(broken):
    edit(broken, "trace/slices.yaml", "  survivors_triaged: true\n", "  survivors_triaged: false\n")
    assert_error(broken, "SL-01: accepted with untriaged S2 mutation survivors on trajectory")


def test_survivors_triaged_is_asked_for_only_where_a_hazard_names_the_module(broken):
    """SL-01 names trajectory, which HZ-002's mitigation_contract points at. Point it
    somewhere else and the same slice needs no triage flag: nothing there is S2."""
    edit(broken, "trace/slices.yaml", "  survivors_triaged: true\n", "")
    assert_error(broken, "SL-01: accepted with untriaged S2 mutation survivors on trajectory")
    edit(broken, "trace/hazards.yaml", "mitigation_contract: modules/trajectory/CONTRACT.md::C-103",
         "mitigation_contract: modules/atmosphere/CONTRACT.md::C-003")
    assert not any("untriaged" in e for e in errors(broken))


# ------------------------------------------------------------------ report (F-14)

def test_report_exits_nonzero_and_banners_errors_on_broken_chain(broken):
    edit(broken, "trace/hazards.yaml", "  requirement: REQ-003\n", "")
    run = cli(broken, "--report")
    assert run.returncode == 1
    head = run.stdout.splitlines()[:6]
    assert "**BROKEN: 1 error(s). Do not review this matrix as evidence.**" in head
    assert any("HZ-001: missing required field 'requirement'" in line for line in head)
    assert "## Requirements" in run.stdout      # the matrix still renders, under the banner


# ------------------------------------------------------------------ vocabulary against core (P3)

def test_validation_class_enum_matches_the_g1_table():
    """The class list lives in CORE-LFC-003; the checker's enum may not drift from it."""
    g1 = (ROOT / "core" / "lifecycle" / "g1-requirements-validation-basis.md").read_text(encoding="utf-8")
    table = re.findall(r"^\| `([a-z_]+)` \|", g1, re.M)
    assert len(table) == len(set(table)), f"duplicate class in the G1 table: {table}"
    assert set(table) == check_traces.VALIDATION_CLASS
