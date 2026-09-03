"""A project's CLAUDE.md carries a marker for every generated block, and the expectation
is derived from the template rather than restated (P3, P2). The failure this prevents:
a renderer with no marker to render into is silent, so the block never appears and
nothing says so. `examples/minimal` went without `commands-project` that way, and carried
a hand-written command list that had drifted from tooling/commands.yaml."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_layer as bl  # noqa: E402
import framework_docs as fd  # noqa: E402
import init_project  # noqa: E402

ROOT = fd.FRAMEWORK_ROOT


def example_projects():
    return [m.parent.parent for m in sorted(ROOT.glob("examples/*/.hyperion/profiles"))]


def drop_block(text, name):
    """The file as a project that never added the markers would have it: block gone."""
    return fd.GENERATED_RE.sub(lambda m: "" if m.group(1) == name else m.group(0), text)


# ------------------------------------------------------------------ the two sets agree

def test_the_template_declares_a_marker_for_every_block_the_renderer_fills():
    """Neither side may grow alone: a renderer with no marker renders into nothing, and
    a marker with no renderer is an error at build time."""
    src = bl.Sources()
    rendered = set(bl.claude_renders(src, [], [], []))
    assert set(init_project.template_blocks()) == rendered


def test_a_block_added_to_the_template_extends_the_expectation(tmp_path):
    """The end of the list that fell behind: one edit, in the template, and the set a
    project is expected to carry follows. Nothing else names the blocks."""
    template = tmp_path / bl.TEMPLATE
    template.parent.mkdir(parents=True)
    template.write_text(fd.read(ROOT / bl.TEMPLATE).replace(
        "## Commands", "<!-- generated:invented -->\n<!-- /generated -->\n\n## Commands", 1),
        encoding="utf-8")
    assert set(init_project.template_blocks(tmp_path)) == set(init_project.template_blocks()) | {"invented"}


# ------------------------------------------------------------------ the warning fires

def test_a_project_missing_a_block_the_template_declares_is_warned_about(tmp_path, capsys):
    project = tmp_path / "proj"
    project.mkdir()
    assert init_project.main([str(project), "--profiles", "simulation"]) == 0
    claude = project / "CLAUDE.md"
    dropped = init_project.template_blocks()[-1]
    claude.write_text(drop_block(claude.read_text(encoding="utf-8"), dropped), encoding="utf-8")
    capsys.readouterr()

    assert init_project.main([str(project), "--upgrade"]) == 0
    out = capsys.readouterr().out
    assert f"WARNING CLAUDE.md has no <!-- generated:{dropped} --> block" in out
    for kept in init_project.template_blocks():
        if kept != dropped:
            assert f"generated:{kept} --> block" not in out


# ------------------------------------------------------------------ this repository's own projects

def test_every_example_project_carries_every_block_the_template_declares():
    for project in example_projects():
        present = fd.block_names(fd.read(project / "CLAUDE.md"))
        missing = [b for b in init_project.template_blocks() if b not in present]
        rel = project.relative_to(ROOT).as_posix()
        assert not missing, f"{rel}/CLAUDE.md opts out of {', '.join(missing)}"
