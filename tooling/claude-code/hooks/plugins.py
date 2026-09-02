#!/usr/bin/env python3
"""SessionStart hook: warn when plugins beyond the project's declared list are enabled (CORE-HRN-001).

Plugins install at user scope and follow the person, so a project cannot see which
operating layer a session actually runs under (F-47). The declared list is
`enabledPlugins` in .claude/settings.json, rendered from the profile fragments. This
hook compares it with the user's and the local settings and prints a warning, on stdout
so the session sees it as context. It never blocks: the human may add a plugin; the
hook makes the addition visible and names the classes the framework excludes.

Standard library only.
"""

import json
import os
import sys
from pathlib import Path

PROJECT_SETTINGS = ".claude/settings.json"
LOCAL_SETTINGS = ".claude/settings.local.json"
EXCLUDED = ("writes CLAUDE.md or trace records (P3)",
            "carries memory across sessions (P8)",
            "authors tests and implementation in one session (P8)",
            "overrides stop conditions (P10)")


def enabled_in(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    plugins = data.get("enabledPlugins") or {}
    return {name for name, on in plugins.items() if on} if isinstance(plugins, dict) else set()


def user_settings():
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    return config / "settings.json"


def main():
    data = json.load(sys.stdin)
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd())
    if not (root / PROJECT_SETTINGS).exists():
        return 0
    declared = enabled_in(root / PROJECT_SETTINGS)
    extra = sorted((enabled_in(user_settings()) | enabled_in(root / LOCAL_SETTINGS)) - declared)
    if not extra:
        return 0
    print(f"WARNING plugins enabled here but not declared in {PROJECT_SETTINGS}: {', '.join(extra)}. "
          "The declared list comes from the profile fragments (CORE-HRN-001). A plugin is excluded "
          "when it " + "; ".join(EXCLUDED) + ". Anything else may stay, but say so in the declaration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
