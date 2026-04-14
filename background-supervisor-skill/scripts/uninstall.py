#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove the background supervisor hooks from ~/.claude/settings.json.
"""

from __future__ import annotations

import json
import pathlib
import shutil
from typing import Any


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
CLAUDE_HOME = pathlib.Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_HOME / "settings.json"
HOOK_COMMAND = f'python "{SCRIPT_DIR / "bg_hook.py"}"'


def load_settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        return {}
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def save_settings(settings: dict[str, Any]) -> None:
    if SETTINGS_PATH.exists():
        backup = SETTINGS_PATH.with_suffix(".json.bak")
        shutil.copy2(SETTINGS_PATH, backup)
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def prune_event(settings: dict[str, Any], event_name: str) -> None:
    hooks = settings.get("hooks", {})
    event_hooks = hooks.get(event_name, [])
    pruned: list[dict[str, Any]] = []
    for item in event_hooks:
        if not isinstance(item, dict):
            continue
        if item.get("matcher") != "Bash":
            pruned.append(item)
            continue
        hook_list = [
            hook
            for hook in item.get("hooks", [])
            if not (
                isinstance(hook, dict)
                and hook.get("type") == "command"
                and hook.get("command") == HOOK_COMMAND
            )
        ]
        if hook_list:
            item = dict(item)
            item["hooks"] = hook_list
            pruned.append(item)
    if pruned:
        hooks[event_name] = pruned
    elif event_name in hooks:
        del hooks[event_name]


def main() -> None:
    if not SETTINGS_PATH.exists():
        print(f"No settings file at {SETTINGS_PATH}")
        return

    settings = load_settings()
    prune_event(settings, "PostToolUse")
    prune_event(settings, "PostToolUseFailure")
    save_settings(settings)
    print(f"Removed background supervisor hooks from {SETTINGS_PATH}")


if __name__ == "__main__":
    main()
