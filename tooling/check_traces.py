#!/usr/bin/env python3
"""Check every record in trace/ against the Trace Records schema.

Trace tables written in prose are intentions: a renamed test, a deleted requirement, or
a mitigation pointing at nothing stays invisible until it matters. This script makes the
whole record store checkable. Rationale: CORE-TRC-001. Schema it enforces: CORE-TRC-002
(registers: requirements, hazards, slices) and CORE-TRC-003 (logs: findings, reviews,
needs, assumptions, goals, changes, and the generated results.xml), plus the model
independence rule of CORE-HRN-001 over reviews and a slice's authored_by.

Usage (run from the project root, or pass --root):
    python tooling/check_traces.py                 # CI: exit 1 on any break
    python tooling/check_traces.py --report        # matrix on stdout; exit 1 if broken
    python tooling/check_traces.py --root DIR      # project root (default: cwd)

Strictness is not a flag. It is derived from trace/reviews.yaml: once a gate row records
G3 as passed, TBDs and unclaimed requirements become errors (CORE-TRC-003, M4).

Library API, used by the project console and by tooling/tests:
    project = load(root)          # Project: every record set, results, modules, clauses
    issues  = check(project)      # list[Issue]; level is "error" or "warning"
    text    = report(project, issues)
The CLI is a thin wrapper over these three calls.

Requires PyYAML. Records are flat (scalars and lists of scalars); nesting is rejected
so a mis-parsed trace is loud, not silent.
"""

import ast
import datetime as dt
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# ------------------------------------------------------------------ vocabulary (CORE-TRC-002/003)

RECORD_FILES = {           # file stem -> (id prefix, required fields)
    "requirements": ("REQ", ["statement", "kind", "source", "allocated_to",
                             "verification_method", "verified_by", "validation_class",
                             "validated_by", "status"]),
    "hazards": ("HZ", ["register", "never_statement", "failure_mode", "mitigation_contract",
                       "mitigation_test", "mitigation_status", "requirement"]),
    "slices": ("SL", ["name", "requirements", "hazards", "contracts", "status"]),
    "findings": ("FND", ["date", "slice", "source", "form", "severity", "status", "summary"]),
    "reviews": ("REV", ["kind", "date", "reviewer", "disposition"]),
    "needs": ("STK", ["statement", "owner"]),
    "assumptions": ("ASM", ["statement", "owner", "revisit_when"]),
    "goals": ("GOAL", ["statement"]),
    "changes": ("CHG", ["date", "tier", "driver", "ref", "contracts"]),
}

REQ_KIND = {"functional", "cross-cutting"}
VERIFICATION_METHOD = {"test", "analysis", "inspection", "demonstration"}
VALIDATION_CLASS = {"analytical", "conservation", "invariant", "degenerate", "reference",
                    "convergence", "expert_judgement"}
LIFECYCLE = {"proposed", "traced", "verified"}
REGISTER = {"org", "local"}
FAILURE_MODE = {"not_performed", "performed_incorrectly", "performed_wrong_time",
                "performed_uncommanded", "failed_silently"}       # the five G0 questions
SLICE_STATUS = {"planned", "in_progress", "accepted"}
FINDING_FORM = {"test", "clause"}
FINDING_SEVERITY = {"S1", "S2", "S3", "S4"}
FINDING_STATUS = {"admitted", "rejected", "fixed", "reopened"}
FINDING_SOURCE = {"specification", "gate", "mutation", "human", "hands-on"}   # CORE-TRC-003; "is the contract right" is specification (F-29)
REVIEW_KIND = {"gate", "targeted_read", "inspection", "lens", "specification"}
GATES = ["G0", "G1", "G2", "G3", "G4"]
DISPOSITION = {"passed", "failed", "pending", "no_findings", "findings_raised"}
POSITIVE_DISPOSITION = {"passed", "no_findings"}
CHANGE_TIER = {"interface", "baseline"}

MODEL_RE = re.compile(r"claude|opus|sonnet|haiku|fable", re.I)     # a reviewer names a model (CORE-HRN-001)
MODEL_FAMILY_RE = re.compile(r"opus|sonnet|haiku|fable", re.I)
MODEL_REVIEW_KIND = {"gate", "specification", "lens"}

ID_RE = re.compile(r"^[A-Z]{2,4}-\d{2,3}$")      # SL-nn is two digits (TPL-005)
CLAUSE_RE = re.compile(r"\bC-\d{3}\b")
FAULT_POINT_RE = re.compile(r"""\bfault_point\(\s*["']([^"']+)["']\s*\)""")


# ------------------------------------------------------------------ data

@dataclass
class Issue:
    level: str          # "error" | "warning"
    subject: str        # record id or file
    message: str

    def __str__(self):
        return f"{self.subject}: {self.message}"


@dataclass
class Module:
    name: str
    surface: Path | None        # modules/<m>/contract.<ext>; None for baseline
    prose: Path | None          # modules/<m>/CONTRACT.md
    clauses: set = field(default_factory=set)


@dataclass
class Project:
    root: Path
    records: dict = field(default_factory=dict)      # stem -> list[dict]
    results: dict = field(default_factory=dict)      # test node id -> outcome
    modules: dict = field(default_factory=dict)      # name -> Module
    decisions: set = field(default_factory=set)      # DEC-nnn with a file under docs/decisions
    fault_points: dict = field(default_factory=dict)  # name -> [source paths]
    armed_by: dict = field(default_factory=dict)      # name -> [conformance test node ids]
    load_issues: list = field(default_factory=list)

    def ids(self, stem):
        return {r["id"] for r in self.records.get(stem, []) if isinstance(r.get("id"), str)}

    def by_id(self, stem):
        return {r["id"]: r for r in self.records.get(stem, []) if isinstance(r.get("id"), str)}

    def gates_passed(self):
        return {r.get("gate") for r in self.records.get("reviews", [])
                if r.get("kind") == "gate" and r.get("disposition") == "passed"}

    def after_g3(self):
        return "G3" in self.gates_passed()

    def find_tests(self, node_id):
        """Exact match, or every member of a parametrised family named without brackets."""
        if node_id in self.results:
            return {node_id: self.results[node_id]}
        prefix = node_id + "["
        return {k: v for k, v in self.results.items() if k.startswith(prefix)}


# ------------------------------------------------------------------ loading

def _flat(value):
    if isinstance(value, list):
        return all(not isinstance(v, (list, dict)) for v in value)
    return not isinstance(value, dict)


def _load_records(project, stem):
    path = project.root / "trace" / f"{stem}.yaml"
    prefix, _ = RECORD_FILES[stem]
    if not path.exists():
        project.load_issues.append(Issue("error", f"trace/{stem}.yaml", "missing"))
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(data, list):
        project.load_issues.append(Issue("error", f"trace/{stem}.yaml", "must be a list of records"))
        return []
    out, seen = [], set()
    for i, rec in enumerate(data, 1):
        if not isinstance(rec, dict):
            project.load_issues.append(Issue("error", f"trace/{stem}.yaml", f"record {i} is not a mapping"))
            continue
        rid = rec.get("id")
        if not isinstance(rid, str) or not ID_RE.match(rid) or not rid.startswith(prefix + "-"):
            project.load_issues.append(Issue("error", f"trace/{stem}.yaml",
                                             f"record {i}: id {rid!r} must look like {prefix}-nnn (SL-nn)"))
            continue
        if rid in seen:
            project.load_issues.append(Issue("error", rid, "duplicate id"))
        seen.add(rid)
        for k, v in rec.items():
            if not _flat(v):
                project.load_issues.append(Issue("error", rid, f"'{k}' is nested; records are flat"))
        out.append(rec)
    return out


def _node_id(root, classname, name):
    """Rebuild a pytest node id from JUnit classname + name. The longest dotted prefix
    that is a file on disk is the path; the rest are class names."""
    parts = classname.split(".")
    for i in range(len(parts), 0, -1):
        candidate = "/".join(parts[:i]) + ".py"
        if (root / candidate).exists():
            return "::".join([candidate, *parts[i:], name])
    return classname.replace(".", "/") + ".py::" + name


def _load_results(project):
    path = project.root / "trace" / "results.xml"
    if not path.exists():
        project.load_issues.append(Issue(
            "error", "trace/results.xml",
            "missing; run the test suite immediately before this check "
            "(pytest --junitxml=trace/results.xml). A stale or hand-made file defeats the check"))
        return
    for case in ET.parse(path).getroot().iter("testcase"):
        node = _node_id(project.root, case.get("classname", ""), case.get("name", ""))
        outcome = "passed"
        for child in case:
            if child.tag in ("failure", "error"):
                outcome = "failed"
            elif child.tag == "skipped":
                outcome = "xfailed" if "xfail" in (child.get("type") or "") else "skipped"
        project.results[node] = outcome


def _load_modules(project):
    for surface in sorted((project.root / "modules").glob("*/contract.*")):
        name = surface.parent.name
        prose = surface.parent / "CONTRACT.md"
        clauses = set(CLAUSE_RE.findall(prose.read_text(encoding="utf-8"))) if prose.exists() else set()
        project.modules[name] = Module(name, surface, prose if prose.exists() else None, clauses)
    if (project.root / "baseline").is_dir():
        project.modules["baseline"] = Module("baseline", None, None)


def _arming_tests(path, rel):
    """Node ids of test functions in `path` that call arm("<name>"), keyed by name."""
    found = {}
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test"):
            continue
        for call in ast.walk(node):
            if (isinstance(call, ast.Call) and getattr(call.func, "attr", getattr(call.func, "id", None)) == "arm"
                    and call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str)):
                found.setdefault(call.args[0].value, []).append(f"{rel}::{node.name}")
    return found


def _load_fault_points(project):
    sources = list((project.root / "modules").glob("*/src/**/*.py")) + list((project.root / "baseline").glob("**/*.py"))
    for src in sources:
        for name in FAULT_POINT_RE.findall(src.read_text(encoding="utf-8")):
            project.fault_points.setdefault(name, []).append(src.relative_to(project.root).as_posix())
    for test in (project.root / "modules").glob("*/conformance/**/*.py"):
        for name, ids in _arming_tests(test, test.relative_to(project.root).as_posix()).items():
            project.armed_by.setdefault(name, []).extend(ids)


def load(root):
    """Load every record set, the JUnit results, modules and clauses, decisions, fault points."""
    project = Project(Path(root).resolve())
    for stem in RECORD_FILES:
        project.records[stem] = _load_records(project, stem)
    _load_results(project)
    _load_modules(project)
    project.decisions = {p.stem for p in (project.root / "docs" / "decisions").glob("DEC-*.md")}
    _load_fault_points(project)
    return project


# ------------------------------------------------------------------ shared checks

def _as_list(value):
    if value is None:
        return []
    return list(value) if isinstance(value, list) else [value]


def _is_conformance_or_validation(node_id):
    path = node_id.split("::", 1)[0]
    parts = path.split("/")
    return (path.startswith("modules/") and "conformance" in parts) or path.startswith("validation/")


def _check_test_ref(project, subject, node_id, must_pass, err):
    """A traced test: full node id, under conformance/ or validation/, present in
    results.xml, and (when must_pass) passed. Returns True when the reference is sound."""
    path = node_id.split("::", 1)[0]
    if "::" not in node_id:
        err(subject, f"'{node_id}' is not a full test id (path::name)")
        return False
    if "tests" in path.split("/"):
        err(subject, f"'{node_id}' is a unit test; unit tests are model-owned and cannot verify "
                     "a requirement or a hazard (P8). Trace a conformance/ or validation/ test")
        return False
    if not _is_conformance_or_validation(node_id):
        err(subject, f"'{node_id}' is not under modules/*/conformance/ or validation/")
        return False
    members = project.find_tests(node_id)
    if not members:
        err(subject, f"'{node_id}' is not in trace/results.xml (renamed, deleted, or not collected?)")
        return False
    bad = {k: v for k, v in members.items() if v != "passed"}
    if bad and must_pass:
        detail = ", ".join(f"{k} {v}" for k, v in sorted(bad.items()))
        err(subject, f"traced test did not pass: {detail}")
        return False
    return True


def _check_mutant_ref(project, subject, ref, err):
    """An open mutation finding names its mutant: modules/<m>/src/<file>::<mutant id>, file exists."""
    path = ref.split("::", 1)[0]
    parts = path.split("/")
    if "::" not in ref or len(parts) < 4 or parts[0] != "modules" or parts[2] != "src":
        err(subject, f"mutation finding ref '{ref}' must be modules/<m>/src/<file>::<mutant id> while open")
        return False
    if not (project.root / path).is_file():
        err(subject, f"mutation finding ref '{ref}': '{path}' does not exist")
        return False
    return True


def _check_review_ref(project, subject, rev_id, must_pass, err):
    reviews = project.by_id("reviews")
    if rev_id not in reviews:
        err(subject, f"'{rev_id}' does not resolve to a review record")
        return False
    if must_pass and reviews[rev_id].get("disposition") not in POSITIVE_DISPOSITION:
        err(subject, f"review {rev_id} has disposition '{reviews[rev_id].get('disposition')}'; "
                     "a verified claim needs passed or no_findings")
        return False
    return True


def _check_clause_ref(project, subject, ref, err):
    """modules/<m>/CONTRACT.md::C-nnn or modules/<m>/contract.<ext>::C-nnn; both halves resolve."""
    if "::" not in ref:
        err(subject, f"'{ref}' must be <contract path>::C-nnn")
        return False
    path, clause = ref.split("::", 1)
    parts = path.split("/")
    if len(parts) != 3 or parts[0] != "modules" or not (project.root / path).exists():
        err(subject, f"contract path '{path}' does not exist under modules/")
        return False
    module = project.modules.get(parts[1])
    if module is None or module.surface is None:
        err(subject, f"'{parts[1]}' has no contract.* surface; it is not a module")
        return False
    if parts[2] != "CONTRACT.md" and (project.root / path) != module.surface:
        err(subject, f"'{path}' is neither the module's contract surface nor its CONTRACT.md")
        return False
    if clause not in module.clauses:
        err(subject, f"clause '{clause}' is not a marked clause in modules/{parts[1]}/CONTRACT.md")
        return False
    return True


def _check_date(subject, value, err):
    if isinstance(value, dt.date):
        return True
    try:
        dt.date.fromisoformat(str(value))
        return True
    except ValueError:
        err(subject, f"date '{value}' is not YYYY-MM-DD")
        return False


def _check_enum(subject, fld, value, allowed, err):
    if value not in allowed:
        err(subject, f"{fld} '{value}' invalid (expected one of {sorted(allowed)})")
        return False
    return True


# ------------------------------------------------------------------ record checks

def _required(project, stem, err):
    _, fields = RECORD_FILES[stem]
    for r in project.records.get(stem, []):
        for f in fields:
            if f not in r or r[f] is None or r[f] == "":
                err(r["id"], f"missing required field '{f}'")


def check_requirements(project, err, warn):
    after_g3 = project.after_g3()
    sources = project.ids("hazards") | project.ids("needs") | project.ids("assumptions") | project.ids("goals")
    for r in project.records["requirements"]:
        rid, status = r["id"], r.get("status")
        _check_enum(rid, "status", status, LIFECYCLE, err)
        if status == "proposed" and after_g3:
            err(rid, "still proposed after G3 passed; every requirement is traced or verified at G3")
        tbd_ok = status == "proposed"

        for src in _as_list(r.get("source")):
            if src not in sources:
                err(rid, f"source '{src}' does not resolve to a hazard, need, assumption, or goal")

        _check_enum(rid, "kind", r.get("kind"), REQ_KIND, err)
        alloc = r.get("allocated_to")
        targets = _as_list(alloc)
        if r.get("kind") == "functional" and (isinstance(alloc, list) or alloc == "baseline"):
            err(rid, "functional requirement must be allocated to exactly one module, not a list "
                     "or baseline (only cross-cutting may)")
        for m in targets:
            if m not in project.modules:
                err(rid, f"allocated_to '{m}' is not a module (modules/*/contract.* or baseline)")
        if not targets:
            err(rid, "not allocated to a module; an orphan requirement is nobody's job")

        method = r.get("verification_method")
        _check_enum(rid, "verification_method", method, VERIFICATION_METHOD, err)
        vby = _as_list(r.get("verified_by"))
        if not vby:
            err(rid, "no verified_by")
        for v in vby:
            v = str(v)
            if v == "TBD":
                (warn if tbd_ok else err)(rid, "verified_by is TBD" + ("" if tbd_ok else "; TBD is permitted only while proposed"))
            elif method == "test":
                _check_test_ref(project, rid, v, status == "verified", err)
            elif v.startswith("REV-"):
                _check_review_ref(project, rid, v, status == "verified", err)
            else:
                err(rid, f"verification_method {method} needs verified_by REV-nnn, got '{v}'")

        vclass = r.get("validation_class")
        _check_enum(rid, "validation_class", vclass, VALIDATION_CLASS, err)
        vd = str(r.get("validated_by"))
        if vd == "TBD":
            (warn if tbd_ok else err)(rid, "validated_by is TBD" + ("" if tbd_ok else "; TBD is permitted only while proposed"))
        elif vclass == "expert_judgement":
            if not vd.startswith("REV-"):
                err(rid, f"expert_judgement needs validated_by REV-nnn, got '{vd}'")
            else:
                _check_review_ref(project, rid, vd, status == "verified", err)
        elif vclass in VALIDATION_CLASS:
            _check_test_ref(project, rid, vd, status == "verified", err)


def check_hazards(project, err, warn):
    after_g3 = project.after_g3()
    req_ids = project.ids("requirements")
    for h in project.records["hazards"]:
        hid, status = h["id"], h.get("mitigation_status")
        _check_enum(hid, "mitigation_status", status, LIFECYCLE, err)
        if status == "proposed" and after_g3:
            err(hid, "mitigation still proposed after G3 passed")
        tbd_ok = status == "proposed"

        register = h.get("register")
        if _check_enum(hid, "register", register, REGISTER, err):
            need = ["org_hazard_id", "org_system"] if register == "org" else ["severity", "likelihood"]
            forbid = ["severity", "likelihood"] if register == "org" else ["org_hazard_id", "org_system"]
            for f in need:
                if f not in h:
                    err(hid, f"register {register} requires '{f}'")
            for f in forbid:
                if f in h:
                    err(hid, f"register {register} forbids '{f}' (assessment lives in the "
                             f"{'organisational system' if register == 'org' else 'local record'})")
            if register == "local":
                for f in ("severity", "likelihood"):
                    if f in h and not isinstance(h[f], int):
                        err(hid, f"{f} must be an integer on the profile's scale")

        _check_enum(hid, "failure_mode", h.get("failure_mode"), FAILURE_MODE, err)

        contract = str(h.get("mitigation_contract"))
        if contract == "TBD":
            (warn if tbd_ok else err)(hid, "mitigation_contract is TBD" + ("" if tbd_ok else "; permitted only while proposed"))
        else:
            _check_clause_ref(project, hid, contract, err)

        test = str(h.get("mitigation_test"))
        if test == "TBD":
            (warn if tbd_ok else err)(hid, "mitigation_test is TBD" + ("" if tbd_ok else "; permitted only while proposed"))
        else:
            _check_test_ref(project, hid, test, status == "verified", err)

        for rq in _as_list(h.get("requirement")):      # presence is enforced by _required
            if rq not in req_ids:
                err(hid, f"requirement '{rq}' does not resolve")


def check_slices(project, err, warn):
    reqs, hazards = project.by_id("requirements"), project.by_id("hazards")
    claimed = set()
    for s in project.records["slices"]:
        sid = s["id"]
        _check_enum(sid, "status", s.get("status"), SLICE_STATUS, err)
        accepted = s.get("status") == "accepted"
        for rid in _as_list(s.get("requirements")):
            claimed.add(rid)
            if rid not in reqs:
                err(sid, f"claims requirement '{rid}', which does not exist")
            elif accepted and reqs[rid].get("status") != "verified":
                err(sid, f"accepted but claims {rid}, which is {reqs[rid].get('status')}, not verified")
        for hid in _as_list(s.get("hazards")):
            if hid not in hazards:
                err(sid, f"claims hazard '{hid}', which does not exist")
            elif accepted and hazards[hid].get("mitigation_status") != "verified":
                err(sid, f"accepted but claims {hid}, whose mitigation is "
                         f"{hazards[hid].get('mitigation_status')}, not verified")
        for m in _as_list(s.get("contracts")):
            if m not in project.modules or m == "baseline":
                err(sid, f"contracts names '{m}', which is not a module with a contract")
        if "mutation_score" in s and not (isinstance(s["mutation_score"], (int, float)) and 0 <= s["mutation_score"] <= 1):
            err(sid, "mutation_score must be a number from 0 to 1 (killed / total)")
        if "survivors_triaged" in s and not isinstance(s["survivors_triaged"], bool):
            err(sid, "survivors_triaged must be true or false")
        if "authored_by" in s and not (isinstance(s["authored_by"], str) and s["authored_by"].strip()):
            err(sid, "authored_by must name the implementing session's model (CORE-HRN-001)")
        # CORE-TST-002 rung 2: triaged means no mutation finding on the slice is still open,
        # and an accepted slice may not carry open survivors.
        open_survivors = [f["id"] for f in project.records["findings"]
                          if f.get("slice") == sid and f.get("source") == "mutation"
                          and f.get("status") in ("admitted", "reopened")]
        if s.get("survivors_triaged") is True and open_survivors:
            err(sid, f"survivors_triaged is true but {', '.join(open_survivors)} still open (source mutation)")
        if accepted and (s.get("survivors_triaged") is False or open_survivors):
            err(sid, "accepted with untriaged mutation survivors; kill each with a conformance test "
                     "or reject it as equivalent with a reason")

    for rid in sorted(project.ids("requirements") - claimed):
        (err if project.after_g3() else warn)(rid, "not claimed by any slice" +
                                               (" (an error once G3 has passed)" if project.after_g3() else ""))


def check_findings(project, err, warn):
    slices, req_ids, hz_ids = project.ids("slices"), project.ids("requirements"), project.ids("hazards")
    cited_by_change = {c.get("ref") for c in project.records["changes"]}
    for f in project.records["findings"]:
        fid, status, form, sev = f["id"], f.get("status"), f.get("form"), f.get("severity")
        _check_date(fid, f.get("date"), err)
        if f.get("slice") not in slices:
            err(fid, f"slice '{f.get('slice')}' does not resolve")
        src = str(f.get("source"))
        if not (src in FINDING_SOURCE or re.match(r"^lens:[a-z0-9-]+$", src)):
            err(fid, f"source '{src}' must be lens:<name> or one of {sorted(FINDING_SOURCE)}")
        _check_enum(fid, "form", form, FINDING_FORM, err)
        _check_enum(fid, "severity", sev, FINDING_SEVERITY, err)
        _check_enum(fid, "status", status, FINDING_STATUS, err)

        if status == "rejected":
            if not f.get("reason"):
                err(fid, "rejected without a reason; the rejected list is calibration data")
            continue
        ref = f.get("ref")
        if not ref:
            err(fid, f"{status} finding has no ref; a finding without its artifact is vague model output")
            continue
        ref = str(ref)
        if form == "test" and src == "mutation" and status in ("admitted", "reopened"):
            _check_mutant_ref(project, fid, ref, err)          # CORE-TST-002: the mutant, until killed
        elif form == "test":
            if sev in ("S1", "S2") and status == "fixed":
                _check_test_ref(project, fid, ref, True, err)      # conformance/validation, passed
            elif not project.find_tests(ref):
                err(fid, f"ref '{ref}' is not in trace/results.xml")
            elif status == "fixed" and any(v != "passed" for v in project.find_tests(ref).values()):
                err(fid, f"fixed but '{ref}' did not pass")
        elif form == "clause":
            if ref.startswith("REQ-") or ref.startswith("HZ-") or ref.startswith("DEC-"):
                known = req_ids | hz_ids | project.decisions
                if ref not in known:
                    err(fid, f"ref '{ref}' does not resolve to a requirement, hazard, or decision record")
            elif _check_clause_ref(project, fid, ref, err) and status == "fixed" and fid not in cited_by_change:
                err(fid, "fixed clause-form finding on a contract clause, but no changes.yaml row cites it; "
                         "a clause finding closes when the contract changes")


def _same_model(a, b):
    """Two model names agree when their families agree, else when the strings do."""
    fa, fb = MODEL_FAMILY_RE.search(a), MODEL_FAMILY_RE.search(b)
    if fa and fb:
        return fa.group(0).lower() == fb.group(0).lower()
    return a.strip().lower() == b.strip().lower()


def _check_independence(project, rid, kind, reviewer, slice_id, err, warn):
    """CORE-HRN-001: a gate or specification review names its model; no model review
    runs on the model that authored the slice."""
    names_model = bool(MODEL_RE.search(reviewer))
    if kind in ("gate", "specification") and not names_model:
        warn(rid, f"{kind} review names no model in reviewer; if a model reviewed, name it so "
                  "independence can be checked (CORE-HRN-001)")
    slice_row = project.by_id("slices").get(slice_id) if slice_id else None
    authored = (slice_row or {}).get("authored_by")
    if kind in MODEL_REVIEW_KIND and names_model and isinstance(authored, str) and _same_model(reviewer, authored):
        err(rid, f"{kind} review ran on the model that authored {slice_id} (authored_by: {authored}); "
                 "a review on the authoring model shares its blind spots (CORE-HRN-001)")


def check_reviews(project, err, warn):
    slices = project.ids("slices")
    known = project.ids("requirements") | project.ids("hazards") | slices | project.decisions
    passed = project.gates_passed()
    for r in project.records["reviews"]:
        rid, kind = r["id"], r.get("kind")
        _check_enum(rid, "kind", kind, REVIEW_KIND, err)
        _check_date(rid, r.get("date"), err)
        if not isinstance(r.get("reviewer"), str) or not r["reviewer"].strip():
            err(rid, "reviewer must name a person and/or a model")
        else:
            _check_independence(project, rid, kind, r["reviewer"], r.get("slice"), err, warn)
        _check_enum(rid, "disposition", r.get("disposition"), DISPOSITION, err)
        if kind == "gate":
            gate = r.get("gate")
            if _check_enum(rid, "gate", gate, set(GATES), err) and r.get("disposition") == "passed":
                prior = GATES[GATES.index(gate) - 1] if gate != "G0" else None
                if prior and prior not in passed:
                    err(rid, f"{gate} passed but {prior} has no passed gate row; gates are one-way doors in order")
        elif "gate" in r:
            err(rid, "gate is only meaningful when kind is gate")
        if "slice" in r and r["slice"] not in slices:
            err(rid, f"slice '{r['slice']}' does not resolve")
        if "ref" in r and r["ref"] not in known and not (project.root / str(r["ref"])).exists():
            err(rid, f"ref '{r['ref']}' does not resolve to a record or a path")


def check_logs(project, err, warn):
    finding_ids = project.ids("findings")
    for c in project.records["changes"]:
        cid = c["id"]
        _check_date(cid, c.get("date"), err)
        _check_enum(cid, "tier", c.get("tier"), CHANGE_TIER, err)
        ref = str(c.get("ref"))
        if ref not in finding_ids and ref not in project.decisions:
            err(cid, f"ref '{ref}' must cite a decision record (docs/decisions/DEC-nnn.md) or a finding")
        for m in _as_list(c.get("contracts")):
            if m not in project.modules:
                err(cid, f"contracts names '{m}', which is not a module")


def check_fault_points(project, err, warn):
    for name, where in sorted(project.fault_points.items()):
        tests = project.armed_by.get(name, [])
        if not tests:
            err(where[0], f"fault_point(\"{name}\") is armed by no test under modules/*/conformance/; "
                          "a fault point nothing exercises is dead code, not a control")
            continue
        outcomes = {t: project.results.get(t) for t in tests}
        if not any(v == "passed" for v in outcomes.values()):
            err(where[0], f"fault_point(\"{name}\") is armed by {', '.join(tests)} but none passed "
                          f"({outcomes})")


def check(project):
    """Every rule in CORE-TRC-002 and CORE-TRC-003. Returns issues; errors fail CI."""
    issues = list(project.load_issues)
    err = lambda s, m: issues.append(Issue("error", s, m))
    warn = lambda s, m: issues.append(Issue("warning", s, m))
    if any(i.subject.startswith("trace/") and i.message.startswith("missing") for i in issues):
        return issues                     # a missing file makes every other check noise
    for stem in RECORD_FILES:
        _required(project, stem, err)
    for fn in (check_requirements, check_hazards, check_slices, check_findings,
               check_reviews, check_logs, check_fault_points):
        fn(project, err, warn)
    return issues


# ------------------------------------------------------------------ report

def _outcome(project, ref):
    ref = str(ref)
    if ref.startswith("REV-"):
        return project.by_id("reviews").get(ref, {}).get("disposition", "missing")
    members = project.find_tests(ref)
    if not members:
        return "missing"
    return "passed" if all(v == "passed" for v in members.values()) else ", ".join(sorted(set(members.values())))


def report(project, issues):
    """Markdown matrix for a reviewer who does not read code. Opens with the verdict."""
    errors = [i for i in issues if i.level == "error"]
    out = ["# Trace Matrix", ""]
    if errors:
        out += [f"**BROKEN: {len(errors)} error(s). Do not review this matrix as evidence.**", ""]
        out += [f"- {e}" for e in errors[:10]]
        if len(errors) > 10:
            out.append(f"- ... and {len(errors) - 10} more")
        out.append("")
    else:
        out += ["Chain intact: 0 errors.", ""]
    gates = ", ".join(g for g in GATES if g in project.gates_passed()) or "none"
    out += [f"Generated by `check_traces.py --report`. Gates passed: {gates}.", ""]

    claimed = {}
    for s in project.records["slices"]:
        for rid in _as_list(s.get("requirements")):
            claimed[rid] = s["id"]
    out += ["## Requirements", "",
            "| Requirement | Kind | Module | Verification | Result | Validation | Result | Status | Slice |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(project.records["requirements"], key=lambda x: x["id"]):
        vby = _as_list(r.get("verified_by"))
        vres = ", ".join(_outcome(project, v) for v in vby)
        out.append(f"| `{r['id']}` {r.get('statement', '')} | {r.get('kind', '-')} "
                   f"| {', '.join(_as_list(r.get('allocated_to')))} | {r.get('verification_method', '-')}: "
                   f"{', '.join(map(str, vby))} | {vres} | {r.get('validation_class', '-')}: "
                   f"{r.get('validated_by', '-')} | {_outcome(project, r.get('validated_by'))} "
                   f"| {r.get('status', '-')} | {claimed.get(r['id'], '-')} |")

    out += ["", "## Hazards", "",
            "| Hazard | Must never happen | Mode | Register | Control | Test | Result | Status |",
            "|---|---|---|---|---|---|---|---|"]
    for h in sorted(project.records["hazards"], key=lambda x: x["id"]):
        reg = h.get("register", "-")
        reg += f" S{h['severity']}/L{h['likelihood']}" if reg == "local" else f" {h.get('org_hazard_id', '')}"
        out.append(f"| `{h['id']}` | {h.get('never_statement', '-')} | {h.get('failure_mode', '-')} | {reg} "
                   f"| {h.get('mitigation_contract', '-')} | {h.get('mitigation_test', '-')} "
                   f"| {_outcome(project, h.get('mitigation_test'))} | {h.get('mitigation_status', '-')} |")

    out += ["", "## Slices", "", "| Slice | Requirements | Hazards | Contracts | Status |", "|---|---|---|---|---|"]
    for s in sorted(project.records["slices"], key=lambda x: x["id"]):
        out.append(f"| `{s['id']}` {s.get('name', '')} | {', '.join(_as_list(s.get('requirements'))) or '-'} "
                   f"| {', '.join(_as_list(s.get('hazards'))) or '-'} | {', '.join(_as_list(s.get('contracts'))) or '-'} "
                   f"| {s.get('status', '-')} |")

    out += ["", "## Findings", "", "| Finding | Slice | Source | Form | Severity | Status | Ref |", "|---|---|---|---|---|---|---|"]
    for f in sorted(project.records["findings"], key=lambda x: x["id"]):
        out.append(f"| `{f['id']}` {f.get('summary', '')} | {f.get('slice', '-')} | {f.get('source', '-')} "
                   f"| {f.get('form', '-')} | {f.get('severity', '-')} | {f.get('status', '-')} | {f.get('ref', '-')} |")

    out += ["", "## Reviews", "", "| Review | Kind | Gate | Date | Reviewer | Disposition | Subject |", "|---|---|---|---|---|---|---|"]
    for r in sorted(project.records["reviews"], key=lambda x: x["id"]):
        out.append(f"| `{r['id']}` | {r.get('kind', '-')} | {r.get('gate', '-')} | {r.get('date', '-')} "
                   f"| {r.get('reviewer', '-')} | {r.get('disposition', '-')} | {r.get('subject', r.get('ref', '-'))} |")

    unverified = [h["id"] for h in project.records["hazards"] if h.get("mitigation_status") != "verified"]
    open_findings = [f["id"] for f in project.records["findings"] if f.get("status") in ("admitted", "reopened")]
    out += ["", "## Open items", "",
            f"- Hazards not yet verified: {', '.join(unverified) or 'none'}",
            f"- Open findings: {', '.join(open_findings) or 'none'}",
            f"- Fault points: {len(project.fault_points)}, all armed by a passing conformance test"
            if not [i for i in errors if 'fault_point' in i.message] else "- Fault points: see errors above",
            f"- Records: {', '.join(f'{len(project.records[s])} {s}' for s in RECORD_FILES)}"]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ CLI

def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if "--strict" in args:
        print("NOTE  --strict is gone: strictness now comes from the gate record in "
              "trace/reviews.yaml (G3 passed => TBDs and unclaimed requirements are errors)",
              file=sys.stderr)
        args.remove("--strict")
    if "--trace-dir" in args:
        print("ERROR --trace-dir is gone: the checker reads the whole project; pass --root DIR",
              file=sys.stderr)
        return 2
    root = Path(args[args.index("--root") + 1]) if "--root" in args else Path.cwd()

    project = load(root)
    issues = check(project)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if "--report" in args:
        print(report(project, issues), end="")
        return 1 if errors else 0

    for w in warnings:
        print(f"WARN  {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} trace break(s). Traces are updated in the session that "
              "changes the thing being traced.", file=sys.stderr)
        return 1
    counts = ", ".join(f"{len(project.records[s])} {s}" for s in ("requirements", "hazards", "slices", "findings", "reviews"))
    print(f"OK {counts}; {len(project.results)} test results; chain intact ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
