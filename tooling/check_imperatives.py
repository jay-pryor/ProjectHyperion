#!/usr/bin/env python3
"""Flag imperatives whose source document has changed since last confirmation.

CLAUDE.md carries imperatives; core carries the rules they derive from. The two can
drift silently: a rule changes in core, the imperative keeps the old wording, and the
session obeys the stale one. Nothing about the artifacts reveals this.

This does not prove an imperative is still correct. It forces someone to look.

Usage:
    python tooling/check_imperatives.py            # CI: exit 1 on drift
    python tooling/check_imperatives.py --accept   # re-record hashes after confirming
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = Path(__file__).resolve().parent / "imperatives.json"
FM = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def body_hash(path):
    """Hash the document body, excluding frontmatter, so version and status bumps
    do not trigger a spurious review."""
    text = (ROOT / path).read_text(encoding="utf-8")
    return hashlib.sha256(FM.sub("", text).encode("utf-8")).hexdigest()[:16]


def main():
    accept = "--accept" in sys.argv
    if not MAP.exists():
        print(f"ERROR missing {MAP.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = json.loads(MAP.read_text(encoding="utf-8"))
    drift, missing = [], []

    for imp in data["imperatives"]:
        src = imp["source_path"]
        if not (ROOT / src).exists():
            missing.append(f"{imp['id']}: source {src} does not exist")
            continue
        current = body_hash(src)
        if current != imp["source_hash"]:
            drift.append((imp, current))
            if accept:
                imp["source_hash"] = current

    for m in missing:
        print(f"ERROR {m}", file=sys.stderr)

    if accept:
        MAP.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Re-recorded {len(drift)} source hash(es)")
        return 1 if missing else 0

    if drift:
        print("Source documents changed since these imperatives were last confirmed:\n",
              file=sys.stderr)
        for imp, _ in drift:
            print(f"  {imp['id']}  [{imp['source_id']}]  in {imp['carried_in']}",
                  file=sys.stderr)
            print(f"      \"{imp['text']}\"", file=sys.stderr)
            print(f"      re-read {imp['source_path']}, then --accept\n", file=sys.stderr)

    if drift or missing:
        return 1

    print(f"OK {len(data['imperatives'])} imperatives, all sources unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
