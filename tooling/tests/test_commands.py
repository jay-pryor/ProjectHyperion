"""tooling/commands.yaml is the one source for the command lines a human runs (P3), and
every script with a CLI has a row in it. The failure this prevents: a tool shipping with
no human-facing command line, which is how build_console.py came to be absent from
README.md and templates/project-CLAUDE.md while CI ran it on every push."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_layer as bl  # noqa: E402
import framework_docs as fd  # noqa: E402

ROOT = fd.FRAMEWORK_ROOT
MAIN_RE = re.compile(r"^def main\(", re.M)
ROWS = bl.Sources().commands


def scripts_with_a_cli():
    return sorted(p.name for p in (ROOT / "tooling").glob("*.py") if MAIN_RE.search(fd.read(p)))


def block(path, name):
    text = fd.read(ROOT / path)
    m = re.search(rf"<!-- generated:{name} -->\n(.*?)\n<!-- /generated -->", text, re.DOTALL)
    assert m, f"{path}: no generated:{name} block"
    return m.group(1)


# ------------------------------------------------------------------ the source is complete

def test_every_script_with_a_cli_has_a_command_row():
    documented = {r["script"] for r in ROWS if r.get("script")}
    missing = [s for s in scripts_with_a_cli() if s not in documented]
    assert not missing, f"no row in tooling/commands.yaml for {', '.join(missing)}"


def test_every_row_names_a_script_that_exists():
    absent = [r["script"] for r in ROWS if r.get("script") and not (ROOT / "tooling" / r["script"]).exists()]
    assert not absent, f"tooling/commands.yaml names missing scripts: {', '.join(absent)}"


def test_the_loaded_source_has_no_defects():
    assert bl.Sources().errors == []


# ------------------------------------------------------------------ the renderer

def test_render_selects_by_context_and_prefixes_the_script():
    rows = [{"script": "a.py", "context": "framework", "does": "one"},
            {"script": "b.py", "args": "--x .", "context": "project", "does": "two"},
            {"script": "c.py", "context": "both", "does": "three"}]
    out = bl.render_commands(rows, "project", "hyperion/tooling/")
    assert "a.py" not in out
    assert "    python hyperion/tooling/b.py --x .  # two" in out
    assert "python hyperion/tooling/c.py" in out


def test_a_literal_run_is_not_prefixed():
    out = bl.render_commands([{"run": "pytest -q", "context": "framework", "does": "suite"}],
                             "framework", "tooling/")
    assert out == "    pytest -q  # suite"


# ------------------------------------------------------------------ the blocks say what the source says

def test_readme_and_template_carry_the_rendered_blocks():
    assert block("README.md", "commands") == bl.render_commands(ROWS, "framework", "tooling/")
    project = bl.render_commands(ROWS, "project", "hyperion/tooling/")
    assert block("templates/project-CLAUDE.md", "commands-project") == project
    assert block("README.md", "commands-project").endswith(project)


def test_the_readme_block_says_it_is_not_run_from_this_repository():
    """A reader copies a command line out of its section, so the line's own block says
    where it runs. The template needs no such header: you are already in the project."""
    readme = block("README.md", "commands-project")
    assert readme.splitlines()[0].startswith("    # not from this repository")
    assert not block("templates/project-CLAUDE.md", "commands-project").startswith("    #")


def test_the_console_is_among_the_project_commands():
    assert "build_console.py" in block("templates/project-CLAUDE.md", "commands-project")
