"""The Claude Code hooks against a throwaway project, JSON on stdin, one test per rule.

scope.py enforces the session-types block of CORE-SES-001 at write time and a lens agent's
own restriction (CORE-HRN-001); plugins.py warns on plugins outside the declared list.
Both are standard-library scripts copied into .claude/hooks/ by build_layer.py. A rule
with no test here is a rule the hook may silently stop enforcing.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

TOOLING = Path(__file__).resolve().parents[1]
HOOKS = TOOLING / "claude-code" / "hooks"
sys.path.insert(0, str(TOOLING))
import check_commit  # noqa: E402

TABLE = {
    "scope": "project", "session_file": ".hyperion/session", "test_command": "pytest",
    "types": {
        "IMPLEMENT": {"may_modify": ["modules/*/src/**", "modules/*/tests/**", "trace/**"],
                      "must_not_modify": ["modules/*/contract.*", "modules/*/conformance/**", "baseline/**"]},
        "REVIEW": {"may_modify": ["trace/findings.yaml"], "must_not_modify": ["modules/**"]},
    },
    "agents": {"lens-x": {"may_modify": ["trace/findings.yaml"], "must_not_modify": []}},
}


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "proj"
    (root / ".hyperion").mkdir(parents=True)
    (root / ".hyperion" / "session-types.json").write_text(json.dumps(TABLE), encoding="utf-8")
    return root


def declare(root, session):
    (root / ".hyperion" / "session").write_text(session + "\n", encoding="utf-8")


def run(hook, root, payload, env=None):
    payload = {"session_id": "s1", "cwd": str(root), **payload}
    full_env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root), **(env or {})}
    return subprocess.run([sys.executable, str(HOOKS / hook)], input=json.dumps(payload),
                          capture_output=True, text=True, env=full_env, cwd=root)


def edit(root, rel, tool="Edit", agent=None):
    payload = {"tool_name": tool, "tool_input": {"file_path": str(root / rel)}}
    if agent:
        payload["agent_type"] = agent
    return run("scope.py", root, payload)


def decision(result):
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"] if result.stdout.strip() else None


# ------------------------------------------------------------------ scope.py: the declared session

def test_no_declaration_allows_and_warns_once_per_session(project):
    first = edit(project, "modules/m/contract.py")
    assert decision(first) is None
    assert "no session declared" in first.stderr
    second = edit(project, "modules/m/contract.py")
    assert decision(second) is None and second.stderr == ""


def test_write_inside_may_modify_is_allowed(project):
    declare(project, "IMPLEMENT")
    assert decision(edit(project, "modules/m/src/impl.py")) is None
    assert decision(edit(project, "trace/findings.yaml", tool="Write")) is None


def test_write_in_must_not_modify_is_denied_naming_type_and_glob(project):
    declare(project, "IMPLEMENT")
    d = decision(edit(project, "modules/m/contract.py"))
    assert d["permissionDecision"] == "deny"
    assert "IMPLEMENT" in d["permissionDecisionReason"] and "modules/*/contract.*" in d["permissionDecisionReason"]


def test_write_outside_may_modify_is_denied(project):
    declare(project, "IMPLEMENT")
    d = decision(edit(project, "docs/slices/SL-01.md", tool="MultiEdit"))
    assert d["permissionDecision"] == "deny" and "IMPLEMENT" in d["permissionDecisionReason"]


def test_notebook_path_is_checked_like_file_path(project):
    declare(project, "IMPLEMENT")
    payload = {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": str(project / "baseline" / "n.ipynb")}}
    assert decision(run("scope.py", project, payload))["permissionDecision"] == "deny"


def test_session_file_itself_and_paths_outside_the_project_pass(project, tmp_path):
    declare(project, "IMPLEMENT")
    assert decision(edit(project, ".hyperion/session", tool="Write")) is None
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "elsewhere.txt")}}
    assert decision(run("scope.py", project, payload)) is None


def test_non_write_tools_are_ignored(project):
    declare(project, "IMPLEMENT")
    assert decision(edit(project, "modules/m/contract.py", tool="Read")) is None
    assert decision(run("scope.py", project, {"tool_name": "Bash", "tool_input": {"command": "rm -rf modules"}})) is None


def test_unknown_declared_type_is_denied(project):
    declare(project, "HACK")
    d = decision(edit(project, "modules/m/src/impl.py"))
    assert d["permissionDecision"] == "deny" and "HACK" in d["permissionDecisionReason"]


def test_no_table_means_nothing_to_enforce(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    assert decision(edit(root, "anything.py")) is None


# ------------------------------------------------------------------ scope.py: inside a lens agent

def test_lens_agent_may_write_only_findings(project):
    declare(project, "IMPLEMENT")                       # the parent's type does not leak in
    assert decision(edit(project, "trace/findings.yaml", agent="lens-x")) is None
    d = decision(edit(project, "modules/m/src/impl.py", agent="lens-x"))
    assert d["permissionDecision"] == "deny" and "lens-x" in d["permissionDecisionReason"]


@pytest.mark.parametrize("command, allowed", [
    ("pytest -q modules/m/conformance", True),
    ("pytest", True),
    ("rm -rf modules", False),
    ("pytest -q; rm -rf modules", False),
    ("pytest && git commit -am x", False),
    ("python -m pytest", False),
])
def test_lens_agent_bash_is_the_test_command_only(project, command, allowed):
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "agent_type": "lens-x"}
    d = decision(run("scope.py", project, payload))
    assert (d is None) == allowed, (command, d)


def test_unknown_agent_type_falls_back_to_the_declared_session(project):
    declare(project, "REVIEW")
    d = decision(edit(project, "modules/m/src/impl.py", agent="general-purpose"))
    assert d["permissionDecision"] == "deny" and "REVIEW" in d["permissionDecisionReason"]


# ------------------------------------------------------------------ the two matchers agree

@pytest.mark.parametrize("path, glob", [
    ("modules/m/src/a/b.py", "modules/*/src/**"),
    ("modules/m/contract.py", "modules/*/contract.*"),
    ("modules/m/CONTRACT.md", "modules/*/contract.*"),
    ("fixtures/s/tolerance.yaml", "**/tolerance.yaml"),
    ("tolerance.yaml", "**/tolerance.yaml"),
    ("trace/findings.yaml", "trace/**"),
    ("modules/m/x/src/b.py", "modules/*/src/**"),
    ("CLAUDE.md", "**"),
])
def test_hook_matcher_mirrors_check_commit(path, glob):
    spec = {}
    exec((HOOKS / "scope.py").read_text(encoding="utf-8").split("def first_match")[0], spec)
    assert spec["matches"](path, glob) == check_commit.matches(path, glob)


# ------------------------------------------------------------------ plugins.py

def settings(root, plugins):
    (root / ".claude").mkdir(parents=True, exist_ok=True)
    (root / ".claude" / "settings.json").write_text(json.dumps({"enabledPlugins": {p: True for p in plugins}}))


def test_plugins_outside_the_declared_list_warn_and_name_the_exclusions(project, tmp_path):
    settings(project, ["pyright-lsp@claude-plugins-official"])
    user = tmp_path / "cfg"
    user.mkdir()
    (user / "settings.json").write_text(json.dumps({"enabledPlugins": {
        "pyright-lsp@claude-plugins-official": True, "memory-writer@x": True, "off@x": False}}))
    r = run("plugins.py", project, {"hook_event_name": "SessionStart"}, env={"CLAUDE_CONFIG_DIR": str(user)})
    assert r.returncode == 0
    assert "memory-writer@x" in r.stdout and "off@x" not in r.stdout
    assert "P3" in r.stdout and "P8" in r.stdout and "P10" in r.stdout


def test_declared_plugins_only_is_silent(project, tmp_path):
    settings(project, ["pyright-lsp@claude-plugins-official"])
    user = tmp_path / "cfg"
    user.mkdir()
    (user / "settings.json").write_text(json.dumps({"enabledPlugins": {"pyright-lsp@claude-plugins-official": True}}))
    r = run("plugins.py", project, {"hook_event_name": "SessionStart"}, env={"CLAUDE_CONFIG_DIR": str(user)})
    assert r.returncode == 0 and r.stdout == ""


def test_local_settings_count_as_enabled(project, tmp_path):
    settings(project, [])
    (project / ".claude" / "settings.local.json").write_text(json.dumps({"enabledPlugins": {"extra@x": True}}))
    user = tmp_path / "cfg"
    user.mkdir()
    r = run("plugins.py", project, {"hook_event_name": "SessionStart"}, env={"CLAUDE_CONFIG_DIR": str(user)})
    assert "extra@x" in r.stdout
