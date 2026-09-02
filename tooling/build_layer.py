#!/usr/bin/env python3
"""Render the operating layer from its hand-written sources (CORE-IMP-001, M1).

Everything a session consumes is derived text: the imperative table, the session table,
the stop conditions, the loadout table, the lens library, the agent index, the severity
scale inside every agent prompt, a project's module-map diagram, the imperatives map
with its section hashes, the README status line and a project's `.hyperion/version`
(both from `VERSION`, F-22), and the Claude Code binding (.claude/, .hyperion/session-types.json,
.devcontainer/; rendered by harness.py, CORE-HRN-001). Hand-copied derived text drifts
(P3); this script renders it and --check fails CI when any rendering is stale.

Sources: imperatives/*.yaml and profiles/*/fragment.yaml (CORE-IMP-001), the
session-types block (CORE-SES-001), document frontmatter (TOOL-001), the lens-selection
block (CORE-REV-003), and a project's modules/*/manifest.yaml (CORE-LFC-004).

Usage:
    python tooling/build_layer.py                 # render framework outputs and examples/*
    python tooling/build_layer.py --check         # exit 1 if any rendered output is stale
    python tooling/build_layer.py --project DIR [--profiles NAME ...]   # one project's blocks

A project is any directory with .hyperion/profiles; init_project.py creates it. Project
rendering is what init_project.py --upgrade calls.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

import framework_docs as fd

TIER_ORDER = ["core", "profile", "agents", "templates", "tooling"]
PROJECT_TIERS = {"core", "profile", "agents", "templates", "tooling"}
TEMPLATE = "templates/project-CLAUDE.md"
FRAMEWORK_CLAUDE = "CLAUDE.md"
README = "README.md"
LENS_DOC = "core/reviews/lens-reviews.md"
AGENT_INDEX = "agents/00-agent-index.md"
MAP = "tooling/imperatives.json"


# ------------------------------------------------------------------ sources

class Sources:
    """Every hand-written input, loaded once. `errors` collects source defects."""

    def __init__(self, root=fd.FRAMEWORK_ROOT):
        self.root = Path(root)
        self.docs = fd.collect_docs(self.root)
        self.by_id = fd.docs_by_id(self.docs)
        self.types = fd.session_types(self.root)
        self.core = fd.load_fragment(self.root / "imperatives" / "core.yaml")
        self.framework = fd.load_fragment(self.root / "imperatives" / "framework.yaml")
        self.profiles = {n: fd.profile_fragment(self.root, n) for n in fd.profile_names(self.root)}
        self.agents = sorted(
            (d for d in self.docs.values()
             if d["fm"] and d["fm"].get("tier") == "agents" and "lens" in d["fm"]),
            key=lambda d: (d["fm"].get("profile") or "", d["fm"]["lens"]))
        self.errors = []

    def profile_fragments(self, names):
        for n in names:
            if n not in self.profiles:
                raise SystemExit(f"ERROR unknown profile {n!r}; have {', '.join(self.profiles) or 'none'}")
        return [self.profiles[n] for n in names]

    def imperative_rows(self, fragment, carried_in):
        """Resolve every row of a fragment to its section: text, source path, hash."""
        rows = []
        for imp in fragment["imperatives"]:
            row = {"id": imp["id"], "text": imp["text"], "source": imp["source"],
                   "carried_in": carried_in, "profile": fragment.get("profile")}
            try:
                doc, _, body = fd.resolve_source(self.by_id, imp["source"])
            except ValueError as e:
                self.errors.append(f"{fragment['_path']}: {imp['id']}: {e}")
                continue
            flat = " ".join(body.lower().split())      # anchors may be line-wrapped in the source
            for word in imp.get("anchor") or []:
                if " ".join(word.lower().split()) not in flat:
                    self.errors.append(
                        f"{fragment['_path']}: {imp['id']}: anchor {word!r} not in section "
                        f"{imp['source']}; the rule is not where the row says it is")
            row["source_path"] = doc["path"]
            row["section_hash"] = fd.section_hash(body)
            rows.append(row)
        return rows

    def project_docs(self, profiles):
        """Documents a project with these profiles may load: not root tier, not
        superseded, readable by the model, and a profile's only when chosen."""
        out = []
        for d in self.docs.values():
            fm = d["fm"]
            if not fm or fm.get("tier") not in PROJECT_TIERS or fm.get("status") == "superseded":
                continue
            if not fd.model_readable(fm):
                continue
            if fm["tier"] == "profile" and d["path"].split("/")[1] not in profiles:
                continue
            if fm.get("profile") and fm["profile"] not in profiles:     # a profile's agent
                continue
            out.append(d)
        return sorted(out, key=lambda d: (TIER_ORDER.index(d["fm"]["tier"]), d["fm"]["id"]))


# ------------------------------------------------------------------ renderers

def _globs(items, empty="nothing"):
    if not items:
        return empty
    if items == ["**"]:
        return "everything"
    return ", ".join(f"`{g}`" for g in items)


def render_session_table(types):
    out = ["| Type | May modify | Must not modify |", "|---|---|---|"]
    for name, t in types.items():
        if t["scope"] not in ("project", "both"):
            continue
        may = _globs(t["may_modify"])
        if t.get("note"):
            may += f" ({t['note']})"
        out.append(f"| {name} | {may} | {_globs(t['must_not_modify'], 'nothing')} |")
    return "\n".join(out)


def render_imperatives(rows):
    out = ["| # | Imperative | Source |", "|---|---|---|"]
    for r in rows:
        text = r["text"] + (f" *({r['profile'].capitalize()})*" if r.get("profile") else "")
        out.append(f"| {r['id']} | {text} | {r['source']} |")
    return "\n".join(out)


def render_stop_conditions(core, fragments):
    out = [f"- {c}" for c in core["stop_conditions"]]
    for f in fragments:
        out += [f"- {c} *({f['profile'].capitalize()})*" for c in f["stop_conditions"]]
    return "\n".join(out)


def render_loadout(src, profiles, fragments):
    docs = src.project_docs(profiles)
    ids = lambda pred: [d["fm"]["id"] for d in docs if pred(d["fm"])]
    out = ["| Session | Load |", "|---|---|",
           f"| every session | {', '.join(ids(lambda fm: fm.get('load') == 'always'))} |"]
    for name, t in src.types.items():
        if t["scope"] not in ("project", "both"):
            continue
        files = list(t.get("project_files") or [])
        if files == ["**"]:
            out.append(f"| {name} | whatever the question needs; the only type with no ceiling |")
            continue
        parts = ids(lambda fm: fm.get("load") == "on-task" and name in (fm.get("sessions") or []))
        for f in fragments:
            files += (f.get("loadout") or {}).get(name, [])
        parts += [f"`{p}`" for p in files]
        if t.get("loads"):
            parts.append(t["loads"])
        out.append(f"| {name} | {', '.join(parts) or 'nothing beyond the standing set'} |")
    return "\n".join(out)


def render_targeted_reads(src, fragments):
    lines = []
    for f in fragments:
        for doc_id in f.get("targeted_reads") or []:
            doc = src.by_id.get(doc_id)
            if doc is None:
                src.errors.append(f"{f['_path']}: targeted_reads names unknown id {doc_id}")
                continue
            items = [re.sub(r"^\d+\.\s*", "", h) for lvl, _, h, _ in fd.sections(doc["body"])
                     if lvl == 2 and re.match(r"^\d+\.", h)]
            items = [i[0].lower() + i[1:] for i in items]
            lines.append(f"- [ ] Targeted human reads done ({doc_id}): {'; '.join(items)}")
    if not lines:
        lines.append("- [ ] Targeted human reads done (CORE-REV-004)")
    return "\n".join(lines)


def lens_selection(src):
    doc = src.docs[LENS_DOC]
    block = fd.fenced_block(doc["body"], "yaml lens-selection")
    if block is None:
        src.errors.append(f"{LENS_DOC}: no ```yaml lens-selection``` block")
        return {}
    return yaml.safe_load(block) or {}


def unwritten_lenses(src):
    named = {n for names in lens_selection(src).values() for n in names}
    written = {a["fm"]["lens"] for a in src.agents}
    return sorted(named - written)


def render_lens_library(src):
    out = ["| Lens | Looks for | Profile | Agent |", "|---|---|---|---|"]
    for a in src.agents:
        fm, name = a["fm"], Path(a["path"]).stem
        out.append(f"| {fm['lens']} | {fm['question']} | {fm.get('profile') or 'core'} "
                   f"| [{name}](../../agents/{name}.md) |")
    for lens in unwritten_lenses(src):
        out.append(f"| {lens} | *(not yet written; named in the selection block)* | — | — |")
    return "\n".join(out)


def render_agent_index(src):
    groups = {}
    for a in src.agents:
        groups.setdefault(a["fm"].get("profile") or "core", []).append(a)
    out = []
    for group, agents in groups.items():
        title = "Core agents" if group == "core" else f"{group.capitalize()} profile agents"
        out += [f"## {title}", "", "| Agent | Question | Run when | Model |", "|---|---|---|---|"]
        for a in agents:
            fm, name = a["fm"], Path(a["path"]).stem
            out.append(f"| [{name}]({name}.md) | {fm['question']} | {fm['run_when']} | {fm['model']} |")
        out.append("")
    missing = unwritten_lenses(src)
    if missing:
        out += ["## Not yet written", "",
                "Named in the selection block of CORE-REV-003 with no agent file: "
                + ", ".join(missing) + ". Write one when a slice first needs it, not in advance."]
    return "\n".join(out)


def render_tier_rows(fragment):
    out = ["| Path touched | Tier |", "|---|---|"]
    out += [f"| `{r['path']}` | {r['tier']} |" for r in fragment.get("tier_rows") or []]
    return "\n".join(out)


def render_module_map(project_root):
    """Mermaid dependency diagram from modules/*/manifest.yaml (CORE-LFC-004)."""
    node = lambda name: re.sub(r"[^A-Za-z0-9_]", "_", name)
    baseline, edges = [], []
    for manifest in sorted(Path(project_root).glob("modules/*/manifest.yaml")):
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        module = data.get("module") or manifest.parent.name
        for imp in data.get("allowed_imports") or []:
            if imp.startswith("baseline/"):
                target = imp.split("/", 1)[1]
                if target not in baseline:
                    baseline.append(target)
                edges.append(f"    {node(module)}[{module}] --> baseline_{node(target)}")
            elif imp.startswith("modules/"):
                target = imp.split("/")[1]
                edges.append(f"    {node(module)}[{module}] --> {node(target)}[{target}]")
            else:
                edges.append(f"    {node(module)}[{module}] --> {node(imp)}[{imp}]")
    out = ["```mermaid", "flowchart LR"]
    if baseline:
        out.append("    subgraph baseline")
        out += [f"        baseline_{node(b)}[{b}]" for b in baseline]
        out.append("    end")
    out += edges or ["    none[no manifests yet]"]
    out.append("```")
    return "\n".join(out)


def render_version_status(root):
    """The README status line (F-22): the one place outside VERSION that states the
    version, and it is rendered."""
    return (f"Version {fd.framework_version(root)}, from `VERSION`; the history is in "
            "`CHANGELOG.md`, and a release tag must equal `v$(cat VERSION)`.")


def render_map(rows, existing, comment):
    """imperatives.json. A hash is carried forward from `existing` when the row's source
    is unchanged, so only check_imperatives.py --accept re-records one (CORE-IMP-001)."""
    prior = {r["id"]: r for r in (existing or {}).get("imperatives", [])}
    out = []
    for r in rows:
        keep = prior.get(r["id"])
        h = keep["section_hash"] if keep and keep.get("source") == r["source"] else r["section_hash"]
        out.append({"id": r["id"], "text": r["text"], "source": r["source"],
                    "source_path": r["source_path"], "section_hash": h,
                    "carried_in": r["carried_in"]})
    return json.dumps({"_comment": comment, "imperatives": out}, indent=2) + "\n"


# ------------------------------------------------------------------ outputs

def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _filled(path, renders, src):
    text = fd.read(path)
    new, unknown = fd.fill_blocks(text, renders)
    for name in unknown:
        src.errors.append(f"{path}: generated block {name!r} has no renderer")
    return new


def framework_outputs(src):
    """{path: rendered text} for every generated output in the framework repository."""
    core_rows = src.imperative_rows(src.core, TEMPLATE)
    fw_rows = src.imperative_rows(src.framework, src.framework.get("carried_in", FRAMEWORK_CLAUDE))
    profile_rows = []
    for name, frag in src.profiles.items():
        profile_rows += src.imperative_rows(frag, frag["_path"])
    out = {}
    root = src.root
    out[TEMPLATE] = _filled(root / TEMPLATE, {
        "session-table": render_session_table(src.types),
        "imperatives": render_imperatives(core_rows),
        "stop-conditions": render_stop_conditions(src.core, []),
        "loadout": render_loadout(src, [], []),
        "targeted-reads": render_targeted_reads(src, []),
    }, src)
    out[FRAMEWORK_CLAUDE] = _filled(root / FRAMEWORK_CLAUDE, {"imperatives": render_imperatives(fw_rows)}, src)
    out[README] = _filled(root / README, {"version": render_version_status(root)}, src)
    out[LENS_DOC] = _filled(root / LENS_DOC, {"lens-library": render_lens_library(src)}, src)
    out[AGENT_INDEX] = _filled(root / AGENT_INDEX, {"agent-index": render_agent_index(src)}, src)
    for name, frag in src.profiles.items():
        for rel, d in src.docs.items():
            if rel.startswith(f"profiles/{name}/") and "tier-rows" in fd.block_names(d["body"]):
                out[rel] = _filled(root / rel, {"tier-rows": render_tier_rows(frag)}, src)
    for a in src.agents:
        try:
            out[a["path"]] = fd.fill_includes(fd.read(root / a["path"]), src.by_id)
        except ValueError as e:
            src.errors.append(f"{a['path']}: {e}")
    import harness              # here, not at the top: harness imports this module's renderers
    for path, text in harness.outputs(src, root, [], framework=True, name="hyperion").items():
        out[Path(path).relative_to(root).as_posix()] = text
    all_rows = fw_rows + core_rows + profile_rows
    seen = set()
    for r in all_rows:
        if r["id"] in seen:
            src.errors.append(f"duplicate imperative id {r['id']} across fragments")
        seen.add(r["id"])
    out[MAP] = render_map(all_rows, _read_json(root / MAP),
                          "Generated by tooling/build_layer.py from imperatives/*.yaml and "
                          "profiles/*/fragment.yaml (CORE-IMP-001). Edit a fragment, not this file; "
                          "check_imperatives.py --accept re-records a section hash.")
    return out


def project_profiles(project):
    path = Path(project) / ".hyperion" / "profiles"
    return path.read_text(encoding="utf-8").split() if path.exists() else []


def project_outputs(src, project, profiles):
    """{path: rendered text} for one project's generated blocks and map."""
    project = Path(project)
    fragments = src.profile_fragments(profiles)
    rows = src.imperative_rows(src.core, "CLAUDE.md")
    for f in fragments:
        rows += src.imperative_rows(f, "CLAUDE.md")
    out = {}
    claude = project / "CLAUDE.md"
    if claude.exists():
        out[claude] = _filled(claude, {
            "session-table": render_session_table(src.types),
            "imperatives": render_imperatives(rows),
            "stop-conditions": render_stop_conditions(src.core, fragments),
            "loadout": render_loadout(src, profiles, fragments),
            "targeted-reads": render_targeted_reads(src, fragments),
        }, src)
    module_map = project / "docs" / "module-map.md"
    if module_map.exists():
        out[module_map] = _filled(module_map, {"module-map": render_module_map(project)}, src)
    out[project / ".hyperion" / "version"] = fd.framework_version(src.root) + "\n"
    out[project / ".hyperion" / "imperatives.json"] = render_map(
        rows, None, f"Generated by init_project.py for profiles [{', '.join(profiles)}] at the "
                    "framework version in .hyperion/version (CORE-IMP-001). Regenerate with "
                    "init_project.py --upgrade; never edit or --accept.")
    import harness              # here, not at the top: harness imports this module's renderers
    out.update(harness.outputs(src, project, profiles, framework=False, name=project.name))
    return out


def apply(outputs, check):
    """Write, or in check mode compare. Returns the list of stale paths."""
    stale = []
    for path, text in outputs.items():
        path = Path(path)
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != text:
            stale.append(path)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    return stale


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any output is stale")
    ap.add_argument("--project", help="render one project's generated blocks instead")
    ap.add_argument("--profiles", action="append", metavar="NAME[,NAME]",
                    help="profile for --project, repeatable (default: .hyperion/profiles)")
    args = ap.parse_args(argv)
    args.profiles = fd.split_profiles(args.profiles)

    src = Sources()
    root = src.root
    if args.project:
        profiles = args.profiles if args.profiles is not None else project_profiles(args.project)
        outputs = project_outputs(src, args.project, profiles)
    else:
        outputs = {root / rel: text for rel, text in framework_outputs(src).items()}
        for marker in sorted(root.glob("examples/*/.hyperion/profiles")):
            project = marker.parent.parent
            outputs.update(project_outputs(src, project, project_profiles(project)))

    if src.errors:
        for e in dict.fromkeys(src.errors):      # a fragment is resolved once per carrier
            print(f"ERROR {e}", file=sys.stderr)
        return 1

    stale = apply(outputs, args.check)
    rel = lambda p: Path(p).resolve().relative_to(root).as_posix() if str(p).startswith(str(root)) else str(p)
    if args.check:
        for p in stale:
            print(f"ERROR stale generated output: {rel(p)}", file=sys.stderr)
        if stale:
            print("Run: python tooling/build_layer.py", file=sys.stderr)
            return 1
        print(f"OK {len(outputs)} generated outputs current")
        return 0
    for p in stale:
        print(f"Wrote {rel(p)}")
    if not stale:
        print(f"OK {len(outputs)} generated outputs already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
