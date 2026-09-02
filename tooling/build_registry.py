#!/usr/bin/env python3
"""Generate REGISTRY.md from document frontmatter and validate the frontmatter (TOOL-001).

The registry is generated, never hand-maintained: a hand-maintained index rots, and a
rotted index is worse than none because it is trusted. --check also validates what the
schema demands: required fields, unique IDs, resolving `related`, `sessions` on every
on-task document naming real session types, `load: never` only on human-only documents, agent fields on every lens, no human-only
document in the standing loadout, and every ID cited in any body resolving. The ID
pattern is built from the IDs actually found, so a new prefix needs no script change.

Usage:
    python tooling/build_registry.py           # regenerate REGISTRY.md
    python tooling/build_registry.py --check   # exit 1 if stale or invalid (CI)
"""

import re
import sys
from datetime import date
from pathlib import Path

import framework_docs as fd

ROOT = fd.FRAMEWORK_ROOT
REGISTRY = ROOT / fd.REGISTRY

REQUIRED = ["id", "title", "tier", "status", "version", "audience", "load"]
AGENT_FIELDS = ["lens", "question", "run_when", "model"]
TIER_ORDER = ["root", "handbook", "core", "profile", "agents", "templates", "tooling"]
LOADS = {"always", "on-task", "reference", "never"}


def validate(docs, types):
    errors = []
    profiles = set(fd.profile_names(ROOT)) | {p.name for p in (ROOT / "profiles").iterdir() if p.is_dir()}
    for d in docs.values():
        fm, rel = d["fm"], d["path"]
        if fm is None:
            errors.append(f"{rel}: missing frontmatter")
            continue
        missing = [f for f in REQUIRED if f not in fm]
        if missing:
            errors.append(f"{rel}: missing field(s) {', '.join(missing)}")
            continue
        if fm["load"] not in LOADS:
            errors.append(f"{rel}: load must be one of {sorted(LOADS)}")
        if fm["load"] == "on-task":
            if "sessions" not in fm or not isinstance(fm["sessions"], list):
                errors.append(f"{rel}: load=on-task requires a sessions: list (TOOL-001)")
            else:
                for s in fm["sessions"]:
                    if s not in types:
                        errors.append(f"{rel}: sessions names unknown session type {s}")
        elif fm["load"] == "never":
            if fm.get("audience") != ["human"] or fm.get("sessions") != []:
                errors.append(f"{rel}: load=never means audience: [human] and sessions: [] (TOOL-001)")
        elif "sessions" in fm:
            errors.append(f"{rel}: sessions is only meaningful with load: on-task or never")
        if fm["load"] == "always" and fm.get("audience") == ["human"]:
            errors.append(f"{rel}: load=always but audience=[human]; "
                          "human-only docs must be on-task or reference")
        if fm["tier"] == "agents" and rel != "agents/00-agent-index.md":
            for f in AGENT_FIELDS:
                if f not in fm:
                    errors.append(f"{rel}: agent file lacks {f}: (TOOL-001)")
            if fm.get("model") not in fd.MODEL_ALIASES:
                errors.append(f"{rel}: model must be one of {', '.join(fd.MODEL_ALIASES)}")
            if fm.get("profile") and fm["profile"] not in profiles:
                errors.append(f"{rel}: profile {fm['profile']!r} has no profiles/ directory")

    valid = [d for d in docs.values() if d["fm"] and all(f in d["fm"] for f in REQUIRED)]
    seen = {}
    for d in valid:
        if d["fm"]["id"] in seen:
            errors.append(f"duplicate id {d['fm']['id']}: {seen[d['fm']['id']]} and {d['path']}")
        seen[d["fm"]["id"]] = d["path"]
    known = set(seen)
    for d in valid:
        for ref in d["fm"].get("related") or []:
            if ref not in known:
                errors.append(f"{d['path']}: related references unknown id {ref}")

    # Every Hyperion ID cited in any body must resolve, including in examples/. The
    # pattern comes from the prefixes in use, so a new profile needs no script edit.
    prefixes = sorted({i.split("-")[0] for i in known})
    id_pat = re.compile(r"\b((?:" + "|".join(map(re.escape, prefixes)) + r")-[A-Z]{0,3}-?\d{3})\b")
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        _, body = fd.split_frontmatter(fd.read(path))
        for ref in sorted(set(id_pat.findall(body))):
            if ref not in known:
                errors.append(f"{path.relative_to(ROOT).as_posix()}: body cites unknown id {ref}")
    return valid, errors


def render(docs):
    def tier_key(d):
        t = d["fm"].get("tier", "")
        return (TIER_ORDER.index(t) if t in TIER_ORDER else 99, d["path"])

    docs = sorted(docs, key=tier_key)
    out = ["---", "id: HYP-001", "title: Registry", "tier: root", "status: active",
           "version: 0.1", "audience: [human, model]", "load: reference", "related: [HYP-000]",
           "---", "", "# Registry", "",
           "<!-- GENERATED FILE — do not edit. Run: python tooling/build_registry.py -->", "",
           f"Generated {date.today().isoformat()} · {len(docs)} documents", ""]

    out += ["## Standing context loadout", "",
            "Documents tagged `load: always`. Keep this list short — every entry costs",
            "context budget in every session.", ""]
    out += [f"- `{d['fm']['id']}` [{d['fm']['title']}]({d['path']})" for d in docs if d["fm"]["load"] == "always"]
    out.append("")

    for tier in TIER_ORDER:
        rows = [d for d in docs if d["fm"].get("tier") == tier]
        if not rows:
            continue
        out += [f"## {tier}", "", "| ID | Title | Status | Load | Sessions | Path |",
                "|---|---|---|---|---|---|"]
        for d in rows:
            fm = d["fm"]
            sessions = ", ".join(fm.get("sessions") or []) if fm["load"] == "on-task" else ""
            out.append(f"| `{fm['id']}` | {fm['title']} | {fm['status']} | {fm['load']} | "
                       f"{sessions} | [{d['path']}]({d['path']}) |")
        out.append("")

    drafts = [d for d in docs if d["fm"].get("status") == "draft"]
    if drafts:
        out += ["## Draft documents", ""]
        out += [f"- `{d['fm']['id']}` {d['fm']['title']}" for d in drafts]
        out.append("")
    return "\n".join(out) + "\n"


def main():
    check = "--check" in sys.argv
    try:
        types = fd.session_types(ROOT)
    except ValueError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 1
    docs, errors = validate(fd.collect_docs(ROOT), types)
    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    content = render(docs)
    if check:
        current = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
        strip = lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("Generated "))
        if strip(current) != strip(content):
            print("ERROR REGISTRY.md is stale. Run: python tooling/build_registry.py", file=sys.stderr)
            return 1
        print(f"OK {len(docs)} documents, registry current")
        return 0

    REGISTRY.write_text(content, encoding="utf-8")
    print(f"Wrote {REGISTRY.relative_to(ROOT)} ({len(docs)} documents)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
