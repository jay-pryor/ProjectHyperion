#!/usr/bin/env python3
"""Generate REGISTRY.md from document frontmatter and validate the documents (TOOL-001).

The registry is generated, never hand-maintained: a hand-maintained index rots, and a
rotted index is worse than none because it is trusted. --check also validates what the
schema demands: required fields (`prevents` and `reader` among them, P6), unique IDs,
resolving `related`, `sessions` on every on-task document naming real session types,
`load: never` only on human-only documents, agent fields on every lens, `superseded_by`
exactly when `status: superseded`, no human-only document in the standing loadout, and
every ID cited in any body resolving. Three rules the framework CLAUDE.md used to state
in prose are checks here (F-21, P2): the line limit per tier, the principle trace of every
core and profile document, and the duplicate-sentence rule (F-19, P3). The ID pattern is
built from the IDs actually found, so a new prefix needs no script change.

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

REQUIRED = ["id", "title", "tier", "status", "audience", "load", "prevents", "reader"]
AGENT_FIELDS = ["lens", "question", "run_when", "model"]
TIER_ORDER = ["root", "handbook", "core", "profile", "agents", "templates", "tooling"]
LOADS = {"always", "on-task", "reference", "never"}
STATUSES = {"draft", "active", "superseded"}

# F-21: a document that needs more lines is usually two documents. Root and tooling
# documents are not limited here: the registry is generated, and CLAUDE.md's own limit is
# a rule of that file.
LINE_LIMIT = {"core": 120, "profile": 120, "handbook": 120, "agents": 120, "templates": 160}
PRINCIPLE_TIERS = {"core", "profile"}          # every body cites a principle, transitively
DUPLICATE_TIERS = {"core", "profile"}          # one fact, one place (P3)
DUPLICATE_MIN_WORDS = 12
PRINCIPLE_RE = re.compile(r"\bP(?:10|[1-9])\b")
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def id_pattern(known_ids):
    """Regex for any Hyperion ID, from the prefixes in use."""
    prefixes = sorted({i.split("-")[0] for i in known_ids})
    return re.compile(r"\b((?:" + "|".join(map(re.escape, prefixes)) + r")-[A-Z]{0,3}-?\d{3})\b")


# ------------------------------------------------------------------ the three prose rules

def line_limit_errors(docs, root=ROOT):
    """Tier line limits (F-21). Counted over the whole file, frontmatter included."""
    errors = []
    for d in docs:
        limit = LINE_LIMIT.get(d["fm"].get("tier"))
        if limit is None:
            continue
        lines = len(fd.read(Path(root) / d["path"]).splitlines())
        if lines > limit:
            errors.append(f"{d['path']}: {lines} lines exceeds the {limit}-line limit for tier "
                          f"{d['fm']['tier']}; split it (TOOL-001)")
    return errors


def principle_trace_errors(docs):
    """Every core and profile body cites P<n>, or an ID whose document does, transitively
    (F-21; HYP-002 rule 1). Documents are the nodes, body citations the edges."""
    by_id = {d["fm"]["id"]: d for d in docs}
    id_pat = id_pattern(by_id)
    cites = {i: set(id_pat.findall(d["body"])) - {i} for i, d in by_id.items()}
    traced = {i for i, d in by_id.items() if PRINCIPLE_RE.search(d["body"])}
    changed = True
    while changed:
        changed = False
        for i in by_id:
            if i not in traced and cites[i] & traced:
                traced.add(i)
                changed = True
    return [f"{d['path']}: cites no principle (P1-P10), directly or through a cited document"
            for i, d in by_id.items()
            if d["fm"].get("tier") in PRINCIPLE_TIERS and i not in traced]


def prose_sentences(body):
    """Normalised sentences of a body with generated and include blocks removed: those are
    rendered copies by design, not restatements."""
    text = fd.GENERATED_RE.sub(" ", body)
    text = fd.INCLUDE_RE.sub(" ", text)
    out = []
    for sentence in SENTENCE_END_RE.split(" ".join(text.split())):
        sentence = sentence.strip()
        if len(sentence.split()) > DUPLICATE_MIN_WORDS:
            out.append(sentence)
    return out


def duplicate_sentence_errors(docs):
    """A sentence of more than DUPLICATE_MIN_WORDS words in two documents of the checked
    tiers is a restatement, and restatements drift (F-19, P3). Link by ID instead."""
    seen = {}
    errors = []
    for d in sorted(docs, key=lambda d: d["path"]):
        if d["fm"].get("tier") not in DUPLICATE_TIERS:
            continue
        for sentence in set(prose_sentences(d["body"])):
            first = seen.setdefault(sentence, d["path"])
            if first != d["path"]:
                errors.append(f"{d['path']} repeats a sentence of {first}: \"{sentence[:70]}...\" "
                              "(P3: keep it where its failure is prevented, link by ID elsewhere)")
    return errors


# ------------------------------------------------------------------ frontmatter

def validate(docs, types):
    errors = []
    profiles = set(fd.profile_names(ROOT)) | {p.name for p in (ROOT / "profiles").iterdir() if p.is_dir()}
    for d in docs.values():
        fm, rel = d["fm"], d["path"]
        if fm is None:
            errors.append(f"{rel}: missing frontmatter")
            continue
        if rel == fd.REGISTRY:      # rendered below; validating it would block a schema change
            continue
        missing = [f for f in REQUIRED if f not in fm]
        if missing:
            errors.append(f"{rel}: missing field(s) {', '.join(missing)}")
            continue
        if "version" in fm:
            errors.append(f"{rel}: version: is no longer a document field; VERSION and git history are (F-22)")
        if fm["status"] not in STATUSES:
            errors.append(f"{rel}: status must be one of {sorted(STATUSES)}")
        if (fm["status"] == "superseded") != ("superseded_by" in fm):
            errors.append(f"{rel}: superseded_by is required when status: superseded and forbidden otherwise (TOOL-001)")
        for f in ("prevents", "reader"):
            if not isinstance(fm[f], str) or len(fm[f].split()) < 4:
                errors.append(f"{rel}: {f}: must be a sentence naming the specific failure or reader (P6)")
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

    valid = [d for d in docs.values()
             if d["fm"] and (d["path"] == fd.REGISTRY or all(f in d["fm"] for f in REQUIRED))]
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
        if d["fm"].get("superseded_by") and d["fm"]["superseded_by"] not in known:
            errors.append(f"{d['path']}: superseded_by references unknown id {d['fm']['superseded_by']}")

    # Every Hyperion ID cited in any body must resolve, including in examples/.
    id_pat = id_pattern(known)
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        _, body = fd.split_frontmatter(fd.read(path))
        for ref in sorted(set(id_pat.findall(body))):
            if ref not in known:
                errors.append(f"{path.relative_to(ROOT).as_posix()}: body cites unknown id {ref}")

    errors += line_limit_errors(valid)
    errors += principle_trace_errors(valid)
    errors += duplicate_sentence_errors(valid)
    return valid, errors


# ------------------------------------------------------------------ rendering

REGISTRY_FM = {"id": "HYP-001", "title": "Registry", "tier": "root", "status": "active",
               "audience": "[human, model]", "load": "reference",
               "prevents": "A hand-maintained index that rots and is trusted anyway",
               "reader": "Anyone locating a document by ID or tier; never loaded by a session",
               "related": "[HYP-000]"}


def render(docs, version):
    def tier_key(d):
        t = d["fm"].get("tier", "")
        return (TIER_ORDER.index(t) if t in TIER_ORDER else 99, d["path"])

    # The registry's own row comes from the constants above, not from the file on disk,
    # so one run converges after a schema change.
    docs = [dict(d, fm=REGISTRY_FM) if d["path"] == fd.REGISTRY else d for d in docs]
    docs = sorted(docs, key=tier_key)
    out = ["---", *(f"{k}: {v}" for k, v in REGISTRY_FM.items()),
           "---", "", "# Registry", "",
           "<!-- GENERATED FILE — do not edit. Run: python tooling/build_registry.py -->", "",
           f"Hyperion {version} (from `VERSION`; history in `CHANGELOG.md`)", "",
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
        out += [f"## {tier}", "", "| ID | Title | Status | Load | Sessions | Prevents | Path |",
                "|---|---|---|---|---|---|---|"]
        for d in rows:
            fm = d["fm"]
            sessions = ", ".join(fm.get("sessions") or []) if fm["load"] == "on-task" else ""
            out.append(f"| `{fm['id']}` | {fm['title']} | {fm['status']} | {fm['load']} | "
                       f"{sessions} | {fm['prevents']} | [{d['path']}]({d['path']}) |")
        out.append("")

    drafts = [d for d in docs if d["fm"].get("status") == "draft"]
    if drafts:
        out += ["## Draft documents", ""]
        out += [f"- `{d['fm']['id']}` {d['fm']['title']}" for d in drafts]
        out.append("")
    superseded = [d for d in docs if d["fm"].get("status") == "superseded"]
    if superseded:
        out += ["## Superseded documents", "", "Excluded from every loadout; each points forward.", ""]
        out += [f"- `{d['fm']['id']}` {d['fm']['title']} → `{d['fm']['superseded_by']}`" for d in superseded]
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

    content = render(docs, fd.framework_version(ROOT))
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
