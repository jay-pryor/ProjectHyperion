#!/usr/bin/env python3
"""Run the project's type check, and prove that it distinguishes units (CORE-CON-001).

`Metres = NewType("Metres", float)` is erased at runtime: passing Seconds where Metres is
expected raises nothing. The type is only a promise while a checker runs, so without this
step the unit lives in the type name with exactly the durability of the comment it
replaced. Two things must hold, and a mypy step alone gives neither:

  clean       mypy reports no error over the project's sources, and checked more than
              zero files -- a run that matched nothing passes vacuously.
  discriminating
              a probe synthesised from `baseline/units.py` alone is rejected: the base
              type where a unit is expected, and one unit where another is expected.
              A probe that type-checks means the units are not being enforced, whatever
              the clean run said (erased NewTypes, `ignore_errors`, an unchecked path).

The probe is derived from the unit definitions, never hand-written, so it cannot fall
behind them. It is written into the project root, checked, and removed.

Usage:
    python tooling/check_units.py <project_root>      # exit 1 when either half fails
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {"hyperion", "console", "trace", "docs", "lessons", "lint", "fixtures"}
LITERALS = {"float": "1.0", "int": "1", "str": '"x"', "bytes": 'b"x"', "bool": "True"}
CONFIGS = ("mypy.ini", ".mypy.ini", "setup.cfg", "pyproject.toml")
CHECKED_RE = re.compile(r"(?:checked|no issues found in) (\d+) source file")
PROBE = "_hyperion_units_probe.py"


def unit_types(root):
    """[(name, base type)] for every NewType in baseline/units.py, in file order."""
    path = root / "baseline" / "units.py"
    if not path.exists():
        return []
    out = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        call = node.value if isinstance(node, ast.Assign) else None
        if not (isinstance(call, ast.Call) and getattr(call.func, "id", "") == "NewType"):
            continue
        if len(call.args) == 2 and isinstance(call.args[1], ast.Name):
            out.append((node.targets[0].id, call.args[1].id))
    return out


def source_dirs(root):
    """Top-level directories holding project code, framework and generated output aside."""
    return [p.name for p in sorted(root.iterdir())
            if p.is_dir() and not p.name.startswith((".", "_"))
            and p.name not in SKIP_DIRS and any(p.rglob("*.py"))]


def mypy(root, targets):
    cmd = [sys.executable, "-m", "mypy"]
    if not any((root / c).exists() for c in CONFIGS):
        cmd += ["--explicit-package-bases", "--namespace-packages"]
    done = subprocess.run(cmd + targets, cwd=root, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def probe_source(units):
    """A probe module and the line each expected error falls on.

    Line 1 of each pair takes a unit; the call under it passes something that is not it.
    """
    by_base = {}
    for name, base in units:
        by_base.setdefault(base, []).append(name)
    lines = [f"from baseline.units import {', '.join(n for n, _ in units)}", ""]
    expected = []
    for base, names in sorted(by_base.items()):
        if base not in LITERALS:
            continue
        unit = names[0]
        lines += [f"def _takes_{unit}(x: {unit}) -> {unit}:", "    return x", ""]
        lines.append(f"_takes_{unit}({LITERALS[base]})")
        expected.append((len(lines), f"bare {base} accepted where {unit} was expected"))
        for other in names[1:]:
            lines.append(f"_takes_{unit}({other}({LITERALS[base]}))")
            expected.append((len(lines), f"{other} accepted where {unit} was expected"))
        lines.append("")
    return "\n".join(lines) + "\n", expected


def check(root, out):
    units = unit_types(root)
    if not units:
        out("FAIL baseline/units.py defines no NewType; units are not in the type (CORE-CON-001)")
        return False
    out(f"units      {len(units)} type(s): {', '.join(n for n, _ in units)}")

    dirs = source_dirs(root)
    code, text = mypy(root, dirs)
    checked = int(m.group(1)) if (m := CHECKED_RE.search(text)) else 0
    out(f"clean      mypy {' '.join(dirs)} -> {checked} file(s) checked, exit {code}")
    ok = True
    if code != 0:
        out("  FAIL: " + "\n  ".join(text.strip().splitlines()[:20]))
        ok = False
    elif checked == 0:
        out("  FAIL: the run checked no files, so it proved nothing")
        ok = False

    source, expected = probe_source(units)
    if not expected:
        out("  FAIL: no unit type has a base the probe can build a value of; nothing to prove")
        return False
    (root / PROBE).write_text(source, encoding="utf-8")
    try:
        _, text = mypy(root, [PROBE])
    finally:
        (root / PROBE).unlink(missing_ok=True)
    reported = {int(m.group(1)) for m in re.finditer(rf"^{re.escape(PROBE)}:(\d+): error:",
                                                     text, re.M)}
    out(f"probe      {len(expected)} deliberate unit confusion(s)")
    for line, what in expected:
        good = line in reported
        out(f"  line {line:<3} {what:<52} {'rejected' if good else 'FAIL: accepted'}")
        ok = ok and good
    return ok


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(argv[0]).resolve()
    if check(root, print):
        print("OK the type check runs clean and rejects every unit confusion put to it")
        return 0
    print("FAIL units are documented in the type but not enforced by one")
    return 1


if __name__ == "__main__":
    sys.exit(main())
