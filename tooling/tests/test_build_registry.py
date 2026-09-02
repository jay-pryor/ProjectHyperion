"""The three prose rules build_registry.py --check enforces (TOOL-001, F-19, F-21), one
test per rule on synthetic documents, plus the repository itself passing them."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_registry as br  # noqa: E402
import framework_docs as fd  # noqa: E402


def doc(path, tier, body, **fm):
    fm = {"id": fm.get("id", path.upper().replace("/", "-").replace(".MD", "")), "tier": tier, **fm}
    return {"fm": fm, "body": body, "path": path}


LONG = "This sentence has more than twelve words in it so that the duplicate detector counts it."


# ------------------------------------------------------------------ duplicate sentences

def test_repeated_long_sentence_in_two_core_docs_is_an_error():
    docs = [doc("core/a.md", "core", LONG + " Short one."), doc("core/b.md", "core", "Intro. " + LONG)]
    errors = br.duplicate_sentence_errors(docs)
    assert len(errors) == 1 and "core/b.md repeats a sentence of core/a.md" in errors[0]


def test_whitespace_differences_do_not_hide_a_duplicate():
    wrapped = LONG.replace("twelve words", "twelve\n   words")
    docs = [doc("core/a.md", "core", LONG), doc("profiles/x/b.md", "profile", wrapped)]
    assert len(br.duplicate_sentence_errors(docs)) == 1


def test_short_sentences_and_other_tiers_are_ignored():
    short = "Twelve words exactly is not more than twelve words so it passes."
    assert len(short.split()) == 12
    docs = [doc("core/a.md", "core", short + " " + LONG), doc("core/b.md", "core", short),
            doc("templates/t.md", "templates", LONG), doc("agents/x.md", "agents", LONG)]
    assert br.duplicate_sentence_errors(docs) == []


def test_generated_and_include_blocks_are_exempt():
    gen = f"<!-- generated:x -->\n{LONG}\n<!-- /generated -->"
    inc = f"<!-- include: CORE-A#s -->\n{LONG}\n<!-- /include -->"
    docs = [doc("core/a.md", "core", LONG), doc("core/b.md", "core", gen), doc("core/c.md", "core", inc)]
    assert br.duplicate_sentence_errors(docs) == []


# ------------------------------------------------------------------ principle trace

def test_core_doc_citing_no_principle_directly_or_transitively_is_an_error():
    docs = [doc("core/a.md", "core", "Cites P3 directly.", id="CORE-A-001"),
            doc("core/b.md", "core", "Cites CORE-A-001 which cites a principle.", id="CORE-B-001"),
            doc("core/c.md", "core", "Cites CORE-B-001, two hops away.", id="CORE-C-001"),
            doc("core/d.md", "core", "Cites nothing but CORE-E-001.", id="CORE-D-001"),
            doc("core/e.md", "core", "Cites CORE-D-001 back; a cycle with no principle.", id="CORE-E-001"),
            doc("templates/t.md", "templates", "Templates are not checked.", id="TPL-001")]
    errors = br.principle_trace_errors(docs)
    assert sorted(e.split(":")[0] for e in errors) == ["core/d.md", "core/e.md"]


def test_p10_is_a_principle_and_p11_is_not():
    docs = [doc("core/a.md", "core", "Cites P10.", id="CORE-A-001"),
            doc("core/b.md", "core", "Cites P11, which does not exist.", id="CORE-B-001")]
    errors = br.principle_trace_errors(docs)
    assert len(errors) == 1 and errors[0].startswith("core/b.md")


# ------------------------------------------------------------------ line limits

def test_line_limit_per_tier(tmp_path):
    (tmp_path / "core").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "core" / "long.md").write_text("x\n" * 121)
    (tmp_path / "core" / "ok.md").write_text("x\n" * 120)
    (tmp_path / "templates" / "long.md").write_text("x\n" * 161)
    (tmp_path / "templates" / "ok.md").write_text("x\n" * 160)
    docs = [doc("core/long.md", "core", ""), doc("core/ok.md", "core", ""),
            doc("templates/long.md", "templates", ""), doc("templates/ok.md", "templates", "")]
    errors = br.line_limit_errors(docs, root=tmp_path)
    assert sorted(e.split(":")[0] for e in errors) == ["core/long.md", "templates/long.md"]


# ------------------------------------------------------------------ the repository

def test_repository_passes_every_check():
    docs, errors = br.validate(fd.collect_docs(fd.FRAMEWORK_ROOT), fd.session_types(fd.FRAMEWORK_ROOT))
    assert errors == []
    assert all("prevents" in d["fm"] and "reader" in d["fm"] and "version" not in d["fm"] for d in docs)
