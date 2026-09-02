#!/usr/bin/env python3
"""Mutation score per slice, survivors as findings rows.

Rung 2 of CORE-TST-002: at slice acceptance the mutation tool runs over modules/<m>/src
for every module the slice's contracts: names, with the test command restricted to that
module's conformance/ plus validation/ and never tests/, so a unit test written beside
the implementation cannot mask a weak conformance suite (P8). The score is killed /
total and goes on the slice as mutation_score (CORE-TRC-002); every survivor is a
findings row with source: mutation (CORE-TRC-003), S1 when the mutated module is named
by a hazard's mitigation_contract.

Usage:
    python tooling/mutation_score.py --slice SL-nn <project_root>        # print only
    python tooling/mutation_score.py --module <m> <project_root>
    python tooling/mutation_score.py --slice SL-nn --write <project_root>  # append rows, set slice fields
    python tooling/mutation_score.py --slice SL-nn --mutants DIR <root>    # parse an existing mutants/ dir

Toolchain: mutmut 3.x (pip install mutmut). It runs in a scratch copy of the project so
its mutants/ cache and its test run never touch the project or trace/results.xml. With
--mutants the run is skipped and DIR is parsed instead; tooling/tests uses this with a
canned results file. --write is idempotent: a survivor whose ref is already in
findings.yaml is skipped, and the slice's mutation_score and survivors_triaged are set.
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


def hazard_modules(root):
    """Modules named by any hazard's mitigation_contract (modules/<m>/...)."""
    found = set()
    for h in load_yaml(root / "trace" / "hazards.yaml"):
        parts = str(h.get("mitigation_contract", "")).split("/")
        if len(parts) >= 2 and parts[0] == "modules":
            found.add(parts[1])
    return found


# ------------------------------------------------------------------ running mutmut

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


def finding_row(mutant, fid, slice_id, hazard_mods, date):
    module = mutant.file.split("/")[1]
    where = f"{Path(mutant.file).name}:{mutant.line} in {mutant.function}" if mutant.line else f"{mutant.function}"
    change = f': "{mutant.before}" became "{mutant.after}"' if mutant.before else ""
    return {
        "id": f"FND-{fid:03d}",
        "date": date,
        "slice": slice_id,
        "source": "mutation",
        "form": "test",
        "severity": "S1" if module in hazard_mods else "S2",
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


def survivor_rows(survivors, root, slice_id, hazard_mods, date):
    """Rows for survivors not already recorded by ref; also the refs still open."""
    findings = load_yaml(root / "trace" / "findings.yaml")
    known = {str(f.get("ref")): f.get("status") for f in findings}
    fid = next_finding_id(findings)
    rows = []
    for m in survivors:
        if m.ref in known:
            continue
        rows.append(finding_row(m, fid, slice_id, hazard_mods, date))
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


def set_slice_fields(root, slice_id, value, triaged):
    """Replace or add mutation_score and survivors_triaged inside the slice's block, text-wise."""
    path = root / "trace" / "slices.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == f"- id: {slice_id}"), None)
    if start is None:
        raise SystemExit(f"ERROR {slice_id} is not in trace/slices.yaml")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("- ")), len(lines))
    block = [l for l in lines[start:end] if not l.strip().startswith(("mutation_score:", "survivors_triaged:"))]
    while block and not block[-1].strip():
        block.pop()
    block += [f"  mutation_score: {value}", f"  survivors_triaged: {'true' if triaged else 'false'}"]
    path.write_text("\n".join(lines[:start] + block + lines[end:]) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument("--slice", help="SL-nn; modules come from its contracts: list")
    which.add_argument("--module", help="one module; rows are printed without a slice unless --slice")
    ap.add_argument("--write", action="store_true", help="append survivor rows and set the slice fields")
    ap.add_argument("--mutants", help="parse this mutants/ directory instead of running mutmut")
    ap.add_argument("root")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if args.write and not args.slice:
        ap.error("--write needs --slice; the fields go on a slice record")

    modules = modules_for_slice(root, args.slice) if args.slice else [args.module]
    for m in modules:
        if not (root / "modules" / m / "src").is_dir():
            raise SystemExit(f"ERROR modules/{m}/src does not exist")
    hazard_mods = hazard_modules(root)
    today = dt.date.today().isoformat()

    mutants = []
    with tempfile.TemporaryDirectory(prefix="hyperion-mutmut-") as tmp:
        for m in modules:
            mutants_dir = Path(args.mutants) if args.mutants else run_mutmut(root, m, Path(tmp) / m)
            found = parse_results(mutants_dir, m)
            mutants += [describe(mutants_dir, root, x) for x in found]
            print(f"{m}: {len(found)} mutants from modules/{m}/src ({'parsed' if args.mutants else 'mutmut run'})")

    killed, survived, value = score(mutants)
    other = len(mutants) - killed - survived
    survivors = [x for x in mutants if x.status in SURVIVED]
    label = args.slice or args.module
    print(f"mutation_score {label}: {value}  ({killed} killed, {survived} survived, {other} other of {len(mutants)})")

    rows, open_refs = survivor_rows(survivors, root, args.slice or "<SL-nn>", hazard_mods, today)
    print(f"survivors: {len(survivors)}, new rows: {len(rows)}, already recorded: {len(survivors) - len(rows)}")
    if rows:
        print("# ready to append to trace/findings.yaml" + ("" if args.write else " (not written; pass --write)"))
        print("".join(render_row(r) for r in rows), end="")

    if args.write:
        if rows:
            append_findings(root, rows)
        set_slice_fields(root, args.slice, value, triaged=not open_refs)
        print(f"wrote {len(rows)} row(s); {args.slice}: mutation_score {value}, survivors_triaged {not open_refs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
