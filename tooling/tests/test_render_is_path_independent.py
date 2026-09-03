"""Rendering the operating layer depends on the repository's contents and nothing else:
the same checkout at a different absolute path, rendered from a different working
directory, must produce byte-identical output (P2). The failure this prevents:
tooling/imperatives.json recorded each profile imperative's carrier as the absolute path
of the checkout that rendered it, so `--check` called the file stale on every other
machine — the check that guards generated output reporting a failure that was not one."""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_layer as bl  # noqa: E402
import framework_docs as fd  # noqa: E402

ROOT = fd.FRAMEWORK_ROOT
COPY_IGNORE = shutil.ignore_patterns(".git", "__pycache__", ".venv")


def outputs(root):
    """Everything `build_layer.py` with no arguments would write, keyed by the path
    relative to `root` so that two checkouts are comparable."""
    root = Path(root)
    src = bl.Sources(root)
    out = dict(bl.framework_outputs(src))
    assert src.errors == [], src.errors
    for marker in sorted(root.glob("examples/*/.hyperion/profiles")):
        project = marker.parent.parent
        for path, text in bl.project_outputs(src, project, bl.project_profiles(project)).items():
            out[Path(path).relative_to(root).as_posix()] = text
    return out


def test_the_same_checkout_elsewhere_renders_byte_identical_output(tmp_path, monkeypatch):
    here = outputs(ROOT)
    elsewhere = tmp_path / "elsewhere"
    shutil.copytree(ROOT, elsewhere, ignore=COPY_IGNORE)
    monkeypatch.chdir(tmp_path)
    assert outputs(elsewhere) == here


def test_no_generated_output_names_the_directory_it_was_rendered_in():
    """The same invariant stated directly, so a renderer that interpolates a filesystem
    path fails here, naming the output, rather than as a stale file on another machine."""
    assert [p for p, text in outputs(ROOT).items() if str(ROOT) in text] == []
