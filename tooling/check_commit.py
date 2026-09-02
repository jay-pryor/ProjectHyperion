#!/usr/bin/env python3
"""Reject commits whose paths contradict their declared session (CORE-SES-001, M3).

Session discipline is honour-based, but its main violation is visible in the diff. Each
commit carries a `Session: <TYPE>` trailer; this script reads the session-types block
and enforces, per commit:

    1. the trailer is present and names a session type valid in this scope;
    2. every touched path matches the type's `may_modify` and nothing in its
       `must_not_modify` (a path no type names is a warning: a gap in the table);
    3. after G3 is recorded as passed, a diff to modules/*/contract.* or CONTRACT.md
       changes the contract's `Version:` line (CORE-CHG-001, F-02);
    4. a commit touching fixtures/**/expected/** or a tolerance.yaml carries a
       `Fixture-change: DEC-nnn | FND-nnn` trailer that resolves in the project's records
       at that commit (SIM-DET-001, F-24).

--framework mode, for this repository's own history, applies rule 1 only.

Usage:
    python hyperion/tooling/check_commit.py <base>..HEAD [--root DIR]
    python tooling/check_commit.py --framework <base>..HEAD

Requires git and PyYAML. Exit 1 on any error; warnings never fail.
"""

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

import yaml

import framework_docs as fd

TRAILER_RE = re.compile(r"^Session:\s*([A-Z]+)\s*$", re.MULTILINE)
FIXTURE_RE = re.compile(r"^Fixture-change:\s*((?:DEC|FND)-\d{3})\s*$", re.MULTILINE)
CONTRACT_RE = re.compile(r"^modules/([^/]+)/(contract\.[^/]+|CONTRACT\.md)$")
VERSION_LINE_RE = re.compile(r"^[-+]Version:", re.MULTILINE)
FIXTURE_PATHS = ["fixtures/*/expected/*", "fixtures/**/expected/**", "**/tolerance.yaml", "tolerance.yaml"]


# ------------------------------------------------------------------ git

def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def commits(root, rng):
    return git(root, "rev-list", "--reverse", rng).split()


def message(root, sha):
    return git(root, "show", "-s", "--format=%B", sha)


def touched(root, sha):
    return git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", sha).split()


def file_at(root, sha, path):
    out = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=root, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def diff_of(root, sha, path):
    return git(root, "show", "--format=", sha, "--", path)


# ------------------------------------------------------------------ glob matching

def matches(path, glob):
    """fnmatch with `**` spanning directories and `*` staying inside one segment."""
    pattern = re.escape(glob).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(pattern, path) is not None


def any_match(path, globs):
    return any(matches(path, g) for g in globs)


# ------------------------------------------------------------------ rules

def check_commit(root, sha, types, framework):
    """(errors, warnings) for one commit."""
    errors, warnings = [], []
    short = sha[:7]
    msg = message(root, sha)
    m = TRAILER_RE.search(msg)
    if not m:
        errors.append(f"{short}: no `Session: <TYPE>` trailer")
        return errors, warnings
    session = m.group(1)
    valid_scope = ("framework", "both") if framework else ("project", "both")
    if session not in types or types[session]["scope"] not in valid_scope:
        errors.append(f"{short}: Session {session} is not a session type valid here")
        return errors, warnings
    if framework:
        return errors, warnings

    t = types[session]
    paths = touched(root, sha)
    owned = {g for tt in types.values() if tt["scope"] != "framework" for g in tt["may_modify"]}
    for p in paths:
        if any_match(p, t["must_not_modify"]):
            errors.append(f"{short}: {session} must not modify {p}")
        elif not any_match(p, t["may_modify"]):
            if any_match(p, owned):
                errors.append(f"{short}: {p} is outside {session}'s scope (another session type owns it)")
            else:
                warnings.append(f"{short}: {p} is owned by no session type (CORE-SES-001)")

    if after_g3(root, sha):
        for p in paths:
            cm = CONTRACT_RE.match(p)
            if not cm:
                continue
            prose = f"modules/{cm.group(1)}/CONTRACT.md"
            if prose in paths and VERSION_LINE_RE.search(diff_of(root, sha, prose)):
                continue
            errors.append(f"{short}: {p} changed without a `Version:` change in {prose} (CORE-CHG-001)")

    fixture_paths = [p for p in paths if any_match(p, FIXTURE_PATHS)]
    if fixture_paths:
        fm = FIXTURE_RE.search(msg)
        if not fm:
            errors.append(f"{short}: touches {fixture_paths[0]} without a `Fixture-change: DEC-nnn | FND-nnn` trailer")
        elif not resolves(root, sha, fm.group(1)):
            errors.append(f"{short}: Fixture-change {fm.group(1)} does not resolve in the project's records")
    return errors, warnings


def after_g3(root, sha):
    text = file_at(root, sha, "trace/reviews.yaml")
    if not text:
        return False
    try:
        rows = yaml.safe_load(text) or []
    except yaml.YAMLError:
        return False
    return any(isinstance(r, dict) and r.get("kind") == "gate" and r.get("gate") == "G3"
               and r.get("disposition") == "passed" for r in rows)


def resolves(root, sha, ref):
    if ref.startswith("DEC-"):
        return file_at(root, sha, f"docs/decisions/{ref}.md") is not None
    text = file_at(root, sha, "trace/findings.yaml")
    if not text:
        return False
    try:
        rows = yaml.safe_load(text) or []
    except yaml.YAMLError:
        return False
    return any(isinstance(r, dict) and r.get("id") == ref for r in rows)


# ------------------------------------------------------------------ cli

def run(root, rng, framework=False, types=None):
    types = types or fd.session_types()
    errors, warnings = [], []
    shas = commits(root, rng)
    for sha in shas:
        e, w = check_commit(root, sha, types, framework)
        errors += e
        warnings += w
    return shas, errors, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("range", help="git revision range, e.g. main..HEAD")
    ap.add_argument("--root", default=".", help="repository root (default: cwd)")
    ap.add_argument("--framework", action="store_true", help="only require the Session trailer")
    args = ap.parse_args(argv)

    shas, errors, warnings = run(Path(args.root).resolve(), args.range, args.framework)
    for w in warnings:
        print(f"WARNING {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK {len(shas)} commit(s) in {args.range}, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
