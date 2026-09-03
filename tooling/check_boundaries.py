#!/usr/bin/env python3
"""Validate the real import graph against modules/*/manifest.yaml (CORE-CON-003).

The manifest is the single statement of what a module may import: `build_layer.py`
draws the module map from it and this script proves the map true. Without the check the
manifest is a drawing, and the diagram drifts from the code -- the death of architecture
documentation the rule exists to prevent.

Four rules, each failing the build:

  surface     From outside a module, only `modules/<m>/contract*` is importable, and
              `modules/<m>/conformance/**` from test code alone. Those two are the whole
              of what is promised (CORE-CON-001); `src/` and `tests/` are internals.
  declared    Every `baseline/*` or `modules/*` import a module makes is listed in its
              own manifest. An import not on the list fails; adding one is an
              Interface-tier decision that leaves a visible diff (CORE-CHG-001).
  drawn       Every entry in a manifest is actually imported. An entry nothing uses is
              an edge on the module map that does not exist in the code.
  acyclic     No cycle among modules, and nothing in `baseline/` imports a module.

Usage:
    python tooling/check_boundaries.py <project_root>      # exit 1 on any violation
"""

import ast
import sys
from pathlib import Path

import yaml

SKIP_DIRS = {"hyperion", "console", "trace", "docs", "lessons", "lint", "fixtures"}


def source_files(root):
    """Every project .py file, excluding dot directories, caches, and the vendored framework."""
    for path in sorted(root.rglob("*.py")):
        parts = path.relative_to(root).parts
        if any(p.startswith(".") or p == "__pycache__" for p in parts[:-1]):
            continue
        if parts[0] in SKIP_DIRS:
            continue
        yield path


def resolve(root, file, node):
    """Dotted names a single import statement binds, resolved to project modules."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    base = node.module or ""
    if node.level:                                     # from . import x / from ..y import z
        pkg = file.relative_to(root).parts[:-1]
        pkg = pkg[: len(pkg) - (node.level - 1)]
        base = ".".join([*pkg, base] if base else pkg)
    if not base:
        return []
    # `from a.b import c` is an import of a.b.c when a/b/c is itself a module.
    out = []
    for alias in node.names:
        target = root / Path(*base.split(".")) / alias.name
        out.append(f"{base}.{alias.name}" if target.with_suffix(".py").exists()
                   or target.is_dir() else base)
    return out


def internal_imports(root, file):
    """{import path: first line} for imports of `modules/...` or `baseline/...`."""
    tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        for dotted in resolve(root, file, node):
            head = dotted.split(".")[0]
            if head in ("modules", "baseline"):
                found.setdefault(dotted.replace(".", "/"), node.lineno)
    return found


def is_test(root, file):
    """Test code may reuse another module's conformance suite; production code may not."""
    parts = file.relative_to(root).parts
    return ("conformance" in parts or "tests" in parts or parts[0] == "validation"
            or file.name.startswith("test_") or file.name == "conftest.py")


def surface_violation(target, owner, from_test):
    """The message when `target` reaches past module `owner`'s surface, else None."""
    rest = target.split("/", 2)[2] if target.count("/") >= 2 else ""
    if rest.startswith("contract"):
        return None
    if rest == "conformance" or rest.startswith("conformance/"):
        if from_test:
            return None
        return (f"imports {owner}'s conformance suite from production code; a suite is "
                f"promised to other tests, not to implementations")
    reached = rest or "the module package"
    return (f"reaches into {owner}'s internals ({reached}); only modules/{owner}/contract*"
            f" is importable, and modules/{owner}/conformance/** from test code")


def owner_of(root, file):
    """The module a file belongs to, or None for baseline and everything else."""
    parts = file.relative_to(root).parts
    return parts[1] if len(parts) > 2 and parts[0] == "modules" else None


def collect(root):
    """(uses, errors): uses is {module or None: {target: (file, line)}} for external imports."""
    uses, errors = {}, []
    for file in source_files(root):
        owner, from_test = owner_of(root, file), is_test(root, file)
        where = file.relative_to(root)
        for target, line in internal_imports(root, file).items():
            if owner and target.startswith(f"modules/{owner}/"):
                continue                                        # a module's own internals
            if target.startswith("modules/"):
                other = target.split("/")[1]
                bad = surface_violation(target, other, from_test)
                if bad:
                    errors.append(f"{where}:{line}: {bad}")
                    continue
            uses.setdefault(owner, {}).setdefault(target, (where, line))
    return uses, errors


def check_manifests(root, uses):
    """Declared-versus-used, both directions, for every module."""
    errors = []
    for mdir in sorted(p for p in (root / "modules").glob("*") if p.is_dir()):
        manifest = mdir / "manifest.yaml"
        if not manifest.exists():
            errors.append(f"modules/{mdir.name}: no manifest.yaml; the module declares no imports")
            continue
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        declared = [str(i) for i in data.get("allowed_imports") or []]
        used = uses.get(mdir.name, {})
        for target, (where, line) in sorted(used.items()):
            if target not in declared:
                errors.append(f"{where}:{line}: imports {target}, which modules/{mdir.name}/"
                              f"manifest.yaml does not list")
        for target in declared:
            if target not in used:
                errors.append(f"modules/{mdir.name}/manifest.yaml: declares {target}, which no file "
                              f"in the module imports; the module map draws an edge that is not there")
    return errors


def cycles(uses):
    """Module-to-module cycles in the real graph, as `a -> b -> a` strings."""
    edges = {m: sorted({t.split("/")[1] for t in targets if t.startswith("modules/")})
             for m, targets in uses.items() if m}
    found, path, on_path, done = [], [], set(), set()

    def walk(node):
        path.append(node); on_path.add(node)
        for nxt in edges.get(node, []):
            if nxt in on_path:
                found.append(" -> ".join(path[path.index(nxt):] + [nxt]))
            elif nxt not in done:
                walk(nxt)
        path.pop(); on_path.discard(node); done.add(node)

    for module in sorted(edges):
        if module not in done:
            walk(module)
    return sorted(set(found))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(argv[0]).resolve()
    if not (root / "modules").is_dir():
        print(f"ERROR no modules/ under {root}")
        return 1

    uses, errors = collect(root)
    errors += check_manifests(root, uses)
    errors += [f"baseline/: imports {t} ({w}:{l}); baseline is the substrate every module "
               f"inherits and cannot depend on one"
               for t, (w, l) in sorted(uses.get(None, {}).items())
               if t.startswith("modules/") and str(w).startswith("baseline/")]
    errors += [f"circular dependency: {c}; the decomposition is wrong, not the check"
               for c in cycles(uses)]

    modules = sorted(p.name for p in (root / "modules").glob("*") if p.is_dir())
    for module in modules:
        edges = sorted(uses.get(module, {}))
        print(f"{module}  {len(edges)} import(s): {', '.join(edges) or 'none'}")
    if errors:
        for line in errors:
            print(f"FAIL {line}")
        print(f"FAIL {len(errors)} boundary violation(s) across {len(modules)} module(s)")
        return 1
    print(f"OK {len(modules)} module(s); the import graph matches the manifests and is acyclic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
