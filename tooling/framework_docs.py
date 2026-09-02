"""Readers for Hyperion's hand-written sources, shared by every script in tooling/.

One parser per source, used by every consumer, so that the registry, the generator, the
drift check, the loadout helper and the commit checker cannot disagree about what a
document, a section, or a session type is (P3). Nothing here writes a file.

Sources this module reads:
    frontmatter          TOOL-001            every framework document
    sections             CORE-IMP-001        section-level sourcing: `ID#slug`
    session-types block  CORE-SES-001        the ```yaml session-types``` fence
    fragments            CORE-IMP-001        imperatives/*.yaml, profiles/*/fragment.yaml
    generated blocks     CORE-IMP-001        <!-- generated:name --> ... <!-- /generated -->
    include blocks       CORE-IMP-001        <!-- include: ID#slug --> ... <!-- /include -->

Requires PyYAML.
"""

import hashlib
import re
from pathlib import Path

import yaml

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent
SESSION_DOC = "core/session-protocol.md"
REGISTRY = "REGISTRY.md"
MODEL_ALIASES = ("sonnet", "opus", "haiku")

FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE_RE = re.compile(r"^```")
GENERATED_RE = re.compile(r"<!-- generated:(\S+) -->(.*?)<!-- /generated -->", re.DOTALL)
INCLUDE_RE = re.compile(r"<!-- include: (\S+) -->(.*?)<!-- /include -->", re.DOTALL)
SOURCE_RE = re.compile(r"^([A-Z]+-[A-Z]*-?\d{3})#([a-z0-9-]+)$")


# ------------------------------------------------------------------ documents

def read(path):
    return Path(path).read_text(encoding="utf-8")


def split_frontmatter(text):
    """(frontmatter dict or None, body). Scalars are kept as strings so `version: 0.1`
    does not become a float."""
    m = FM_RE.match(text)
    if not m:
        return None, text
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        return None, text
    return {k: _stringify(v) for k, v in data.items()}, text[m.end():]


def _stringify(value):
    if isinstance(value, list):
        return [_stringify(v) for v in value]
    if value is None or isinstance(value, (dict, bool)):
        return value
    return str(value)


def collect_docs(root=FRAMEWORK_ROOT):
    """Every framework document with frontmatter, keyed by path. examples/ holds
    projects built under the framework, not documents of it, and is skipped."""
    docs = {}
    for path in sorted(Path(root).rglob("*.md")):
        if ".git" in path.parts or "examples" in path.parts:
            continue
        text = read(path)
        fm, body = split_frontmatter(text)
        rel = path.relative_to(root).as_posix()
        docs[rel] = {"fm": fm, "body": body, "path": rel}
    return docs


def docs_by_id(docs):
    return {d["fm"]["id"]: d for d in docs.values() if d["fm"] and "id" in d["fm"]}


def model_readable(fm):
    return "model" in (fm.get("audience") or [])


# ------------------------------------------------------------------ sections

def slug(heading):
    return re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")


def sections(body):
    """[(level, slug, heading, text)] for every heading outside a code fence. A
    section runs to the next heading of any level, so a hash covers exactly the
    sentences under one heading and nothing else (M6)."""
    out, fenced, current = [], False, None
    for line in body.splitlines():
        if FENCE_RE.match(line):
            fenced = not fenced
        m = None if fenced else HEADING_RE.match(line)
        if m:
            current = [len(m.group(1)), slug(m.group(2)), m.group(2), []]
            out.append(current)
        elif current is not None:
            current[3].append(line)
    return [(lvl, s, h, "\n".join(lines).strip()) for lvl, s, h, lines in out]


def section(body, slug_):
    for _, s, _, text in sections(body):
        if s == slug_:
            return text
    return None


def section_hash(text):
    normalised = "\n".join(l.rstrip() for l in text.strip().splitlines())
    return hashlib.sha256(normalised.encode("utf-8")).hexdigest()[:16]


def resolve_source(by_id, ref):
    """`ID#slug` -> (doc, slug, section text). Raises ValueError naming the defect: an
    unknown document, a document the model never loads, or a section that is not there."""
    m = SOURCE_RE.match(ref)
    if not m:
        raise ValueError(f"source {ref!r} is not of the form ID#section-slug")
    doc_id, slug_ = m.groups()
    doc = by_id.get(doc_id)
    if doc is None:
        raise ValueError(f"source {ref}: unknown document id {doc_id}")
    if not model_readable(doc["fm"]):
        raise ValueError(f"source {ref}: audience of {doc_id} excludes the model; "
                         "an imperative cannot derive from a document its reader never loads")
    text = section(doc["body"], slug_)
    if text is None:
        have = ", ".join(s for _, s, _, _ in sections(doc["body"]) if s)
        raise ValueError(f"source {ref}: no section '{slug_}' in {doc['path']} (have: {have})")
    return doc, slug_, text


# ------------------------------------------------------------------ fenced data blocks

def fenced_block(body, info):
    """Content of the ```<info> fence, e.g. info='yaml session-types'."""
    m = re.search(r"^```" + re.escape(info) + r"\s*\n(.*?)^```", body, re.DOTALL | re.MULTILINE)
    return m.group(1) if m else None


def session_types(root=FRAMEWORK_ROOT):
    """The session table as data (CORE-SES-001, M3)."""
    _, body = split_frontmatter(read(Path(root) / SESSION_DOC))
    block = fenced_block(body, "yaml session-types")
    if block is None:
        raise ValueError(f"{SESSION_DOC}: no ```yaml session-types``` block")
    types = yaml.safe_load(block)
    for name, t in types.items():
        for key in ("purpose", "scope", "may_modify", "must_not_modify"):
            if key not in t:
                raise ValueError(f"{SESSION_DOC}: session type {name} lacks '{key}'")
    return types


def project_session_types(root=FRAMEWORK_ROOT):
    return {n: t for n, t in session_types(root).items() if t["scope"] in ("project", "both")}


# ------------------------------------------------------------------ fragments

def load_fragment(path):
    data = yaml.safe_load(read(path)) or {}
    data.setdefault("imperatives", [])
    data.setdefault("stop_conditions", [])
    data["_path"] = Path(path).as_posix()
    return data


def split_profiles(values):
    """argparse action='append' values -> names: --profiles a --profiles b, or --profiles a,b."""
    if values is None:
        return None
    return [n for v in values for n in v.replace(",", " ").split()]


def profile_names(root=FRAMEWORK_ROOT):
    return sorted(p.parent.name for p in (Path(root) / "profiles").glob("*/fragment.yaml"))


def profile_fragment(root, name):
    path = Path(root) / "profiles" / name / "fragment.yaml"
    if not path.exists():
        raise ValueError(f"unknown profile {name!r}: no {path.relative_to(root).as_posix()}")
    frag = load_fragment(path)
    frag.setdefault("profile", name)
    return frag


# ------------------------------------------------------------------ generated and include blocks

def block_names(text):
    return [m.group(1) for m in GENERATED_RE.finditer(text)]


def fill_blocks(text, renders):
    """Replace the content of every generated block whose name is in `renders`.
    Returns (new text, names present but not rendered)."""
    unknown = []

    def sub(m):
        name = m.group(1)
        if name not in renders:
            unknown.append(name)
            return m.group(0)
        return f"<!-- generated:{name} -->\n{renders[name].rstrip()}\n<!-- /generated -->"

    return GENERATED_RE.sub(sub, text), unknown


def fill_includes(text, by_id):
    """Fill every include block verbatim from its source section (F-07)."""
    def sub(m):
        _, _, body = resolve_source(by_id, m.group(1))
        return f"<!-- include: {m.group(1)} -->\n{body}\n<!-- /include -->"

    return INCLUDE_RE.sub(sub, text)


def parse_imperative_table(text):
    """{id: (text, source)} from a rendered imperatives block, or None if absent."""
    m = next((m for m in GENERATED_RE.finditer(text) if m.group(1) == "imperatives"), None)
    if m is None:
        return None
    rows = {}
    for line in m.group(2).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.match(r"^IMP-[A-Z0-9]+$", cells[0]):
            rows[cells[0]] = (re.sub(r"\s*\*\([^)]*\)\*\s*$", "", cells[1]), cells[2])
    return rows
