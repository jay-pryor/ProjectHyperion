#!/usr/bin/env python3
"""PreToolUse hook: deny a write outside the declared session's globs (CORE-HRN-001, M3).

Session scope used to be a rule the model remembered. This hook reads the type declared
by the session making the call and the globs build_layer.py rendered from the
session-types block of CORE-SES-001 into .hyperion/session-types.json, and denies an
Edit, Write, MultiEdit, or NotebookEdit whose path is outside them. Inside a subagent it
applies that agent's own row instead: a lens agent may write nothing but
trace/findings.yaml and may run only the project's test command.

The type is bound to the harness's session id, not to the working tree. A skill declares
by running a shell command the hook already recognises by exact string; on seeing one the
hook records the type at .hyperion/sessions/<session_id>, keyed by the id it was handed
and never by anything the command carries -- a session that could restate its own type
could widen it. So two sessions in one working tree cannot overwrite each other's scope,
and a binding left by yesterday's session is not inherited by today's. Recording on
PreToolUse, before the command runs, is not early: the record is the whole effect of
declaring and the echo only tells the human. Bindings are scratch state, aged out.

Bash is denied whenever it can write, because the hook cannot tell which path a shell
command writes and no parse of a shell command is sound enough to try (a quoting trick
re-opens the hole). Writes therefore go through the four tools whose path is a field the
hook can read. What that leaves allowed is reading, and running a program that is checked
into the repository: `writes_via` does not classify what such a program does, and `git`
is deliberately not in it because what git changes is exactly what the diff shows. Those
are check_commit.py's, over the real paths of a commit; this hook is the first layer, not
the sound one.

No session declared: every write is allowed and a one-line warning goes to stderr once
per Claude Code session. A session with no binding of its own is undeclared whatever any
other session declared. Paths outside the project are not the table's business and pass.

Standard library only; the hook needs no framework path. The glob matcher mirrors
check_commit.matches and tooling/tests/test_hooks.py asserts they agree.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

TABLE = ".hyperion/session-types.json"
SESSION_DIR = ".hyperion/sessions"
BINDING_MAX_AGE = 7 * 86400        # older than any session that is still running
SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}")   # it becomes a file name
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SHELL_CHAIN = re.compile(r"[;&|<>`$]|\n")

# The shell's ordinary write channel, recognised without extracting a path from it.
SEGMENTS = re.compile(r"[;&|]+|\n")
FD_DUP = re.compile(r"\d?>&[\d-]")               # `2>&1` names no file and cannot write one
PREFIXES = {"sudo", "env", "time", "nohup", "command", "exec", "xargs", "nice", "then", "do"}
WRITE_VERBS = {"cp", "dd", "install", "ln", "mkdir", "mv", "patch", "rm", "rmdir",
               "rsync", "shred", "tee", "touch", "truncate", "unlink"}
STREAM_EDITORS = {"sed", "perl", "awk", "gawk", "ruby"}
INTERPRETERS = {"python", "python3", "node", "perl", "ruby", "sh", "bash", "zsh"}


def writes_via(command):
    """How this shell command can write, or None when nothing in it can.

    Deliberately blunt: four shapes, no path extraction. A checked-in program run by
    name is allowed and is not classified -- that is the line the rule draws.
    """
    if ">" in FD_DUP.sub("", command):
        return "a redirection (`>`)"
    for segment in SEGMENTS.split(command):
        tokens = segment.split()
        while tokens and (tokens[0] in PREFIXES
                          or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[0])):
            tokens = tokens[1:]                      # `sudo`, `xargs`, `FOO=1` and friends
        if not tokens:
            continue
        head = tokens[0].rsplit("/", 1)[-1]
        rest = tokens[1:]
        if head in WRITE_VERBS:
            return f"`{head}`"
        if head in STREAM_EDITORS and any(re.fullmatch(r"-[A-Za-z]*i[A-Za-z]*", t) for t in rest):
            return f"`{head} -i`"
        if head == "find" and any(t in ("-delete", "-exec", "-execdir") for t in rest):
            return "`find` with an action"
        if head in INTERPRETERS and ("<<" in segment or "-c" in rest or "-" in rest):
            return f"an inline program handed to `{head}`"
    return None


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


def binding_path(root, session_id, suffix=""):
    """Where this session's binding lives, or None when the harness handed no usable id.

    No id means no binding can be keyed, and the caller falls through to warn-and-allow;
    it must never fall back to a shared file, which is the defect this keying removes.
    """
    if not session_id or not SESSION_ID.fullmatch(session_id):
        return None
    return root / SESSION_DIR / (session_id + suffix)


def reap(directory):
    """Drop bindings older than BINDING_MAX_AGE. This is scratch state, not a record."""
    cutoff = time.time() - BINDING_MAX_AGE
    for stale in directory.glob("*"):
        try:
            if stale.stat().st_mtime < cutoff:
                stale.unlink()
        except OSError:
            pass                                   # a concurrent session got there first


def write_binding(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    reap(path.parent)                              # the only two moments this directory grows
    path.write_text(text, encoding="utf-8")


def declared_type(root, session_id):
    """The type this session declared, or "" when it declared none."""
    path = binding_path(root, session_id)
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def record(root, session_id, name):
    path = binding_path(root, session_id)
    if path is not None:
        write_binding(path, name + "\n")


def warn_once(root, session_id):
    marker = binding_path(root, session_id, suffix=".warned") or (root / SESSION_DIR / "-.warned")
    if marker.exists():
        return
    write_binding(marker, "")
    print("WARNING no session declared by this session; writes are unrestricted. "
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
    tool = data.get("tool_name")
    if tool != "Bash" and tool not in WRITE_TOOLS:
        return 0

    rel = None
    session_id = data.get("session_id")
    command = ((data.get("tool_input") or {}).get("command") or "").strip()
    if tool in WRITE_TOOLS:
        rel = relative(root, written_path(data) or "")
        if rel is None:
            return 0                               # outside the project
    else:
        declared = {c: n for n, c in (table.get("declare_commands") or {}).items()}.get(command)
        if declared:
            record(root, session_id, declared)     # the type comes from the table the hook
            return 0                               # reads, keyed by the id it was handed
    session = declared_type(root, session_id)
    if not session:
        warn_once(root, session_id)
        return 0
    types = table.get("types") or {}
    if session not in types:
        return deny(f"this session is bound to {session!r}, which is not a session type here "
                    f"({', '.join(types)}); redeclare with a skill (CORE-SES-001)")
    if tool == "Bash":
        how = writes_via(command)
        if how is None:
            return 0
        return deny(f"{session}: this command can write ({how}), and the hook cannot tell which "
                    "path a shell command writes. Use Edit or Write, where the path is checked "
                    "against the type's globs, or run a script that is checked in (CORE-HRN-001)")
    return check_globs(rel, session, types[session])


if __name__ == "__main__":
    sys.exit(main())
