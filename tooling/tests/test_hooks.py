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
import build_layer  # noqa: E402
import check_commit  # noqa: E402
import harness  # noqa: E402

TYPES = {
    "IMPLEMENT": {"may_modify": ["modules/*/src/**", "modules/*/tests/**", "trace/**"],
                  "must_not_modify": ["modules/*/contract.*", "modules/*/conformance/**", "baseline/**"]},
    "CONTRACT": {"may_modify": ["modules/*/contract.*", "trace/**"],
                 "must_not_modify": ["modules/*/src/**"]},
    "REVIEW": {"may_modify": ["trace/findings.yaml"], "must_not_modify": ["modules/**"]},
    "QUERY": {"may_modify": [], "must_not_modify": ["**"]},
}
TABLE = {
    "scope": "project", "session_dir": ".hyperion/sessions", "test_command": "pytest",
    "declare_commands": {n: harness.declare_command(n) for n in TYPES},
    "types": TYPES,
    "agents": {"lens-x": {"may_modify": ["trace/findings.yaml"], "must_not_modify": []}},
}
BINDINGS = ".hyperion/sessions"


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "proj"
    (root / ".hyperion").mkdir(parents=True)
    (root / ".hyperion" / "session-types.json").write_text(json.dumps(TABLE), encoding="utf-8")
    return root


def declare(root, session, session_id="s1"):
    """Bind a session id to a type, as the hook does on seeing a declaration go past."""
    (root / BINDINGS).mkdir(parents=True, exist_ok=True)
    (root / BINDINGS / session_id).write_text(session + "\n", encoding="utf-8")


def run(hook, root, payload, env=None, session_id="s1"):
    payload = {"session_id": session_id, "cwd": str(root), **payload}
    full_env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root), **(env or {})}
    return subprocess.run([sys.executable, str(HOOKS / hook)], input=json.dumps(payload),
                          capture_output=True, text=True, env=full_env, cwd=root)


def edit(root, rel, tool="Edit", agent=None, session_id="s1"):
    payload = {"tool_name": tool, "tool_input": {"file_path": str(root / rel)}}
    if agent:
        payload["agent_type"] = agent
    return run("scope.py", root, payload, session_id=session_id)


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


def test_paths_outside_the_project_pass(project, tmp_path):
    declare(project, "IMPLEMENT")
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "elsewhere.txt")}}
    assert decision(run("scope.py", project, payload)) is None


def test_non_write_tools_are_ignored(project):
    declare(project, "IMPLEMENT")
    assert decision(edit(project, "modules/m/contract.py", tool="Read")) is None


# ------------------------------------------------------------------ scope.py: Bash at top level

def bash(root, command, agent=None, session_id="s1"):
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    if agent:
        payload["agent_type"] = agent
    return run("scope.py", root, payload, session_id=session_id)


def test_a_shell_write_to_a_forbidden_path_is_denied(project):
    # The tool call and the heredoc are the same write; only one of them used to be seen.
    declare(project, "IMPLEMENT")
    assert decision(edit(project, "modules/m/conformance/test_x.py"))["permissionDecision"] == "deny"
    d = decision(bash(project, "cat > modules/m/conformance/test_x.py <<'EOF'\npass\nEOF"))
    assert d["permissionDecision"] == "deny"
    assert "IMPLEMENT" in d["permissionDecisionReason"]
    assert "Use Edit or Write" in d["permissionDecisionReason"]


def test_a_shell_write_inside_may_modify_is_denied_too(project):
    # The hook cannot read the path out of a shell command, so it cannot allow one either.
    declare(project, "IMPLEMENT")
    assert decision(edit(project, "modules/m/src/impl.py")) is None
    assert decision(bash(project, "sed -i s/a/b/ modules/m/src/impl.py"))["permissionDecision"] == "deny"


@pytest.mark.parametrize("command, allowed", [
    ("pytest -q", True),
    ("grep -rn Metres modules/ | head -5", True),
    ("git status --short", True),                    # git's effects are check_commit.py's
    ("python tooling/build_registry.py", True),      # a program that is checked in
    ("cat modules/m/src/impl.py", True),
    ("pytest -q 2>&1 | tail -5", True),              # a duplicated fd names no file
    ("pytest -q 2>&1 > out.txt", False),
    ("FOO=1 python tooling/build_layer.py", True),
    ("cat > modules/m/src/impl.py", False),
    ("pytest -q > out.txt", False),
    ("rm -rf modules", False),
    ("sudo mkdir docs", False),
    ("cat list | xargs rm", False),
    ("sed -i s/a/b/ f.py", False),
    ("find . -name '*.py' -delete", False),
    ("python - <<'PY'\nopen('x','w')\nPY", False),
    ("python -c \"open('x','w')\"", False),
])
def test_bash_is_allowed_only_when_it_cannot_write(project, command, allowed):
    declare(project, "IMPLEMENT")
    d = decision(bash(project, command))
    assert (d is None) == allowed, (command, d)


def test_the_declaration_command_itself_is_allowed_and_is_what_binds_the_session(project):
    # The command writes nothing; seeing it is how the hook learns the type, and it keys
    # that on the id the runtime handed it. The exact string is allowed, nothing near it.
    command = harness.declare_command("REVIEW")
    assert decision(bash(project, command)) is None
    assert (project / BINDINGS / "s1").read_text(encoding="utf-8").strip() == "REVIEW"
    assert decision(edit(project, "modules/m/src/impl.py"))["permissionDecision"] == "deny"
    assert decision(bash(project, command + " && rm -rf modules"))["permissionDecision"] == "deny"


def test_every_session_skill_declares_with_a_command_the_hook_allows():
    # The skill and the table are rendered from harness.declare_command; if they ever
    # drift, every session opens with a denied declaration.
    src = build_layer.Sources()
    table = json.loads(harness.render_session_table_json(
        src, framework=True, agents=[], test_command="pytest"))
    assert table["declare_commands"]
    for name, command in table["declare_commands"].items():
        assert f"!`{command}`" in harness.render_session_skill(
            src, name, [], [], framework=True)


def test_bash_without_a_declaration_warns_and_allows(project):
    first = bash(project, "rm -rf modules")
    assert decision(first) is None
    assert "no session declared" in first.stderr


def test_unknown_declared_type_is_denied(project):
    declare(project, "HACK")
    d = decision(edit(project, "modules/m/src/impl.py"))
    assert d["permissionDecision"] == "deny" and "HACK" in d["permissionDecisionReason"]


def test_no_table_means_nothing_to_enforce(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    assert decision(edit(root, "anything.py")) is None


# ------------------------------------------------------------------ scope.py: one binding per session

def test_two_sessions_in_one_tree_do_not_share_a_declaration(project):
    # The binding is keyed on the runtime's session id, so the second declaration does not
    # redefine the first session's scope. Both directions: each type's own writes stay
    # legal and the other's stay denied.
    declare(project, "IMPLEMENT", session_id="s1")
    declare(project, "CONTRACT", session_id="s2")
    assert decision(edit(project, "modules/m/src/impl.py", session_id="s1")) is None
    assert decision(edit(project, "modules/m/src/impl.py", session_id="s2"))["permissionDecision"] == "deny"
    assert decision(edit(project, "modules/m/contract.py", session_id="s2")) is None
    assert decision(edit(project, "modules/m/contract.py", session_id="s1"))["permissionDecision"] == "deny"


def test_a_concurrent_declaration_cannot_widen_a_query_session(project):
    # QUERY may modify nothing; it is the strictest row and the one most likely to be
    # trusted. A FRAMEWORK-shaped declaration made alongside it must not reach it.
    assert decision(bash(project, harness.declare_command("QUERY"), session_id="q")) is None
    assert decision(bash(project, harness.declare_command("IMPLEMENT"), session_id="i")) is None
    d = decision(edit(project, "modules/m/src/impl.py", session_id="q"))
    assert d["permissionDecision"] == "deny" and "QUERY" in d["permissionDecisionReason"]
    assert decision(edit(project, "modules/m/src/impl.py", session_id="i")) is None


def test_a_session_with_no_binding_is_undeclared_not_the_other_session(project):
    declare(project, "IMPLEMENT", session_id="s1")
    r = edit(project, "modules/m/contract.py", session_id="s2")
    assert decision(r) is None and "no session declared" in r.stderr


def test_a_binding_left_by_an_earlier_session_does_not_apply_to_a_new_one(project):
    # The stale-declaration defect needed no concurrency: one machine, one person, and a
    # session opened the next day without typing a skill.
    declare(project, "IMPLEMENT", session_id="yesterday")
    r = edit(project, "modules/m/conformance/test_x.py", session_id="today")
    assert decision(r) is None and "no session declared" in r.stderr


def test_a_session_id_that_is_not_a_usable_file_name_falls_through_to_the_warning(project):
    declare(project, "IMPLEMENT", session_id="s1")
    r = edit(project, "modules/m/contract.py", session_id="../s1")
    assert decision(r) is None and "no session declared" in r.stderr


def test_bindings_are_scratch_state_and_are_aged_out(project):
    declare(project, "IMPLEMENT", session_id="ancient")
    stale = project / BINDINGS / "ancient"
    os.utime(stale, (0, 0))
    assert decision(bash(project, harness.declare_command("REVIEW"), session_id="fresh")) is None
    assert not stale.exists()
    assert (project / BINDINGS / "fresh").exists()


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
