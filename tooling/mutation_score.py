#!/usr/bin/env python3
"""Mutation score per slice, survivors as findings rows.

Rung 2 of CORE-TST-002: at slice acceptance the mutation tool runs over modules/<m>/src
for every module the slice's contracts: names, with the test command restricted to that
module's conformance/ plus validation/ and never tests/, so a unit test written beside
the implementation cannot mask a weak conformance suite (P8). The score is killed /
total per module and goes on the slice as mutation_score (CORE-TRC-002); every survivor
is a findings row with source: mutation (CORE-TRC-003).

Severity comes from the hazard register, not from here. A survivor on a module some
hazard's mitigation_contract names is S2 and blocks acceptance; anywhere else it is S3,
"defect not covered by any contract promise" (CORE-REV-005), and is backlog. Minting one
severity for every survivor empties whichever class it mints, and a blocking finding per
line of source is the control that gets dropped first (P5). S1 is never minted here at
all: whether the gap lets silently wrong output through is read off the mutant.

Usage:
    python tooling/mutation_score.py --slice SL-nn <project_root>        # print only
    python tooling/mutation_score.py --module <m> <project_root>
    python tooling/mutation_score.py --slice SL-nn --write <project_root>  # append S2 rows, set slice fields
    python tooling/mutation_score.py --slice SL-nn --triage <m> <root>     # append one module's rows, on demand
    python tooling/mutation_score.py --slice SL-nn --check <project_root>  # CI: the record is still earned
    python tooling/mutation_score.py --slice SL-nn --mutants DIR <root>    # parse an existing mutants/ dir

Toolchain: mutmut 3.x, pinned (pip install "mutmut>=3,<4"). The parsing below reads
mutmut 3.x internals -- its exit-code map, its x_<name>__mutmut_<n> mangling, and its
mutants/ layout -- so a major version it has not been read against is refused rather
than silently parsed as zero mutants, which would record a score of 0.0 with no
survivors and pass every check. A run that finds no mutant at all is an error for the
same reason. mutmut runs in a scratch copy of the project so its mutants/ cache and its
test run never touch the project or trace/results.xml. With --mutants the run is skipped
and DIR is parsed instead; tooling/tests uses this with a canned results file. --write is
idempotent: a survivor whose ref is already in findings.yaml is skipped, and the slice's
mutation_score and survivors_triaged are set.
"""

import argparse
import ast
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

KILLED = {"killed", "timeout"}                  # behaviour changed and a test noticed
SURVIVED = {"survived", "no tests"}             # nothing noticed, or nothing ran
STATUS_BY_EXIT_CODE = {1: "killed", 3: "killed", 0: "survived", 5: "no tests", 33: "no tests",
                       34: "skipped", 35: "suspicious", 36: "timeout", 37: "caught by type check",
                       -24: "timeout", 24: "timeout", 152: "timeout", 255: "timeout",
                       None: "not checked"}
MUTANT_KEY_RE = re.compile(r"^(?P<module>[\w.]+)\.(?P<mangled>x_\w+?)__mutmut_(?P<n>\d+)$")
CLASS_SEPARATOR = "ClassName"                   # mutmut: x_<Class>ClassName<method>ClassName...
MUTMUT_MAJOR = 3                                # the internals below are mutmut 3.x's
HAZARD_CONTRACT_RE = re.compile(r"^modules/([^/]+)/CONTRACT\.md::")


@dataclass
class Mutant:
    key: str            # modules.trajectory.src.integrator.x_simulate__mutmut_3
    file: str           # modules/trajectory/src/integrator.py
    function: str       # simulate
    status: str
    line: int = 0       # in the original file, best effort
    before: str = ""
    after: str = ""

    @property
    def ref(self):
        return f"{self.file}::{self.key.rsplit('.', 1)[1]}"


# ------------------------------------------------------------------ project records

def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or [] if path.exists() else []


def modules_for_slice(root, slice_id):
    for s in load_yaml(root / "trace" / "slices.yaml"):
        if s.get("id") == slice_id:
            contracts = s.get("contracts") or []
            return [contracts] if isinstance(contracts, str) else list(contracts)
    raise SystemExit(f"ERROR {slice_id} is not in trace/slices.yaml")


def hazard_named_modules(hazards):
    """Modules some hazard's mitigation_contract points at (CORE-TRC-002#hazard).

    This is where a survivor's severity comes from. The field already exists and is the
    hazard register's, so nothing moves into or out of the blocking class without an
    edit a human makes to a hazard -- there is no severity knob on this tool to turn."""
    named = set()
    for h in hazards:
        m = HAZARD_CONTRACT_RE.match(str(h.get("mitigation_contract") or ""))
        if m:
            named.add(m.group(1))
    return named


def severity_for(module, hazard_named):
    return "S2" if module in hazard_named else "S3"


def derived_floor(slices, module, exclude=None):
    """The highest score any other accepted slice recorded for `module`, or None.

    The acceptance bar for a module is that its score did not fall. No constant appears
    anywhere: a fixed floor would be a number with no basis, which CORE-CON-001 forbids
    of a tolerance, and equivalent mutants give every module a different unreachable
    ceiling. Derived from the records on every read, never stored, so the only way to
    lower a floor is to edit the accepted slice it comes from (CORE-TST-002 rung 2)."""
    seen = []
    for s in slices:
        scores = s.get("mutation_score")
        if s.get("id") == exclude or s.get("status") != "accepted" or not isinstance(scores, dict):
            continue
        value = scores.get(module)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            seen.append(value)
    return max(seen) if seen else None


# ------------------------------------------------------------------ running mutmut

def check_mutmut_version():
    """Refuse a mutmut whose internals this parser has not been read against.

    parse_results reads mutmut's exit-code map, its name mangling, and its mutants/
    layout. Under a version that changed any of them it would find nothing and report a
    score of 0.0 with no survivors -- a passing record for a run that measured nothing
    (P2). Fail loudly instead."""
    from importlib import metadata
    try:
        version = metadata.version("mutmut")
    except metadata.PackageNotFoundError:
        raise SystemExit('ERROR mutmut is not installed; pip install "mutmut>=3,<4"')
    if version.split(".")[0] != str(MUTMUT_MAJOR):
        raise SystemExit(f"ERROR mutmut {version} is installed; this reads mutmut "
                         f'{MUTMUT_MAJOR}.x internals. pip install "mutmut>={MUTMUT_MAJOR},'
                         f'<{MUTMUT_MAJOR + 1}", or read the new layout and raise MUTMUT_MAJOR.')
    return version


def mutmut_config(module):
    return "\n".join([
        "[mutmut]",
        "source_paths=\n    modules\n    baseline",
        f"only_mutate=modules/{module}/src/*",
        "also_copy=\n    validation/\n    conftest.py",
        "pytest_add_cli_args=\n    --import-mode=importlib\n    -p\n    no:cacheprovider",
        f"pytest_add_cli_args_test_selection=\n    modules/{module}/conformance\n    validation",
        "use_git_change_detection=false",
        "use_setproctitle=false",
        "",
    ])


def run_mutmut(root, module, workdir):
    """Copy the project into workdir, configure mutmut for one module, run it; return mutants/."""
    copy = workdir / "project"
    shutil.copytree(root, copy, ignore=shutil.ignore_patterns(".git", "mutants", "__pycache__",
                                                             ".pytest_cache", "results.xml"))
    pyproject = copy / "pyproject.toml"
    if pyproject.exists() and "[tool.mutmut]" in pyproject.read_text(encoding="utf-8"):
        raise SystemExit("ERROR pyproject.toml carries [tool.mutmut]; it would override the per-module config")
    (copy / "setup.cfg").write_text(mutmut_config(module), encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "mutmut", "run"], cwd=copy, capture_output=True, text=True)
    if run.returncode != 0 and not list((copy / "mutants").glob("**/*.meta")):
        raise SystemExit(f"ERROR mutmut run failed (exit {run.returncode}):\n{run.stdout[-2000:]}\n{run.stderr[-2000:]}")
    return copy / "mutants"


# ------------------------------------------------------------------ parsing results

def parse_results(mutants_dir, module):
    """Every mutant of modules/<module>/src from the .meta files mutmut wrote."""
    found = []
    for meta in sorted((Path(mutants_dir) / "modules" / module / "src").glob("**/*.py.meta")):
        rel = meta.relative_to(mutants_dir).as_posix()[: -len(".meta")]
        data = json.loads(meta.read_text(encoding="utf-8"))
        for key, code in data.get("exit_code_by_key", {}).items():
            m = MUTANT_KEY_RE.match(key)
            function = _function_name(m.group("mangled")) if m else key
            found.append(Mutant(key, rel, function, STATUS_BY_EXIT_CODE.get(code, "suspicious")))
    return found


def _function_name(mangled):
    if CLASS_SEPARATOR in mangled:
        return mangled[mangled.rindex(CLASS_SEPARATOR) + len(CLASS_SEPARATOR):]
    return mangled[2:] if mangled.startswith("x_") else mangled


def _functions(source):
    """{name: list of source lines} for every function in a file, keyed by name."""
    out = {}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = (node.lineno, source.splitlines()[node.lineno - 1: node.end_lineno])
    return out


def describe(mutants_dir, root, mutant):
    """Fill line/before/after from the mutated file against its __mutmut_orig twin."""
    mutated = Path(mutants_dir) / mutant.file
    original = Path(root) / mutant.file
    if not mutated.exists():
        return mutant
    funcs = _functions(mutated.read_text(encoding="utf-8"))
    name = mutant.key.rsplit(".", 1)[1]
    orig = funcs.get(name.rpartition("__mutmut_")[0] + "__mutmut_orig")
    this = funcs.get(name)
    if not (orig and this):
        return mutant
    twin = [l.replace(name, name.rpartition("__mutmut_")[0] + "__mutmut_orig") for l in this[1]]
    for offset, (a, b) in enumerate(zip(orig[1], twin)):
        if a != b:
            mutant.before, mutant.after = a.strip(), b.strip()
            break
    else:
        offset = 0
    if original.exists():
        start = _functions(original.read_text(encoding="utf-8")).get(mutant.function)
        mutant.line = start[0] + offset if start else 0
    return mutant


def score(mutants):
    killed = sum(1 for m in mutants if m.status in KILLED)
    survived = sum(1 for m in mutants if m.status in SURVIVED)
    total = killed + survived
    return killed, survived, (round(killed / total, 3) if total else 0.0)


# ------------------------------------------------------------------ findings rows

def next_finding_id(findings):
    numbers = [int(f["id"].split("-")[1]) for f in findings if re.match(r"^FND-\d+$", str(f.get("id")))]
    return max(numbers, default=0) + 1


def finding_row(mutant, fid, slice_id, date, severity):
    """One survivor as a findings row, at the severity the hazard register gives it.

    A survivor establishes that the suite cannot see the change. Whether that is a broken
    promise (S2, a hazard is riding on this module) or a behaviour nothing promised (S3)
    is not the tool's judgement to make, and S1 never is: whether the gap lets silently
    wrong output through is read off the mutant, never off its address
    (CORE-TST-002 rung 2, CORE-REV-005#severity)."""
    where = f"{Path(mutant.file).name}:{mutant.line} in {mutant.function}" if mutant.line else f"{mutant.function}"
    change = f': "{mutant.before}" became "{mutant.after}"' if mutant.before else ""
    return {
        "id": f"FND-{fid:03d}",
        "date": date,
        "slice": slice_id,
        "source": "mutation",
        "form": "test",
        "severity": severity,
        "status": "admitted",
        "ref": mutant.ref,
        "summary": f"Survived mutant at {where}{change}",
    }


def render_row(row):
    lines = [f"- id: {row['id']}"]
    for key in ("date", "slice", "source", "form", "severity", "status", "ref"):
        lines.append(f"  {key}: {row[key]}")
    lines.append(f"  summary: {json.dumps(row['summary'])}")     # JSON string is valid YAML
    return "\n".join(lines) + "\n"


def survivor_rows(survivors, root, slice_id, date, severity="S2", first_id=None):
    """Rows for survivors this slice has not recorded; also the refs still open.

    A row is matched on (ref, slice), not on ref alone. A mutant lives in a module, and
    a module is named by more than one slice: rejecting one as equivalent under the
    promises the first slice claimed would otherwise excuse it for every later slice,
    silently, in the one direction that never shows up as an error. Measured again for
    another slice, it is raised again against that slice's promises.

    `first_id` continues the numbering across modules within one run, since the rows are
    not appended until every module has been measured."""
    findings = load_yaml(root / "trace" / "findings.yaml")
    known = {str(f.get("ref")): f.get("status") for f in findings if f.get("slice") == slice_id}
    fid = next_finding_id(findings) if first_id is None else first_id
    rows = []
    for m in survivors:
        if m.ref in known:
            continue
        rows.append(finding_row(m, fid, slice_id, date, severity))
        fid += 1
    open_refs = [m.ref for m in survivors if known.get(m.ref, "admitted") in ("admitted", "reopened")]
    return rows, open_refs


# ------------------------------------------------------------------ writing

def append_findings(root, rows):
    path = root / "trace" / "findings.yaml"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    path.write_text(text + "".join(render_row(r) for r in rows), encoding="utf-8")


def render_scores(scores):
    """`{trajectory: 0.762}` -- a flow mapping, one entry per module (CORE-TRC-002#slice)."""
    return "{" + ", ".join(f"{m}: {v}" for m, v in sorted(scores.items())) + "}"


def set_slice_fields(root, slice_id, scores, triaged):
    """Replace or add mutation_score and survivors_triaged inside the slice's block, text-wise.

    `triaged` is None for a slice no hazard-named module belongs to: its survivors are S3
    backlog, the field would gate nothing, and check_traces.py does not ask for it."""
    path = root / "trace" / "slices.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == f"- id: {slice_id}"), None)
    if start is None:
        raise SystemExit(f"ERROR {slice_id} is not in trace/slices.yaml")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("- ")), len(lines))
    block = [l for l in lines[start:end] if not l.strip().startswith(("mutation_score:", "survivors_triaged:"))]
    while block and not block[-1].strip():
        block.pop()
    block.append(f"  mutation_score: {render_scores(scores)}")
    if triaged is not None:
        block.append(f"  survivors_triaged: {'true' if triaged else 'false'}")
    path.write_text("\n".join(lines[:start] + block + lines[end:]) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main

def recorded_score(root, slice_id):
    """The mutation_score mapping already on the slice, or None."""
    for s in load_yaml(root / "trace" / "slices.yaml"):
        if s.get("id") == slice_id:
            return s.get("mutation_score")
    raise SystemExit(f"ERROR {slice_id} is not in trace/slices.yaml")


def check_against_record(root, slice_id, scores, rows):
    """CI: is the record still earned by the suite as it stands?

    Three failures a records-only checker cannot see, because it never measures: a score
    nobody earned, a score that has fallen below what an earlier accepted slice reached
    for the same module, and a survivor that appeared after the record was written.
    Whether a recorded survivor is still open is check_traces.py's, not repeated here
    (P3). Returns the exit code."""
    recorded = recorded_score(root, slice_id)
    slices = load_yaml(root / "trace" / "slices.yaml")
    problems, reported = [], []
    if recorded is None:
        problems.append(f"{slice_id} carries no mutation_score; run --write and triage the survivors")
        recorded = {}
    elif not isinstance(recorded, dict):
        problems.append(f"{slice_id} records mutation_score as a single number; it is a mapping of "
                        f"module to score (CORE-TRC-002). Re-run --write.")
        recorded = {}
    for module, value in sorted(scores.items()):
        was = recorded.get(module)
        if was is None and recorded:
            problems.append(f"{slice_id} records no mutation_score for {module}, which its contracts: names")
        elif was is not None and value < was:
            problems.append(f"{module} measured {value}, below the recorded {was}; the suite has "
                            f"weakened since it was written, or the record was never earned")
        floor = derived_floor(slices, module, exclude=slice_id)
        if floor is not None and value < floor:
            problems.append(f"{module} measured {value}, below the {floor} an accepted slice already "
                            f"earned for it; the score ratchets (CORE-TST-002 rung 2)")
        reported.append(f"{module} measured {value}, recorded {was}"
                        + (f", floor {floor}" if floor is not None else ", no floor yet"))
    if rows:
        refs = "\n  ".join(r["ref"] for r in rows)
        problems.append(f"{len(rows)} S2 survivor(s) have no findings row:\n  {refs}")
    for line in problems:
        print(f"ERROR {line}")
    if not problems:
        print(f"OK {slice_id}: {'; '.join(reported)}; every S2 survivor recorded")
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument("--slice", help="SL-nn; modules come from its contracts: list")
    which.add_argument("--module", help="one module; rows are printed without a slice unless --slice")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true",
                      help="append the S2 survivor rows and set the slice fields")
    mode.add_argument("--triage", metavar="MODULE",
                      help="append this module's survivor rows on demand, at the severity the "
                           "hazard register gives them; a worklist, never a gate")
    mode.add_argument("--check", action="store_true",
                      help="exit 1 unless every recorded score is still earned, none has fallen "
                           "below its floor, and every S2 survivor is recorded")
    ap.add_argument("--mutants", help="parse this mutants/ directory instead of running mutmut")
    ap.add_argument("root")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if (args.write or args.check or args.triage) and not args.slice:
        ap.error("--write, --triage and --check need --slice; the rows and fields belong to a slice")

    modules = modules_for_slice(root, args.slice) if args.slice else [args.module]
    for m in modules:
        if not (root / "modules" / m / "src").is_dir():
            raise SystemExit(f"ERROR modules/{m}/src does not exist")
    if args.triage and args.triage not in modules:
        raise SystemExit(f"ERROR --triage {args.triage} is not in {args.slice}'s contracts: "
                         f"({', '.join(modules)})")
    today = dt.date.today().isoformat()
    if not args.mutants:
        print(f"mutmut {check_mutmut_version()}")

    per_module = {}
    with tempfile.TemporaryDirectory(prefix="hyperion-mutmut-") as tmp:
        for m in modules:
            mutants_dir = Path(args.mutants) if args.mutants else run_mutmut(root, m, Path(tmp) / m)
            found = parse_results(mutants_dir, m)
            if not found:
                raise SystemExit(f"ERROR no mutant was found for modules/{m}/src under {mutants_dir}. "
                                 "A run that measures nothing must not be recorded as a score of 0.0; "
                                 "check the mutmut version and the module's src/ (CORE-TST-002).")
            per_module[m] = [describe(mutants_dir, root, x) for x in found]
            print(f"{m}: {len(found)} mutants from modules/{m}/src ({'parsed' if args.mutants else 'mutmut run'})")

    hazard_named = hazard_named_modules(load_yaml(root / "trace" / "hazards.yaml"))
    slice_id = args.slice or "<SL-nn>"
    scores, rows, s2_rows, open_refs = {}, [], [], []
    fid = next_finding_id(load_yaml(root / "trace" / "findings.yaml"))
    for m, muts in per_module.items():
        killed, survived, scores[m] = score(muts)
        other = len(muts) - killed - survived
        severity = severity_for(m, hazard_named)
        survivors = [x for x in muts if x.status in SURVIVED]
        module_rows, module_open = survivor_rows(survivors, root, slice_id, today, severity, fid)
        fid += len(module_rows)
        rows += module_rows
        if severity == "S2":
            s2_rows += module_rows
            open_refs += module_open
        print(f"mutation_score {slice_id}/{m}: {scores[m]}  ({killed} killed, {survived} survived, "
              f"{other} other of {len(muts)}); {len(survivors)} survivor(s) at {severity}, "
              f"{len(module_rows)} new row(s)"
              + ("" if severity == "S2" else " (backlog; --triage to record them)"))

    if args.check:
        return check_against_record(root, args.slice, scores, s2_rows)

    # --write records what blocks acceptance; --triage records one module on request.
    # Everything else is printed, so a survivor is never invisible, only unfiled.
    to_write = s2_rows if args.write else [r for r in rows if r["ref"].startswith(
        f"modules/{args.triage}/")] if args.triage else []
    if rows:
        print("# ready to append to trace/findings.yaml"
              + ("" if to_write else " (not written; pass --write, or --triage <module>)"))
        print("".join(render_row(r) for r in rows), end="")

    if args.write or args.triage:
        if to_write:
            append_findings(root, to_write)
        if args.write:
            triaged = not open_refs if hazard_named & set(modules) else None
            set_slice_fields(root, args.slice, scores, triaged)
            print(f"wrote {len(to_write)} row(s); {args.slice}: mutation_score "
                  f"{render_scores(scores)}, survivors_triaged {triaged}")
        else:
            print(f"wrote {len(to_write)} row(s) for {args.triage}; slice fields untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
