#!/usr/bin/env python3
"""Render a project's whole state to one static HTML file: the project console (M8).

Gate reached, active slice, open findings, and the matrix otherwise live in a human's
head or in a hand-copied CLAUDE.md section, and a reviewer who does not read code has no
one place to look. This script renders every record in trace/, the module manifests and
contracts, the slice definitions, the decision records, the lessons file, and the
framework documents at the pinned version into a single page. It is a pure function of
the repository: same inputs, byte-identical output, no timestamps. It has no write path
back to any record. Rationale: CORE-TRC-001 (the review artifact) and P5, P6.

It renders over the checker's own data and verdict (check_traces.load and .check), so
the console and the checker cannot disagree. Over a broken chain the page opens with a
red banner listing the errors and shows no green anywhere (F-14).

Usage (from the project root, or pass the root):
    python tooling/build_console.py <project_root> [--framework DIR] [--out console/index.html]

--framework defaults to <project_root>/hyperion/ when it exists, else the repository this
script belongs to. Mermaid diagrams are drawn by a script fetched from cdn.jsdelivr.net;
everything else works offline. Requires PyYAML.
"""

import argparse
import html
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

import check_traces as ct
import framework_docs as fd
import markdown_lite as md
from build_registry import TIER_ORDER

MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"
G0_QUESTIONS = [("not_performed", "does not happen"), ("performed_incorrectly", "happens incorrectly"),
                ("performed_wrong_time", "happens at the wrong time"),
                ("performed_uncommanded", "happens when not commanded"), ("failed_silently", "fails silently")]
CLAUSE_LINE_RE = re.compile(r"^\s*[-*]\s+\*\*(C-\d{3})\*\*\s*(.*)$")
VERSION_RE = re.compile(r"^Version:\s*([^\s·]+)", re.MULTILINE)
CLAUSE_TEST_RE = re.compile(r"_C(\d{3})(?:\[|$)")
ORDER_RISK_RE = re.compile(r"Order:\s*(\S+)\s*·\s*Risk:\s*(\S+)")
KV_RE = re.compile(r"^(Date|Status|Tier):\s*(.+)$", re.MULTILINE)
COST_RE = re.compile(r"Cost to undo:\s*(.+)")

# Which framework document explains each view (the console section's table). Only ids
# present in the loaded framework become links.
EXPLAINS = {
    "overview": ["CORE-LFC-001", "HBK-001"],
    "hazards": ["CORE-LFC-002", "TPL-004"],
    "requirements": ["CORE-LFC-003", "CORE-TRC-001"],
    "modules": ["CORE-LFC-004", "CORE-CON-001"],
    "plan": ["CORE-LFC-005", "CORE-LFC-006"],
    "findings": ["CORE-REV-001", "CORE-REV-005"],
    "decisions": ["CORE-DEC-001", "CORE-LSN-001", "CORE-CHG-002"],
    "handbook": ["HBK-000"],
}
VIEWS = [("overview", "Overview"), ("hazards", "Hazards"), ("requirements", "Requirements and matrix"),
         ("modules", "Module map"), ("plan", "Plan"), ("findings", "Findings and reviews"),
         ("decisions", "Decisions, lessons, changes"), ("handbook", "Handbook")]


# ------------------------------------------------------------------ small helpers

def esc(value):
    return html.escape("" if value is None else str(value), quote=False)


def as_list(value):
    return ct._as_list(value)


def plain(records):
    """Records with dates as strings, sorted by id, for the JSON embed."""
    return sorted(({k: (str(v) if not isinstance(v, (list, int, float, bool)) and v is not None else v)
                    for k, v in r.items()} for r in records), key=lambda r: r["id"])


def read_sections(path):
    """{slug: text} of a markdown file without frontmatter."""
    _, body = fd.split_frontmatter(fd.read(path))
    return body, {s: t for _, s, _, t in fd.sections(body)}


# ------------------------------------------------------------------ gather

def git_commit(root):
    try:
        run = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True)
        return run.stdout.strip() or "uncommitted"
    except (OSError, subprocess.CalledProcessError):
        return "uncommitted"


def framework_dir(root, explicit):
    if explicit:
        return Path(explicit).resolve()
    vendored = root / "hyperion"
    return vendored.resolve() if vendored.is_dir() else fd.FRAMEWORK_ROOT


def gather_modules(project):
    """Per module: purpose, contract version, clauses with text, conformance tests per
    clause (from the test name's _Cnnn suffix, with its outcome), imports, requirements."""
    out = {}
    for name, module in sorted(project.modules.items()):
        info = {"name": name, "purpose": "", "version": "", "clauses": {}, "imports": [], "tests": {}}
        if module.prose:
            text = fd.read(module.prose)
            m = VERSION_RE.search(text)
            info["version"] = m.group(1) if m else ""
            _, secs = read_sections(module.prose)
            purpose = next((t for s, t in secs.items() if "purpose" in s), "")
            info["purpose"] = purpose.split("\n\n")[0].strip()
            for line in text.splitlines():
                cm = CLAUSE_LINE_RE.match(line)
                if cm:
                    info["clauses"][cm.group(1)] = cm.group(2).strip()
            for clause in sorted(module.clauses):
                info["clauses"].setdefault(clause, "")
        manifest = project.root / "modules" / name / "manifest.yaml"
        if manifest.exists():
            data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
            info["imports"] = [str(i) for i in data.get("allowed_imports") or []]
        prefix = f"modules/{name}/conformance/"
        for node, outcome in sorted(project.results.items()):
            if node.startswith(prefix):
                tm = CLAUSE_TEST_RE.search(node.rsplit("::", 1)[-1])
                if tm:
                    info["tests"].setdefault(f"C-{tm.group(1)}", []).append((node, outcome))
        info["requirements"] = sorted(r["id"] for r in project.records["requirements"]
                                      if name in as_list(r.get("allocated_to")))
        out[name] = info
    if "baseline" in out:
        out["baseline"]["purpose"] = "Shared substrate every module inherits (no contract; changed only under a decision record)."
        out["baseline"]["files"] = sorted(p.stem for p in (project.root / "baseline").glob("*.py") if p.stem != "__init__")
    return out


def gather_slice_docs(project):
    out = {}
    for path in sorted((project.root / "docs" / "slices").glob("SL-*.md")):
        body, secs = read_sections(path)
        m = ORDER_RISK_RE.search(body)
        out[path.stem] = {"order": m.group(1) if m else "", "risk": m.group(2) if m else "",
                          "criteria": secs.get("acceptance-criteria", ""), "lenses": secs.get("lenses-to-run", ""),
                          "record": secs.get("acceptance-record", ""), "scope": secs.get("scope", ""),
                          "contracts": secs.get("contracts-touched", ""), "out_of_scope": secs.get("out-of-scope", "")}
    return out


def gather_decisions(project):
    out = []
    for path in sorted((project.root / "docs" / "decisions").glob("DEC-*.md")):
        body, secs = read_sections(path)
        title = next((l[2:] for l in body.splitlines() if l.startswith("# ")), path.stem)
        fields = {k.lower(): v.strip() for k, v in KV_RE.findall(body)}
        cost = COST_RE.search(secs.get("reversal", "") or "")
        out.append({"id": path.stem, "title": title, "body": body, "reversal": cost.group(1).strip() if cost else "",
                    **{k: fields.get(k, "") for k in ("date", "status", "tier")}})
    return out


def gather_lessons(project):
    """Every mapping in lessons/*.yaml (a file is one lesson or a list). None if no lessons/."""
    folder = project.root / "lessons"
    if not folder.is_dir():
        return None
    out = []
    for path in sorted(list(folder.glob("*.yaml")) + list(folder.glob("*.yml"))):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for rec in data if isinstance(data, list) else [data]:
            if isinstance(rec, dict) and "id" in rec:
                out.append({k: (str(v) if v is not None else "") for k, v in rec.items()})
    return sorted(out, key=lambda r: r["id"])


def gather_framework(framework):
    """Framework documents in registry order, grouped by tier, handbook first."""
    docs = fd.collect_docs(framework)
    order = ["handbook"] + [t for t in TIER_ORDER if t != "handbook"]
    by_path = {d["path"]: d for d in docs.values() if d["fm"] and "id" in d["fm"]}
    valid = sorted(by_path.values(), key=lambda d: (order.index(d["fm"]["tier"]) if d["fm"]["tier"] in order else 99, d["path"]))
    return valid, by_path


def gather(root, framework):
    project = ct.load(root)
    issues = ct.check(project)
    version_file = project.root / ".hyperion" / "version"
    docs, by_path = gather_framework(framework)
    return {
        "project": project,
        "name": project.root.name,
        "commit": git_commit(project.root),
        "framework_version": version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unpinned",
        "framework_dir": framework.relative_to(project.root).as_posix() if framework.is_relative_to(project.root) else framework.name,
        "errors": [str(i) for i in issues if i.level == "error"],
        "warnings": [str(i) for i in issues if i.level == "warning"],
        "modules": gather_modules(project),
        "slice_docs": gather_slice_docs(project),
        "decisions": gather_decisions(project),
        "lessons": gather_lessons(project),
        "docs": docs,
        "docs_by_path": by_path,
        "doc_ids": {d["fm"]["id"] for d in docs},
    }


# ------------------------------------------------------------------ rendering helpers

def pill(text, kind):
    """kind: ok | bad | warn | muted. Under a broken chain the page CSS turns ok grey."""
    return f'<span class="pill {kind}">{esc(text)}</span>'


def outcome_pill(project, ref):
    ref = str(ref)
    if ref == "TBD":
        return pill("TBD", "warn")
    out = ct._outcome(project, ref)
    if out in ("passed", "no_findings"):
        return pill(out, "ok")
    if out == "missing":
        return pill("missing", "bad")
    if out == "pending":
        return pill(out, "warn")
    return pill(out, "bad")


STATUS_KIND = {"verified": "ok", "accepted": "ok", "passed": "ok", "no_findings": "ok", "fixed": "ok",
               "traced": "warn", "in_progress": "warn", "pending": "warn", "proposed": "muted", "planned": "muted",
               "failed": "bad", "findings_raised": "warn", "admitted": "bad", "reopened": "bad", "rejected": "muted"}


def status_pill(value):
    return pill(value, STATUS_KIND.get(str(value), "muted"))


ANCHOR_PREFIX = {"REQ": "req", "HZ": "hz", "SL": "sl", "FND": "fnd", "REV": "rev", "DEC": "dec", "CHG": "chg",
                 "STK": "stk", "ASM": "asm", "GOAL": "goal", "LSN": "lsn"}


def ref_link(ref, known=None):
    """An in-page link for a record id, a module name, or a contract clause reference."""
    ref = str(ref)
    prefix = ref.split("-")[0]
    if prefix in ANCHOR_PREFIX and (known is None or ref in known):
        return f'<a href="#{ANCHOR_PREFIX[prefix]}-{esc(ref)}"><code>{esc(ref)}</code></a>'
    if "::C-" in ref:
        path, clause = ref.split("::", 1)
        parts = path.split("/")
        if len(parts) == 3:
            return f'<a href="#mod-{esc(parts[1])}-{esc(clause)}"><code>{esc(ref)}</code></a>'
    return f"<code>{esc(ref)}</code>"


def module_link(name):
    return f'<a href="#mod-{esc(name)}"><code>{esc(name)}</code></a>'


def links(values, known=None):
    return ", ".join(ref_link(v, known) for v in as_list(values)) or "—"


def section(data, view, title, level=2, doc_ids=None):
    """A section header that links to the framework document explaining it."""
    ids = [i for i in (doc_ids or EXPLAINS.get(view, [])) if i in data["doc_ids"]]
    refs = "".join(f' <a class="hb" href="#doc-{i}" title="the rule this view makes visible">{i}</a>' for i in ids)
    return f"<h{level}>{esc(title)}{refs}</h{level}>"


def table(headers, rows, cls="", attrs=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join(f"<tr{a}>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>" for a, cells in rows)
    return f'<div class="tw"><table class="{cls}"{attrs}><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def test_cell(project, tests):
    items = [f"<code>{esc(t)}</code> {outcome_pill(project, t)}" for t in as_list(tests)]
    return "<br>".join(items) or "—"


# ------------------------------------------------------------------ views

def render_overview(data):
    p = data["project"]
    out = [section(data, "overview", "Gate progress")]
    gate_rows = {}
    for r in sorted(p.records["reviews"], key=lambda x: (str(x.get("date")), x["id"])):
        if r.get("kind") == "gate":
            gate_rows.setdefault(r.get("gate"), []).append(r)
    rows = []
    for g in ct.GATES:
        recs = gate_rows.get(g, [])
        passed = next((r for r in recs if r.get("disposition") == "passed"), None)
        if passed:
            rows.append(("", [f"<b>{g}</b>", status_pill("passed"), esc(passed.get("reviewer")), esc(passed.get("date")), ref_link(passed["id"])]))
        elif recs:
            last = recs[-1]
            rows.append(("", [f"<b>{g}</b>", status_pill(last.get("disposition")), esc(last.get("reviewer")), esc(last.get("date")), ref_link(last["id"])]))
        else:
            rows.append(("", [f"<b>{g}</b>", pill("not reviewed", "muted"), "—", "—", "—"]))
    out.append(table(["Gate", "State", "Reviewer", "Date", "Record"], rows))

    out.append(section(data, "overview", "Slice board", doc_ids=["CORE-LFC-006"]))
    cols = []
    for status in ("planned", "in_progress", "accepted"):
        cards = [f'<div class="card">{ref_link(s["id"])}<br>{esc(s.get("name"))}</div>'
                 for s in sorted(p.records["slices"], key=lambda x: x["id"]) if s.get("status") == status]
        cols.append(f'<div class="col"><h4>{status.replace("_", " ")} ({len(cards)})</h4>{"".join(cards) or "<p class=muted>none</p>"}</div>')
    out.append(f'<div class="board">{"".join(cols)}</div>')

    out.append(section(data, "overview", "Open findings by severity", doc_ids=["CORE-REV-005"]))
    open_f = [f for f in p.records["findings"] if f.get("status") in ("admitted", "reopened")]
    counts = Counter(f.get("severity") for f in open_f)
    out.append(table(["Severity", "Open", "Findings"],
                     [("", [s, str(counts.get(s, 0)), links([f["id"] for f in sorted(open_f, key=lambda x: x["id"]) if f.get("severity") == s])])
                      for s in sorted(ct.FINDING_SEVERITY)]))

    out.append(section(data, "overview", "Hazards not yet verified", doc_ids=["CORE-LFC-002"]))
    unverified = [h for h in sorted(p.records["hazards"], key=lambda x: x["id"]) if h.get("mitigation_status") != "verified"]
    out.append(table(["Hazard", "Mitigation status", "Control", "Test"],
                     [("", [ref_link(h["id"]), status_pill(h.get("mitigation_status")), ref_link(h.get("mitigation_contract")),
                            test_cell(p, h.get("mitigation_test"))]) for h in unverified]) if unverified else "<p>Every hazard's mitigation is verified.</p>")

    out.append(section(data, "overview", "Mutation score per accepted slice", doc_ids=["CORE-TST-002"]))
    accepted = [s for s in sorted(p.records["slices"], key=lambda x: x["id"]) if s.get("status") == "accepted"]
    out.append(table(["Slice", "Mutation score", "Survivors triaged"],
                     [("", [ref_link(s["id"]), esc(s["mutation_score"]) if "mutation_score" in s else pill("not recorded", "warn"),
                            esc(s["survivors_triaged"]) if "survivors_triaged" in s else pill("not recorded", "warn")]) for s in accepted])
               if accepted else "<p>No slice accepted yet.</p>")

    out.append(section(data, "overview", "Health checks", doc_ids=["HYP-002", "CORE-CHG-002"]))
    changes = sorted(p.records["changes"], key=lambda x: (str(x.get("date")), x["id"]))
    by_tier = Counter(c.get("tier") for c in changes)
    span = f"{changes[0].get('date')} to {changes[-1].get('date')}" if changes else "no changes logged"
    yield_rows = lens_yield(p)
    admitted = sum(r[1] for r in yield_rows)
    rejected = sum(r[2] for r in yield_rows)
    reopened = [f["id"] for f in p.records["findings"] if f.get("status") == "reopened"]
    out.append(table(["Metric", "Value", "Computed from"], [
        ("", ["Change log", f"{len(changes)} ({', '.join(f'{by_tier[t]} {t}' for t in sorted(by_tier)) or 'none'}), {span}",
              "<code>trace/changes.yaml</code>: count by tier over the dates logged"]),
        ("", ["Lens yield", f"{admitted} admitted, {rejected} rejected across {len(yield_rows)} source(s); per source in <a href='#lens-yield'>Findings</a>",
              "<code>trace/findings.yaml</code> grouped by source and status"]),
        ("", ["Findings reopened", f"{len(reopened)} ({links(reopened) if reopened else 'none'})",
              "<code>trace/findings.yaml</code> rows with status reopened; a flat record holds no status history"]),
    ]))
    if data["warnings"]:
        out.append(section(data, "overview", "Checker warnings", doc_ids=["CORE-TRC-001"]))
        out.append("<ul>" + "".join(f"<li>{esc(w)}</li>" for w in data["warnings"]) + "</ul>")
    return "\n".join(out)


def render_hazards(data):
    p = data["project"]
    out = [section(data, "hazards", "Hazard register trace")]
    rows = []
    for h in sorted(p.records["hazards"], key=lambda x: x["id"]):
        reg = h.get("register", "—")
        reg = f"{reg} S{h.get('severity')}/L{h.get('likelihood')}" if reg == "local" else f"{reg} {h.get('org_hazard_id', '')} ({h.get('org_system', '')})"
        rows.append((f' id="hz-{esc(h["id"])}"', [
            f"<b>{esc(h['id'])}</b>", esc(h.get("never_statement")), esc(h.get("failure_mode")), esc(reg),
            ref_link(h.get("mitigation_contract")), test_cell(p, h.get("mitigation_test")),
            status_pill(h.get("mitigation_status")), links(h.get("requirement"), p.ids("requirements"))]))
    out.append(table(["Hazard", "Must never happen", "Failure mode", "Register", "Control clause", "Mitigation test", "Status", "Requirement"], rows, cls="hazards"))

    out.append(section(data, "hazards", "G0 question coverage", doc_ids=["CORE-LFC-002"]))
    out.append("<p>The five G0 questions against the module that owns each hazard's control clause. "
               "The record carries no function field, so coverage is shown per module, not per function; "
               "a module whose hazards all sit under one question is a gap to look at.</p>")
    owners = {}
    for h in p.records["hazards"]:
        contract = str(h.get("mitigation_contract", ""))
        parts = contract.split("/")
        owner = parts[1] if contract.startswith("modules/") and len(parts) >= 3 else "unallocated (TBD)"
        owners.setdefault(owner, []).append(h)
    rows = []
    for owner in sorted(owners):
        cells = [module_link(owner) if owner in data["modules"] else esc(owner)]
        for mode, _ in G0_QUESTIONS:
            hits = [h["id"] for h in sorted(owners[owner], key=lambda x: x["id"]) if h.get("failure_mode") == mode]
            cells.append(links(hits) if hits else '<span class="muted">—</span>')
        rows.append(("", cells))
    out.append(table(["Module"] + [f"What if it {q}?" for _, q in G0_QUESTIONS], rows))
    return "\n".join(out)


def render_requirements(data):
    p = data["project"]
    claimed = {}
    for s in p.records["slices"]:
        for rid in as_list(s.get("requirements")):
            claimed[rid] = s["id"]
    sources = p.ids("hazards") | p.ids("needs") | p.ids("assumptions") | p.ids("goals")
    out = [section(data, "requirements", "Verification cross-reference matrix"),
           '<p class="filters"><label>Filter <input type="search" data-filter="vcrm" placeholder="id, text, module, test"></label> '
           '<label>Status <select data-filter-key="status" data-filter="vcrm"><option value="">any</option>'
           + "".join(f'<option>{s}</option>' for s in sorted(ct.LIFECYCLE)) + "</select></label></p>"]
    rows = []
    for r in sorted(p.records["requirements"], key=lambda x: x["id"]):
        vby = as_list(r.get("verified_by"))
        vd = r.get("validated_by")
        rows.append((f' id="req-{esc(r["id"])}" class="req" data-status="{esc(r.get("status"))}"', [
            f"<b>{esc(r['id'])}</b><br><small>{esc(r.get('statement'))}</small>", esc(r.get("kind")),
            links(r.get("source"), sources), ", ".join(module_link(m) for m in as_list(r.get("allocated_to"))),
            f"{esc(r.get('verification_method'))}<br>{test_cell(p, vby)}",
            f"{esc(r.get('validation_class'))}<br>{test_cell(p, [vd]) if vd else '—'}",
            status_pill(r.get("status")), ref_link(claimed[r["id"]]) if r["id"] in claimed else pill("unclaimed", "warn")]))
    out.append(table(["Requirement", "Kind", "Source", "Module", "Verification", "Validation", "Status", "Slice"], rows, cls="vcrm", attrs=' id="vcrm"'))

    out.append(section(data, "requirements", "Needs, assumptions, goals", doc_ids=["CORE-LFC-003"]))
    rows = []
    for stem, extra in (("needs", ["owner"]), ("assumptions", ["owner", "revisit_when"]), ("goals", [])):
        for r in sorted(p.records[stem], key=lambda x: x["id"]):
            detail = "; ".join(f"{k.replace('_', ' ')}: {esc(r.get(k))}" for k in extra)
            rows.append((f' id="{ANCHOR_PREFIX[r["id"].split("-")[0]]}-{esc(r["id"])}"',
                         [f"<b>{esc(r['id'])}</b>", stem[:-1], esc(r.get("statement")), detail or "—"]))
    out.append(table(["Id", "Kind", "Statement", "Detail"], rows))
    return "\n".join(out)


def module_graph(modules):
    lines = ["flowchart LR"]
    baseline = modules.get("baseline")
    if baseline:
        lines.append("    subgraph baseline")
        lines += [f"        baseline_{f}[{f}]" for f in baseline.get("files", [])]
        lines.append("    end")
    for name, m in sorted(modules.items()):
        for imp in m["imports"]:
            parts = imp.split("/")
            if parts[0] == "baseline":
                lines.append(f"    {name}[{name}] --> baseline_{parts[-1]}")
            elif parts[0] == "modules" and len(parts) >= 2:
                lines.append(f"    {name}[{name}] --> {parts[1]}[{parts[1]}]")
    return "\n".join(lines)


def render_modules(data):
    p = data["project"]
    out = [section(data, "modules", "Dependency graph"),
           "<p>Drawn from <code>modules/*/manifest.yaml</code>; an edge is a permitted import.</p>",
           f'<pre class="mermaid">{esc(module_graph(data["modules"]))}</pre>']
    for name, m in sorted(data["modules"].items()):
        out.append(f'<h3 id="mod-{esc(name)}">{esc(name)}' + (f' <small>contract {esc(m["version"])}</small>' if m["version"] else "") + "</h3>")
        out.append(f"<p>{esc(m['purpose']) or '<span class=muted>no purpose section</span>'}</p>")
        out.append(f"<p>Imports: {', '.join(f'<code>{esc(i)}</code>' for i in m['imports']) or '—'}. "
                   f"Allocated requirements: {links(m['requirements'])}.</p>")
        if m["clauses"]:
            rows = []
            for clause, text in sorted(m["clauses"].items()):
                tests = m["tests"].get(clause, [])
                cell = "<br>".join(f"<code>{esc(t)}</code> {outcome_pill(p, t)}" for t, _ in tests) or pill("no conformance test cites this clause", "warn")
                rows.append((f' id="mod-{esc(name)}-{esc(clause)}"', [f"<b>{esc(clause)}</b>", md.inline(text), cell]))
            out.append(table(["Clause", "Promise", "Conformance tests citing it"], rows))
    return "\n".join(out)


def slice_lenses_run(p, sid):
    run = {str(f.get("source"))[5:] for f in p.records["findings"] if f.get("slice") == sid and str(f.get("source")).startswith("lens:")}
    run |= {str(r.get("subject", r["id"])) for r in p.records["reviews"] if r.get("slice") == sid and r.get("kind") == "lens"}
    return sorted(run)


def timeline(data):
    p = data["project"]
    events = []
    for r in p.records["reviews"]:
        what = f"{r.get('kind')} {r.get('gate', '')}".strip() + (f": {r.get('subject')}" if r.get("subject") else "")
        events.append((str(r.get("date")), r["id"], f"{what} — {r.get('disposition')} ({r.get('reviewer')})"))
    for f in p.records["findings"]:
        events.append((str(f.get("date")), f["id"], f"{f.get('severity')} {f.get('status')}: {f.get('summary')}"))
    for c in p.records["changes"]:
        events.append((str(c.get("date")), c["id"], f"{c.get('tier')} change: {c.get('driver')}"))
    for d in data["decisions"]:
        if d["date"]:
            events.append((d["date"], d["id"], d["title"]))
    for sid, doc in data["slice_docs"].items():
        m = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", doc["record"])
        if m:
            events.append((m.group(1), sid, "acceptance record dated"))
    return sorted(events)


def render_plan(data):
    p = data["project"]
    out = [section(data, "plan", "Slices in order")]
    rows = []
    for s in sorted(p.records["slices"], key=lambda x: x["id"]):
        doc = data["slice_docs"].get(s["id"], {})
        rows.append((f' id="sl-{esc(s["id"])}"', [
            f"<b>{esc(s['id'])}</b><br><small>{esc(s.get('name'))}</small>", esc(doc.get("order") or "—"), esc(doc.get("risk") or "—"),
            status_pill(s.get("status")), links(s.get("requirements"), p.ids("requirements")), links(s.get("hazards"), p.ids("hazards")),
            ", ".join(module_link(m) for m in as_list(s.get("contracts"))) or "—"]))
    out.append(table(["Slice", "Order", "Risk", "Status", "Requirements", "Hazards", "Contracts"], rows))
    for s in sorted(p.records["slices"], key=lambda x: x["id"]):
        doc = data["slice_docs"].get(s["id"])
        out.append(f'<h3 id="sl-{esc(s["id"])}-detail">{esc(s["id"])} {esc(s.get("name"))}</h3>')
        if not doc:
            out.append(f"<p class=muted>No <code>docs/slices/{esc(s['id'])}.md</code>.</p>")
            continue
        out.append("<h4>Acceptance criteria</h4>" + (md.render(doc["criteria"]) or "<p class=muted>none written</p>"))
        planned = doc["lenses"].strip() or "none listed"
        run = slice_lenses_run(p, s["id"])
        out.append(f"<h4>Lenses</h4><p>Planned: {esc(planned)}<br>Run (as recorded by findings or lens review rows): "
                   f"{', '.join(map(esc, run)) or '<span class=muted>none recorded</span>'}</p>")
        record = md.render(doc["record"]) if doc["record"].strip() else "<p class=muted>not yet written</p>"
        acc = "".join(f"<li>{k.replace('_', ' ')}: {esc(s[k])}</li>" for k in ("mutation_score", "survivors_triaged") if k in s)
        out.append("<h4>Acceptance record</h4>" + record + (f"<ul>{acc}</ul>" if acc else ""))
    out.append(section(data, "plan", "Timeline", doc_ids=["CORE-TRC-003"]))
    out.append(table(["Date", "Record", "Event"], [("", [esc(d), ref_link(i), esc(w)]) for d, i, w in timeline(data)]))
    return "\n".join(out)


def lens_yield(p):
    """[(source, admitted, rejected, total)] sorted by source; admitted = any status but rejected."""
    stats = {}
    for f in p.records["findings"]:
        s = stats.setdefault(str(f.get("source")), [0, 0])
        s[1 if f.get("status") == "rejected" else 0] += 1
    return [(src, a, r, a + r) for src, (a, r) in sorted(stats.items())]


def render_findings(data):
    p = data["project"]
    out = [section(data, "findings", "Findings log"),
           '<p class="filters"><label>Filter <input type="search" data-filter="findings" placeholder="id, source, summary"></label> '
           '<label>Status <select data-filter-key="status" data-filter="findings"><option value="">any</option>'
           + "".join(f"<option>{s}</option>" for s in sorted(ct.FINDING_STATUS)) + "</select></label> "
           '<label>Severity <select data-filter-key="severity" data-filter="findings"><option value="">any</option>'
           + "".join(f"<option>{s}</option>" for s in sorted(ct.FINDING_SEVERITY)) + "</select></label></p>"]
    rows = []
    for f in sorted(p.records["findings"], key=lambda x: x["id"]):
        ref = f.get("ref")
        rows.append((f' id="fnd-{esc(f["id"])}" data-status="{esc(f.get("status"))}" data-severity="{esc(f.get("severity"))}"', [
            f"<b>{esc(f['id'])}</b>", esc(f.get("date")), ref_link(f.get("slice"), p.ids("slices")), esc(f.get("source")), esc(f.get("form")),
            esc(f.get("severity")), status_pill(f.get("status")), esc(f.get("summary")) + (f"<br><small>Reason: {esc(f.get('reason'))}</small>" if f.get("reason") else ""),
            (ref_link(ref) if isinstance(ref, str) and ("::C-" in ref or ref.split("-")[0] in ANCHOR_PREFIX) else f"<code>{esc(ref)}</code>") if ref else "—"]))
    out.append(table(["Finding", "Date", "Slice", "Source", "Form", "Severity", "Status", "Summary", "Ref"], rows, attrs=' id="findings"'))

    out.append('<h2 id="lens-yield">Lens yield <a class="hb" href="#doc-CORE-REV-003">CORE-REV-003</a></h2>' if "CORE-REV-003" in data["doc_ids"] else '<h2 id="lens-yield">Lens yield</h2>')
    out.append("<p>Admitted findings per source (every status but rejected). A source that never yields an admitted finding is a habit, not a control.</p>")
    out.append(table(["Source", "Admitted", "Rejected", "Total"], [("", [esc(s), str(a), str(r), str(t)]) for s, a, r, t in lens_yield(p)]))

    out.append(section(data, "findings", "Review log", doc_ids=["CORE-REV-002", "CORE-REV-004", "CORE-TRC-003"]))
    known = p.ids("requirements") | p.ids("hazards") | p.ids("slices") | p.decisions
    for kind in sorted(ct.REVIEW_KIND):
        recs = [r for r in sorted(p.records["reviews"], key=lambda x: x["id"]) if r.get("kind") == kind]
        if not recs:
            continue
        out.append(f"<h3>{esc(kind.replace('_', ' '))}</h3>")
        rows = [(f' id="rev-{esc(r["id"])}"', [
            f"<b>{esc(r['id'])}</b>", esc(r.get("gate", "—")), esc(r.get("date")), esc(r.get("reviewer")), status_pill(r.get("disposition")),
            ref_link(r.get("slice"), p.ids("slices")) if r.get("slice") else "—",
            (ref_link(r["ref"], known) if r.get("ref") in known else f"<code>{esc(r.get('ref'))}</code>") if r.get("ref") else "—",
            esc(r.get("subject") or r.get("notes") or "—")]) for r in recs]
        out.append(table(["Review", "Gate", "Date", "Reviewer", "Disposition", "Slice", "Ref", "Subject / notes"], rows))
    return "\n".join(out)


def render_decisions(data):
    p = data["project"]
    out = [section(data, "decisions", "Decision records", doc_ids=["CORE-DEC-001"])]
    if data["decisions"]:
        out.append(table(["Decision", "Date", "Status", "Tier", "Reversal cost"],
                         [(f' id="dec-{esc(d["id"])}"', [f"<b>{esc(d['id'])}</b> {esc(d['title'])}", esc(d["date"] or "—"), esc(d["status"] or "—"),
                                                          esc(d["tier"] or "—"), esc(d["reversal"] or "—")]) for d in data["decisions"]]))
        for d in data["decisions"]:
            out.append(f'<details><summary>{esc(d["id"])}: {esc(d["title"])}</summary><div class="doc">{md.render(d["body"], heading_prefix=d["id"] + "-")}</div></details>')
    else:
        out.append("<p class=muted>No records under <code>docs/decisions/</code>.</p>")

    out.append(section(data, "decisions", "Lessons", doc_ids=["CORE-LSN-001"]))
    lessons = data["lessons"]
    if lessons is None:
        out.append("<p class=muted>No <code>lessons/</code> directory. A lesson already at rung 1 or 2 is its type or its test and needs no entry here.</p>")
    elif not lessons:
        out.append("<p class=muted><code>lessons/</code> holds no entries.</p>")
    else:
        rows = [(f' id="lsn-{esc(l["id"])}"', [f"<b>{esc(l['id'])}</b>", esc(l.get("rung", "—")), esc(l.get("defect", "—")), f"<code>{esc(l.get('check', '—'))}</code>",
                                                  esc(l.get("catches", "0")), esc(l.get("last_catch") or "—"), esc(l.get("status", "—"))])
                for l in sorted(lessons, key=lambda x: (str(x.get("rung", "")), x["id"]))]
        out.append(table(["Lesson", "Rung", "Defect", "Check", "Catches", "Last catch", "Status"], rows))

    out.append(section(data, "decisions", "Change log", doc_ids=["CORE-CHG-001", "CORE-CHG-002"]))
    rows = [(f' id="chg-{esc(c["id"])}"', [f"<b>{esc(c['id'])}</b>", esc(c.get("date")), esc(c.get("tier")), esc(c.get("driver")),
                                            ref_link(c.get("ref")), ", ".join(module_link(m) for m in as_list(c.get("contracts"))) or "—"])
            for c in sorted(p.records["changes"], key=lambda x: x["id"])]
    out.append(table(["Change", "Date", "Tier", "Driver", "Driven by", "Contracts"], rows) if rows else "<p class=muted>No changes logged.</p>")
    return "\n".join(out)


def doc_link_resolver(data, doc_path):
    """Relative links between framework documents become in-page anchors."""
    base = Path(doc_path).parent

    def resolve(href):
        if re.match(r"^[a-z]+:", href) or href.startswith("#"):
            return href
        target, _, frag = href.partition("#")
        rel = Path(*(base / target).parts)
        parts = []
        for part in rel.parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        doc = data["docs_by_path"].get("/".join(parts))
        if doc is None:
            return href
        anchor = f"#doc-{doc['fm']['id']}"
        return f"{anchor}-{frag}" if frag else anchor

    return resolve


def render_handbook(data):
    out = [section(data, "handbook", "Handbook"),
           f"<p>The framework documents at version <code>{esc(data['framework_version'])}</code>, read from "
           f"<code>{esc(data['framework_dir'])}</code>, in registry order with the handbook tier first. "
           "Every other view's headers link here.</p>"]
    order = ["handbook"] + [t for t in TIER_ORDER if t != "handbook"]
    nav = []
    for tier in order:
        docs = [d for d in data["docs"] if d["fm"]["tier"] == tier]
        if docs:
            nav.append(f"<li><b>{esc(tier)}</b><ul>" + "".join(f'<li><a href="#doc-{esc(d["fm"]["id"])}">{esc(d["fm"]["id"])}</a> {esc(d["fm"]["title"])}</li>' for d in docs) + "</ul></li>")
    out.append(f'<nav class="docnav"><ul>{"".join(nav)}</ul></nav>')
    for d in data["docs"]:
        fm = d["fm"]
        meta = f"{fm['tier']} · {fm['status']} · v{fm['version']} · load {fm['load']}"
        if fm.get("sessions"):
            meta += f" · sessions {', '.join(fm['sessions'])}"
        meta += f" · audience {', '.join(fm.get('audience') or [])} · <code>{esc(d['path'])}</code>"
        body = md.render(d["body"], heading_prefix=f"doc-{fm['id']}-", resolve_link=doc_link_resolver(data, d["path"]))
        out.append(f'<article class="doc" id="doc-{esc(fm["id"])}"><div class="docmeta"><b>{esc(fm["id"])}</b> {meta}</div>{body}</article>')
    return "\n".join(out)


# ------------------------------------------------------------------ page

CSS = """
:root{--ink:#1f2933;--muted:#6b7480;--rule:#d9dee3;--paper:#fbfbfa;--panel:#fff;--accent:#1f5f8b;--ok:#1d7f4f;--ok-bg:#e3f4ea;
--bad:#a12622;--bad-bg:#fbe5e3;--warn:#8a5a00;--warn-bg:#fff1d6;--grey:#5c6570;--grey-bg:#eceff2;--code:#f0f2f4}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header.top{padding:14px 24px;border-bottom:1px solid var(--rule);background:var(--panel)}header.top h1{margin:0;font-size:1.3rem}
.meta{display:flex;flex-wrap:wrap;gap:6px 22px;font-size:.85rem;color:var(--muted);margin-top:6px}.meta b{color:var(--ink)}
.banner{background:var(--bad-bg);color:var(--bad);border-bottom:2px solid var(--bad);padding:12px 24px}.banner ul{margin:6px 0 0;padding-left:20px}
nav.tabs{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:2px;padding:6px 24px;background:var(--panel);border-bottom:1px solid var(--rule)}
nav.tabs a{padding:6px 12px;border-radius:4px;text-decoration:none;color:var(--accent);font-weight:600;font-size:.9rem}nav.tabs a.active{background:var(--accent);color:#fff}
main{max-width:1280px;margin:0 auto;padding:16px 24px 80px}section.view{display:none}section.view.active{display:block}
h2{font-size:1.15rem;margin:28px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--rule)}h3{font-size:1rem;margin:22px 0 6px}h4{font-size:.9rem;margin:14px 0 4px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
a{color:var(--accent)}a.hb{font-size:.7rem;font-weight:500;margin-left:8px;padding:1px 6px;border:1px solid var(--rule);border-radius:3px;text-decoration:none;vertical-align:middle}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.85em;background:var(--code);padding:1px 4px;border-radius:3px}
pre{background:var(--code);padding:10px 12px;border-radius:4px;overflow-x:auto;font-size:.8rem;line-height:1.45}pre code{background:none;padding:0}
pre.mermaid{background:var(--panel);border:1px solid var(--rule)}
.tw{overflow-x:auto;margin:8px 0 16px}table{border-collapse:collapse;width:100%;font-size:.86rem;background:var(--panel)}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--rule)}th{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);background:#f4f6f8}
tr[hidden]{display:none}small{color:var(--muted)}.muted{color:var(--muted)}
.pill{display:inline-block;font-size:.72rem;font-weight:600;padding:1px 7px;border-radius:10px;white-space:nowrap}
.pill.ok{background:var(--ok-bg);color:var(--ok)}.pill.bad{background:var(--bad-bg);color:var(--bad)}.pill.warn{background:var(--warn-bg);color:var(--warn)}.pill.muted{background:var(--grey-bg);color:var(--grey)}
body.broken .pill.ok{background:var(--grey-bg);color:var(--grey)}
.board{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.col{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:8px 10px}.col h4{margin-top:0}
.card{border:1px solid var(--rule);border-radius:4px;padding:6px 8px;margin:6px 0;font-size:.85rem;background:var(--paper)}
.filters{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:.85rem}.filters input,.filters select{font:inherit;padding:3px 6px;border:1px solid var(--rule);border-radius:3px}
details{border:1px solid var(--rule);border-radius:4px;margin:8px 0;background:var(--panel)}summary{cursor:pointer;padding:6px 10px;font-weight:600}details .doc{padding:0 14px 8px}
nav.docnav{columns:2;font-size:.85rem;background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:10px 14px}nav.docnav ul{margin:0;padding-left:18px}nav.docnav>ul>li{break-inside:avoid;margin-bottom:6px}
article.doc{background:var(--panel);border:1px solid var(--rule);border-radius:4px;padding:6px 18px 14px;margin:18px 0}article.doc h1{font-size:1.25rem}
.docmeta{font-size:.78rem;color:var(--muted);border-bottom:1px solid var(--rule);padding:6px 0;margin-bottom:6px}blockquote{margin:8px 0;padding:4px 14px;border-left:3px solid var(--rule);color:var(--muted)}
.note{font-size:.8rem;color:var(--muted)}
"""

JS = """
(function(){
var views=Array.prototype.slice.call(document.querySelectorAll('section.view'));
var tabs=Array.prototype.slice.call(document.querySelectorAll('nav.tabs a'));
function drawMermaid(view){
  if(!window.mermaid)return;
  var nodes=view.querySelectorAll('pre.mermaid:not([data-processed])');
  if(nodes.length)try{mermaid.run({nodes:nodes});}catch(e){}
}
function show(name){
  views.forEach(function(v){v.classList.toggle('active',v.dataset.view===name);});
  tabs.forEach(function(t){t.classList.toggle('active',t.dataset.view===name);});
  var v=document.getElementById('view-'+name);if(v)drawMermaid(v);
}
function route(){
  var h=location.hash.slice(1);
  if(!h){show('overview');return;}
  if(h.indexOf('view-')===0){show(h.slice(5));window.scrollTo(0,0);return;}
  var el=document.getElementById(h);
  if(!el){show('overview');return;}
  var v=el.closest('section.view');if(v)show(v.dataset.view);
  el.scrollIntoView();
}
window.addEventListener('hashchange',route);
if(window.mermaid){try{mermaid.initialize({startOnLoad:false,theme:'neutral'});}catch(e){}}
else{Array.prototype.forEach.call(document.querySelectorAll('.mermaid-note'),function(n){n.hidden=false;});}
route();
function applyFilters(id){
  var table=document.getElementById(id);if(!table)return;
  var text='',keys={};
  Array.prototype.forEach.call(document.querySelectorAll('[data-filter="'+id+'"]'),function(c){
    if(c.dataset.filterKey)keys[c.dataset.filterKey]=c.value;else text=c.value.toLowerCase();
  });
  Array.prototype.forEach.call(table.tBodies[0].rows,function(row){
    var ok=!text||row.textContent.toLowerCase().indexOf(text)>=0;
    for(var k in keys)if(keys[k]&&row.dataset[k]!==keys[k])ok=false;
    row.hidden=!ok;
  });
}
Array.prototype.forEach.call(document.querySelectorAll('[data-filter]'),function(c){
  c.addEventListener('input',function(){applyFilters(c.dataset.filter);});
});
})();
"""


def page(data):
    p = data["project"]
    broken = bool(data["errors"])
    verdict = pill(f"BROKEN: {len(data['errors'])} error(s)", "bad") if broken else pill("chain intact", "ok")
    gates = ", ".join(g for g in ct.GATES if g in p.gates_passed()) or "none"
    embed = {
        "project": data["name"], "commit": data["commit"], "framework_version": data["framework_version"],
        "errors": data["errors"], "warnings": data["warnings"],
        "records": {stem: plain(p.records[stem]) for stem in ct.RECORD_FILES},
        "results": dict(sorted(p.results.items())),
        "modules": {n: {k: v for k, v in m.items() if k != "tests"} for n, m in sorted(data["modules"].items())},
    }
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           f"<title>{esc(data['name'])} console</title><style>{CSS}</style>",
           f'<script src="{MERMAID_URL}"></script></head>', f'<body class="{"broken" if broken else "intact"}">']
    if broken:
        out.append('<div class="banner"><b>Trace chain BROKEN. Do not review this console as evidence.</b><ul>'
                   + "".join(f"<li>{esc(e)}</li>" for e in data["errors"]) + "</ul></div>")
    out.append(f'<header class="top"><h1>{esc(data["name"])} console</h1><div class="meta">'
               f"<span>Checker: {verdict}</span><span>Commit <b>{esc(data['commit'])}</b></span>"
               f"<span>Framework <b>{esc(data['framework_version'])}</b></span><span>Gates passed <b>{esc(gates)}</b></span>"
               f"<span>Warnings <b>{len(data['warnings'])}</b></span>"
               '<span class="note mermaid-note" hidden>Diagrams need network access (mermaid from cdn.jsdelivr.net); everything else works offline.</span>'
               "</div></header>")
    out.append('<nav class="tabs">' + "".join(f'<a href="#view-{v}" data-view="{v}">{esc(t)}</a>' for v, t in VIEWS) + "</nav>")
    out.append("<main>")
    renderers = {"overview": render_overview, "hazards": render_hazards, "requirements": render_requirements,
                 "modules": render_modules, "plan": render_plan, "findings": render_findings,
                 "decisions": render_decisions, "handbook": render_handbook}
    for view, title in VIEWS:
        out.append(f'<section class="view" id="view-{view}" data-view="{view}">{renderers[view](data)}</section>')
    out.append("</main>")
    out.append('<script type="application/json" id="console-data">'
               + json.dumps(embed, sort_keys=True, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")
    out.append(f"<script>{JS}</script></body></html>")
    return "\n".join(out) + "\n"


def build(root, framework=None):
    root = Path(root).resolve()
    data = gather(root, framework_dir(root, framework))
    return page(data), data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("root", nargs="?", default=".", help="project root (default: cwd)")
    ap.add_argument("--framework", help="framework documents to render in the handbook (default: <root>/hyperion or this repository)")
    ap.add_argument("--out", default="console/index.html", help="output file, relative to the project root unless absolute")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if not (root / "trace").is_dir():
        print(f"ERROR {root}: no trace/ directory; is this a project root?", file=sys.stderr)
        return 2
    text, data = build(root, args.framework)
    out = Path(args.out) if Path(args.out).is_absolute() else root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    state = f"BROKEN, {len(data['errors'])} error(s)" if data["errors"] else "chain intact"
    print(f"Wrote {out} ({len(text.encode('utf-8'))} bytes; {state}; {len(data['docs'])} framework documents)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
