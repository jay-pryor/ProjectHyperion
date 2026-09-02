"""build_console.py against examples/minimal, green and deliberately broken.

The console is a pure function of the repository and inherits the checker's verdict
(M8, F-14). Two builds of the same tree must be byte-identical, every view must be
present, the matrix must hold one row per requirement, and over a broken chain the page
must banner the errors and never say the chain is intact.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "minimal"
SCRIPT = ROOT / "tooling" / "build_console.py"

sys.path.insert(0, str(SCRIPT.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_console  # noqa: E402
import check_traces  # noqa: E402
from test_check_traces import edit  # noqa: E402


@pytest.fixture(scope="session")
def green(tmp_path_factory):
    dst = tmp_path_factory.mktemp("console") / "minimal"
    shutil.copytree(EXAMPLE, dst, ignore=shutil.ignore_patterns("__pycache__", "results.xml"))
    run = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=dst, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    return dst


@pytest.fixture
def broken(green, tmp_path):
    dst = tmp_path / "minimal"
    shutil.copytree(green, dst)
    edit(dst, "trace/hazards.yaml", "  requirement: REQ-003\n", "")
    return dst


def test_two_builds_are_byte_identical(green):
    first, _ = build_console.build(green, ROOT)
    second, _ = build_console.build(green, ROOT)
    assert first == second
    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", first)     # no build time anywhere


def test_every_view_is_present(green):
    text, data = build_console.build(green, ROOT)
    for view, _ in build_console.VIEWS:
        assert f'<section class="view" id="view-{view}"' in text
    assert not data["errors"]
    assert '<span class="pill ok">chain intact</span>' in text


def test_matrix_has_one_row_per_requirement(green):
    text, _ = build_console.build(green, ROOT)
    project = check_traces.load(green)
    assert text.count('class="req"') == len(project.records["requirements"]) == 6


def test_handbook_renders_framework_documents_with_cross_links(green):
    text, data = build_console.build(green, ROOT)
    assert 'id="doc-HBK-000"' in text and 'id="doc-CORE-TRC-001"' in text
    assert data["docs"][0]["fm"]["tier"] == "handbook"          # handbook tier first
    assert 'href="#doc-CORE-LFC-001"' in text                    # a view header links to its rule
    assert 'href="#doc-CORE-PRN-001"' in text                    # a relative link between documents resolved


def test_broken_chain_banners_errors_and_shows_no_green(broken):
    text, data = build_console.build(broken, ROOT)
    assert data["errors"]
    assert 'class="banner"' in text
    assert "HZ-001: missing required field 'requirement'" in text
    assert 'class="broken"' in text
    assert '<span class="pill ok">chain intact</span>' not in text
    assert 'BROKEN: 1 error(s)' in text


def test_cli_writes_the_file(green, tmp_path):
    out = tmp_path / "console.html"
    run = subprocess.run([sys.executable, str(SCRIPT), str(green), "--framework", str(ROOT), "--out", str(out)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert out.exists() and out.read_text(encoding="utf-8").startswith("<!doctype html>")
