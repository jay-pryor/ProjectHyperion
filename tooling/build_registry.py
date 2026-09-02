#!/usr/bin/env python3
"""Generate REGISTRY.md from document frontmatter.

The registry is generated, never hand-maintained: a hand-maintained index rots, and a
rotted index is worse than none because it is trusted.

Usage:
    python tooling/build_registry.py           # regenerate REGISTRY.md
    python tooling/build_registry.py --check   # exit 1 if stale or invalid (CI)
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "REGISTRY.md"

REQUIRED = ["id", "title", "tier", "status", "version", "audience", "load"]
TIER_ORDER = ["root", "core", "profile", "agents", "templates", "tooling"]

FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text):
    """Minimal YAML subset: scalars and inline lists. Avoids a PyYAML dependency."""
    m = FM.match(text)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [v.strip().strip("\"'") for v in inner.split(",") if v.strip()]
        else:
            data[key] = val.strip("\"'")
    return data


def collect():
    docs, errors = [], []
    for path in sorted(ROOT.rglob("*.md")):
        # examples/ holds project files built *under* the framework, not framework
        # documents; they carry no frontmatter and are not registered. Their body
        # citations are still checked below.
        if path == REGISTRY or ".git" in path.parts or "examples" in path.parts:
            continue
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT).as_posix()
        if fm is None:
            errors.append(f"{rel}: missing frontmatter")
            continue
        missing = [f for f in REQUIRED if f not in fm]
        if missing:
            errors.append(f"{rel}: missing field(s) {', '.join(missing)}")
            continue
        fm["path"] = rel
        docs.append(fm)

    seen = {}
    for d in docs:
        if d["id"] in seen:
            errors.append(f"duplicate id {d['id']}: {seen[d['id']]} and {d['path']}")
        seen[d["id"]] = d["path"]

    known = set(seen)
    for d in docs:
        for ref in d.get("related", []):
            if ref not in known:
                errors.append(f"{d['path']}: related references unknown id {ref}")

    # A human-only document must never sit in the standing model loadout: it would
    # consume context budget in every session and prevent nothing.
    for d in docs:
        if d.get("load") == "always" and d.get("audience") == ["human"]:
            errors.append(
                f"{d['path']}: load=always but audience=[human]; "
                "human-only docs must be on-task or reference"
            )

    # Every Hyperion ID cited in body text must resolve. This is what stops the
    # CLAUDE.md operating layer drifting away from the documents it points at.
    id_pat = re.compile(r"\b((?:HYP|CORE|SIM|AGT|TPL|TOOL)-[A-Z]{0,3}-?\d{3})\b")
    for path in sorted(ROOT.rglob("*.md")):
        if path == REGISTRY or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        body = FM.sub("", path.read_text(encoding="utf-8"))
        for ref in sorted(set(id_pat.findall(body))):
            if ref not in known:
                errors.append(f"{rel}: body cites unknown id {ref}")

    return docs, errors


def render(docs):
    def tier_key(d):
        t = d.get("tier", "")
        return (TIER_ORDER.index(t) if t in TIER_ORDER else 99, d["path"])

    out = [
        "---",
        "id: HYP-001",
        "title: Registry",
        "tier: root",
        "status: active",
        "version: 0.1",
        "audience: [human, model]",
        "load: reference",
        "related: [HYP-000]",
        "---",
        "",
        "# Registry",
        "",
        "<!-- GENERATED FILE — do not edit. Run: python tooling/build_registry.py -->",
        "",
        f"Generated {date.today().isoformat()} · {len(docs)} documents",
        "",
    ]

    always = [d for d in sorted(docs, key=tier_key) if d.get("load") == "always"]
    out += ["## Standing context loadout", "",
            "Documents tagged `load: always`. Keep this list short — every entry costs",
            "context budget in every session.", ""]
    out += [f"- `{d['id']}` [{d['title']}]({d['path']})" for d in always]
    out.append("")

    for tier in TIER_ORDER:
        rows = [d for d in sorted(docs, key=tier_key) if d.get("tier") == tier]
        if not rows:
            continue
        out += [f"## {tier}", "", "| ID | Title | Status | Load | Path |",
                "|---|---|---|---|---|"]
        for d in rows:
            out.append(
                f"| `{d['id']}` | {d['title']} | {d['status']} | "
                f"{d['load']} | [{d['path']}]({d['path']}) |"
            )
        out.append("")

    drafts = [d for d in docs if d.get("status") == "draft"]
    if drafts:
        out += ["## Draft documents", ""]
        out += [f"- `{d['id']}` {d['title']}" for d in sorted(drafts, key=tier_key)]
        out.append("")

    return "\n".join(out) + "\n"


def main():
    check = "--check" in sys.argv
    docs, errors = collect()

    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    content = render(docs)

    if check:
        current = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else ""
        # Ignore the generation date line when comparing.
        strip = lambda s: "\n".join(
            l for l in s.splitlines() if not l.startswith("Generated ")
        )
        if strip(current) != strip(content):
            print("ERROR REGISTRY.md is stale. Run: python tooling/build_registry.py",
                  file=sys.stderr)
            return 1
        print(f"OK {len(docs)} documents, registry current")
        return 0

    REGISTRY.write_text(content, encoding="utf-8")
    print(f"Wrote {REGISTRY.relative_to(ROOT)} ({len(docs)} documents)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
