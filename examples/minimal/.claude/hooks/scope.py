#!/usr/bin/env python3
"""PreToolUse hook: deny a write outside the declared session's globs (CORE-HRN-001, M3).

Session scope used to be a rule the model remembered. This hook reads the type the
declaration wrote to .hyperion/session and the globs build_layer.py rendered from the
session-types block of CORE-SES-001 into .hyperion/session-types.json, and denies an
Edit, Write, MultiEdit, or NotebookEdit whose path is outside them. Inside a subagent it
applies that agent's own row instead: a lens agent may write nothing but
trace/findings.yaml and may run only the project's test command.

No session declared: every write is allowed and a one-line warning goes to stderr once
per Claude Code session. Paths outside the project are not the table's business and pass.

Standard library only; the hook needs no framework path. The glob matcher mirrors
check_commit.matches and tooling/tests/test_hooks.py asserts they agree.
"""

import json
import os
import re
import sys
from pathlib import Path

TABLE = ".hyperion/session-types.json"
SESSION_FILE = ".hyperion/session"
WARNED_FILE = ".hyperion/session-warned"
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_CHAIN = re.compile(r"[;&|<>`$]|\n")


def matches(path, glob):
    """fnmatch with `**` spanning directories and `*` staying inside one segment."""
    pattern = re.escape(glob).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.fullmatch(pattern, path) is not None


def first_match(path, globs):
    return next((g for g in globs if matches(path, g)), None)


def find_root(start):
    for d in [start, *start.parents]:
        if (d / TABLE).exists():
            return d
    return None


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": reason}}))
    return 0


def written_path(data):
    ti = data.get("tool_input") or {}
    return ti.get("file_path") or ti.get("notebook_path")


def relative(root, path):
    """Project-relative posix path, or None when the path is outside the project."""
    try:
        return Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        return None


def warn_once(root, session_id):
    marker = root / WARNED_FILE
    stamp = session_id or "-"
    if marker.exists() and marker.read_text(encoding="utf-8").strip() == stamp:
        return
    marker.write_text(stamp + "\n", encoding="utf-8")
    print(f"WARNING no session declared in {SESSION_FILE}; writes are unrestricted. "
          "Open the session with its skill (/implement, /conformance, ...) (CORE-HRN-001)",
          file=sys.stderr)


def check_globs(rel, label, row):
    hit = first_match(rel, row.get("must_not_modify") or [])
    if hit:
        return deny(f"{label} must not modify {rel} (matches `{hit}`; CORE-SES-001)")
    if first_match(rel, row.get("may_modify") or []) is None:
        allowed = ", ".join(f"`{g}`" for g in row.get("may_modify") or []) or "nothing"
        return deny(f"{rel} is outside what {label} may modify ({allowed}; CORE-SES-001)")
    return 0


def check_agent(data, root, table, agent, row):
    tool = data.get("tool_name")
    if tool == "Bash":
        command = ((data.get("tool_input") or {}).get("command") or "").strip()
        test = table.get("test_command") or "pytest"
        if command.startswith(test) and not SHELL_CHAIN.search(command):
            return 0
        return deny(f"{agent} may run only the test command `{test}`; it reports and never fixes "
                    "(CORE-HRN-001)")
    if tool not in WRITE_TOOLS:
        return 0
    rel = relative(root, written_path(data) or "")
    if rel is None:
        return 0
    return check_globs(rel, f"agent {agent}", row)


def main():
    data = json.load(sys.stdin)
    start = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()).resolve()
    root = find_root(start)
    if root is None:
        return 0                                   # nothing generated here; nothing to enforce
    table = json.loads((root / TABLE).read_text(encoding="utf-8"))

    agent = data.get("agent_type")
    row = (table.get("agents") or {}).get(agent) if agent else None
    if row:
        return check_agent(data, root, table, agent, row)
    if data.get("tool_name") not in WRITE_TOOLS:
        return 0

    rel = relative(root, written_path(data) or "")
    if rel is None or rel == SESSION_FILE:
        return 0
    session_path = root / SESSION_FILE
    session = session_path.read_text(encoding="utf-8").strip() if session_path.exists() else ""
    if not session:
        warn_once(root, data.get("session_id"))
        return 0
    types = table.get("types") or {}
    if session not in types:
        return deny(f"{SESSION_FILE} names {session!r}, which is not a session type here "
                    f"({', '.join(types)}); redeclare with a skill (CORE-SES-001)")
    return check_globs(rel, session, types[session])


if __name__ == "__main__":
    sys.exit(main())
