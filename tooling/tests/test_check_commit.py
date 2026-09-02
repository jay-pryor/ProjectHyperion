"""check_commit.py against a throwaway git repository, one commit per rule.

The rules come from the session-types block in CORE-SES-001 (scope), CORE-CHG-001 (a
contract diff bumps its version after G3), and SIM-DET-001 (a fixture diff cites a
decision or finding). A rule with no test here is a rule the checker may silently stop
enforcing.
"""

import subprocess
import sys
from pathlib import Path

import pytest

TOOLING = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLING))
import check_commit  # noqa: E402
import framework_docs as fd  # noqa: E402

GIT_ENV = ["-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false"]

G3_PENDING = "- {id: REV-001, kind: gate, gate: G3, date: 2026-01-01, reviewer: h, disposition: pending}\n"
G3_PASSED = "- {id: REV-001, kind: gate, gate: G3, date: 2026-01-01, reviewer: h, disposition: passed}\n"
FINDINGS = "- {id: FND-001, date: 2026-01-01, slice: SL-01, source: human, form: test, severity: S2, status: admitted, summary: x}\n"


def git(repo, *args):
    return subprocess.run(["git", *GIT_ENV, *args], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()


def commit(repo, files, message):
    """Write `files` ({relative path: content}) and commit them with `message`."""
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    """A project with one contract, one decision, one finding, and G3 not yet passed.
    The scaffold commit sits below the checked range."""
    repo = tmp_path / "proj"
    repo.mkdir()
    git(repo, "init", "-q")
    base = commit(repo, {
        "trace/reviews.yaml": G3_PENDING,
        "trace/findings.yaml": FINDINGS,
        "docs/decisions/DEC-001.md": "# DEC-001\n",
        "modules/m/CONTRACT.md": "# Contract: m\nVersion: 1.0 · Status: active\n",
        "modules/m/contract.py": "def op(): ...\n",
        "modules/m/src/impl.py": "x = 1\n",
    }, "scaffold\n\nSession: GATE")
    return repo, base


def check(repo, base, framework=False):
    return check_commit.run(repo, f"{base}..HEAD", framework=framework, types=fd.session_types())


# ------------------------------------------------------------------ rule 1: the trailer

def test_missing_trailer_is_an_error(repo):
    repo, base = repo
    commit(repo, {"modules/m/src/impl.py": "x = 2\n"}, "no trailer")
    _, errors, _ = check(repo, base)
    assert any("no `Session:" in e for e in errors)


def test_unknown_or_framework_only_type_is_an_error(repo):
    repo, base = repo
    commit(repo, {"modules/m/src/impl.py": "x = 2\n"}, "fw\n\nSession: FRAMEWORK")
    _, errors, _ = check(repo, base)
    assert any("not a session type valid here" in e for e in errors)


# ------------------------------------------------------------------ rule 2: scope

def test_in_scope_commit_passes(repo):
    repo, base = repo
    commit(repo, {"modules/m/src/impl.py": "x = 2\n", "trace/findings.yaml": FINDINGS + "\n"},
           "impl\n\nSession: IMPLEMENT")
    shas, errors, warnings = check(repo, base)
    assert len(shas) == 1 and errors == [] and warnings == []


def test_must_not_modify_is_an_error(repo):
    repo, base = repo
    commit(repo, {"modules/m/conformance/test_op.py": "def test(): ...\n"}, "sneak\n\nSession: IMPLEMENT")
    _, errors, _ = check(repo, base)
    assert any("IMPLEMENT must not modify modules/m/conformance/test_op.py" in e for e in errors)


def test_path_owned_by_another_type_is_an_error(repo):
    repo, base = repo
    commit(repo, {"lessons/LSN-001.md": "x\n"}, "lesson from impl\n\nSession: IMPLEMENT")
    _, errors, _ = check(repo, base)
    assert any("outside IMPLEMENT's scope" in e for e in errors)


def test_path_owned_by_no_type_is_a_warning_only(repo):
    repo, base = repo
    commit(repo, {"README.md": "x\n", "modules/m/src/impl.py": "x = 3\n"}, "readme\n\nSession: IMPLEMENT")
    _, errors, warnings = check(repo, base)
    assert errors == []
    assert any("README.md is owned by no session type" in w for w in warnings)


def test_review_may_only_append_findings(repo):
    repo, base = repo
    commit(repo, {"trace/findings.yaml": FINDINGS + "- {id: FND-002}\n"}, "review\n\nSession: REVIEW")
    assert check(repo, base)[1] == []
    commit(repo, {"trace/slices.yaml": "[]\n"}, "review touches slices\n\nSession: REVIEW")
    assert any("outside REVIEW's scope" in e for e in check(repo, base)[1])


# ------------------------------------------------------------------ rule 3: contract version

def test_contract_change_before_g3_needs_no_bump(repo):
    repo, base = repo
    commit(repo, {"modules/m/contract.py": "def op(a): ...\n"}, "draft\n\nSession: CONTRACT")
    assert check(repo, base)[1] == []


def test_contract_change_after_g3_without_version_is_an_error(repo):
    repo, base = repo
    commit(repo, {"trace/reviews.yaml": G3_PASSED}, "g3\n\nSession: GATE")
    commit(repo, {"modules/m/contract.py": "def op(a): ...\n",
                  "modules/m/CONTRACT.md": "# Contract: m\nVersion: 1.0 · Status: active\n\nC-001 new clause\n"},
           "widen\n\nSession: CONTRACT")
    _, errors, _ = check(repo, base)
    assert any("without a `Version:` change" in e for e in errors)


def test_contract_change_after_g3_with_version_passes(repo):
    repo, base = repo
    commit(repo, {"trace/reviews.yaml": G3_PASSED}, "g3\n\nSession: GATE")
    commit(repo, {"modules/m/contract.py": "def op(a): ...\n",
                  "modules/m/CONTRACT.md": "# Contract: m\nVersion: 1.1 · Status: active\n"},
           "widen\n\nSession: CONTRACT")
    assert check(repo, base)[1] == []


# ------------------------------------------------------------------ rule 4: fixture trailer

def test_fixture_change_without_trailer_is_an_error(repo):
    repo, base = repo
    commit(repo, {"fixtures/s/expected/out.txt": "1\n"}, "record\n\nSession: INTEGRATE")
    assert any("Fixture-change" in e for e in check(repo, base)[1])


def test_tolerance_change_with_resolving_trailer_passes(repo):
    repo, base = repo
    commit(repo, {"fixtures/s/tolerance.yaml": "rel: 1e-9\n"},
           "loosen\n\nSession: CONFORMANCE\nFixture-change: FND-001")
    assert check(repo, base)[1] == []
    commit(repo, {"fixtures/s/expected/out.txt": "1\n"},
           "record\n\nSession: INTEGRATE\nFixture-change: DEC-001")
    assert check(repo, base)[1] == []


def test_fixture_trailer_must_resolve(repo):
    repo, base = repo
    commit(repo, {"fixtures/s/expected/out.txt": "1\n"},
           "record\n\nSession: INTEGRATE\nFixture-change: DEC-099")
    assert any("does not resolve" in e for e in check(repo, base)[1])


# ------------------------------------------------------------------ framework mode and cli

def test_framework_mode_checks_only_the_trailer(repo):
    repo, base = repo
    commit(repo, {"core/x.md": "x\n", "modules/m/src/impl.py": "x = 2\n"}, "edit\n\nSession: FRAMEWORK")
    assert check(repo, base, framework=True)[1] == []
    commit(repo, {"core/y.md": "y\n"}, "edit without trailer")
    assert any("no `Session:" in e for e in check(repo, base, framework=True)[1])
    commit(repo, {"core/z.md": "z\n"}, "project type in framework\n\nSession: IMPLEMENT")
    assert any("not a session type valid here" in e for e in check(repo, base, framework=True)[1])


def test_cli_exit_codes(repo):
    repo, base = repo
    commit(repo, {"modules/m/src/impl.py": "x = 2\n"}, "impl\n\nSession: IMPLEMENT")
    ok = subprocess.run([sys.executable, str(TOOLING / "check_commit.py"), f"{base}..HEAD", "--root", str(repo)],
                        capture_output=True, text=True)
    assert ok.returncode == 0, ok.stderr
    commit(repo, {"modules/m/conformance/t.py": "x\n"}, "bad\n\nSession: IMPLEMENT")
    bad = subprocess.run([sys.executable, str(TOOLING / "check_commit.py"), f"{base}..HEAD", "--root", str(repo)],
                         capture_output=True, text=True)
    assert bad.returncode == 1 and "must not modify" in bad.stderr


def test_glob_semantics():
    m = check_commit.matches
    assert m("modules/m/src/a/b.py", "modules/*/src/**")
    assert not m("modules/m/x/src/a.py", "modules/*/src/**")
    assert m("modules/m/contract.py", "modules/*/contract.*")
    assert m("fixtures/s/tolerance.yaml", "**/tolerance.yaml")
    assert m("trace/findings.yaml", "trace/**")
    assert not m("trace2/findings.yaml", "trace/**")
