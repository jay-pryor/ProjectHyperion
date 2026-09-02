#!/usr/bin/env python3
"""Print the files a session type loads, from frontmatter (F-20, TOOL-001).

The loadout used to be defined twice, in frontmatter and in a hand-written table, with
different membership. Frontmatter is now the only definition: `load: always` documents
enter every session, `load: on-task` documents enter the session types in their
`sessions:` field, profile documents only when the profile is active, and root-tier
documents never. Project files come from the session-types block (CORE-SES-001) and the
profile fragments. The scope hook and the session skills read the same resolver.

Usage:
    python hyperion/tooling/loadout.py --session IMPLEMENT [--profiles simulation]
    python hyperion/tooling/loadout.py --session IMPLEMENT --root <project>   # profiles from .hyperion
    python hyperion/tooling/loadout.py --list                                  # session types
"""

import argparse
import sys
from pathlib import Path

import framework_docs as fd


def loadout(src, session, profiles, framework=False):
    """{'always': [paths], 'session': [paths], 'project': [globs], 'note': str|None}.
    `framework`: resolve for the framework repository itself, whose sessions load its
    own documents, root tier included."""
    if session not in src.types:
        raise SystemExit(f"ERROR unknown session type {session}; have {', '.join(src.types)}")
    t = src.types[session]
    docs = src.project_docs(profiles) if not framework and t["scope"] != "framework" else [
        d for d in src.docs.values() if d["fm"] and fd.model_readable(d["fm"])
        and d["fm"].get("status") != "superseded"]
    if (t.get("project_files") or []) == ["**"]:
        return {"always": [d["path"] for d in docs if d["fm"].get("load") == "always"],
                "session": [d["path"] for d in docs if d["fm"].get("load") != "always"],
                "project": ["whatever the question needs; the only type with no ceiling"],
                "note": None}
    always = [d["path"] for d in docs if d["fm"].get("load") == "always"]
    on_task = [d["path"] for d in docs
               if d["fm"].get("load") == "on-task" and session in (d["fm"].get("sessions") or [])]
    project = list(t.get("project_files") or [])
    for f in src.profile_fragments(profiles):
        project += (f.get("loadout") or {}).get(session, [])
    return {"always": always, "session": on_task, "project": project, "note": t.get("loads")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--session")
    ap.add_argument("--profiles", action="append", metavar="NAME[,NAME]", help="repeatable")
    ap.add_argument("--root", help="project root; profiles default to its .hyperion/profiles")
    ap.add_argument("--list", action="store_true", help="print the session types and exit")
    args = ap.parse_args(argv)
    args.profiles = fd.split_profiles(args.profiles)

    import build_layer          # here, not at the top: build_layer's renderers import this module
    src = build_layer.Sources()
    if args.list or not args.session:
        for name, t in src.types.items():
            print(f"{name:12} {t['scope']:10} {t['purpose']}")
        return 0
    profiles = args.profiles
    if profiles is None:
        profiles = build_layer.project_profiles(Path(args.root)) if args.root else []
    out = loadout(src, args.session, profiles)
    print(f"# {args.session}, profiles [{', '.join(profiles) or 'none'}]")
    print("# every session")
    for p in out["always"]:
        print(f"hyperion/{p}")
    print(f"# {args.session}")
    for p in out["session"]:
        print(f"hyperion/{p}")
    if out["project"] or out["note"]:
        print("# project files")
        for p in out["project"]:
            print(p)
        if out["note"]:
            print(f"# {out['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
