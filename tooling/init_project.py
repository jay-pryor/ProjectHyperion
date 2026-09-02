#!/usr/bin/env python3
"""Assemble a project's operating layer from the framework at a pinned version.

A copied CLAUDE.md has no version and no drift check (F-17). This script instantiates
the project template with every generated block filled for the chosen profiles, and
writes .hyperion/: `version` (the framework's VERSION file, else `git describe`),
`profiles` (so --upgrade knows what to render), and `imperatives.json` (the map
check_imperatives.py reads when run from the project). Derives from CORE-IMP-001.

Usage:
    python hyperion/tooling/init_project.py --profiles simulation <project_root>
    python hyperion/tooling/init_project.py --upgrade [--profiles ...] <project_root>
    python hyperion/tooling/init_project.py --name <PROJECT> ...   # default: directory name

--upgrade re-renders the generated blocks of CLAUDE.md and docs/module-map.md and the
Claude Code binding (.claude/, .hyperion/session-types.json, .devcontainer/; CORE-HRN-001),
re-pins the version, and leaves every hand-written section untouched. Without --upgrade the
script refuses to overwrite an existing CLAUDE.md.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import build_layer
import framework_docs as fd


def framework_version(root=fd.FRAMEWORK_ROOT):
    version = root / "VERSION"
    if version.exists():
        return version.read_text(encoding="utf-8").strip()
    out = subprocess.run(["git", "describe", "--tags", "--always"], cwd=root,
                         capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def template_body(root=fd.FRAMEWORK_ROOT):
    """The markdown inside the template's fenced block, generated blocks emptied."""
    _, body = fd.split_frontmatter(fd.read(root / build_layer.TEMPLATE))
    inner = fd.fenced_block(body, "markdown")
    if inner is None:
        raise SystemExit(f"ERROR {build_layer.TEMPLATE}: no ```markdown block")
    return fd.GENERATED_RE.sub(lambda m: f"<!-- generated:{m.group(1)} -->\n<!-- /generated -->", inner)


def module_map_body(root=fd.FRAMEWORK_ROOT):
    _, body = fd.split_frontmatter(fd.read(root / "templates" / "module-map.md"))
    return fd.fenced_block(body, "markdown")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project_root")
    ap.add_argument("--profiles", action="append", metavar="NAME[,NAME]",
                    help="profile name (repeatable); on --upgrade defaults to .hyperion/profiles")
    ap.add_argument("--upgrade", action="store_true", help="re-render generated blocks only")
    ap.add_argument("--name", help="project name for the CLAUDE.md heading (default: directory name)")
    args = ap.parse_args(argv)
    args.profiles = fd.split_profiles(args.profiles)

    project = Path(args.project_root).resolve()
    hyp = project / ".hyperion"
    claude = project / "CLAUDE.md"

    if args.upgrade:
        profiles = args.profiles if args.profiles is not None else build_layer.project_profiles(project)
        if not hyp.exists() and args.profiles is None:
            raise SystemExit(f"ERROR {project}: no .hyperion/; pass --profiles or run without --upgrade")
    else:
        profiles = args.profiles or []
        if claude.exists():
            raise SystemExit(f"ERROR {claude} exists; use --upgrade to re-render its generated blocks")
        name = args.name or project.name
        write(claude, template_body().replace("<PROJECT>", name))
        module_map = project / "docs" / "module-map.md"
        if not module_map.exists():
            write(module_map, module_map_body())

    src = build_layer.Sources()
    src.profile_fragments(profiles)        # fails on an unknown profile before writing
    outputs = build_layer.project_outputs(src, project, profiles)
    if src.errors:
        for e in src.errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1
    if claude.exists():
        missing = [b for b in ("session-table", "imperatives", "stop-conditions", "loadout", "targeted-reads")
                   if b not in fd.block_names(fd.read(claude))]
        for b in missing:
            print(f"WARNING {claude.name} has no <!-- generated:{b} --> block; add the markers to receive it")

    write(hyp / "version", framework_version() + "\n")
    write(hyp / "profiles", "\n".join(profiles) + ("\n" if profiles else ""))
    for path in build_layer.apply(outputs, check=False):
        print(f"Wrote {Path(path).relative_to(project)}")
    print(f"OK {project.name}: profiles [{', '.join(profiles) or 'none'}], "
          f"framework {framework_version()} pinned in .hyperion/version")
    return 0


if __name__ == "__main__":
    sys.exit(main())
