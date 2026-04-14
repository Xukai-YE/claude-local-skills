#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install or update the background supervisor hooks in ~/.claude/settings.json.
"""

from __future__ import annotations

import json
import pathlib
import shutil
from typing import Any


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
CLAUDE_HOME = pathlib.Path.home() / ".claude"
SETTINGS_PATH = CLAUDE_HOME / "settings.json"


def load_settings() -> dict[str, Any]:
    if not SETTINGS_PATH.exists():
        return {}
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def save_settings(settings: dict[str, Any]) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        backup = SETTINGS_PATH.with_suffix(".json.bak")
        shutil.copy2(SETTINGS_PATH, backup)
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def desired_hook(status_message: str) -> dict[str, Any]:
    return {
        "type": "command",
        "command": f'python "{SCRIPT_DIR / "bg_hook.py"}"',
        "async": True,
        "statusMessage": status_message,
    }


def ensure_event_hook(
    settings: dict[str, Any],
    event_name: str,
    status_message: str,
) -> None:
    hooks = settings.setdefault("hooks", {})
    event_hooks = hooks.setdefault(event_name, [])

    matcher_block: dict[str, Any] | None = None
    for item in event_hooks:
        if isinstance(item, dict) and item.get("matcher") == "Bash":
            matcher_block = item
            break
    if matcher_block is None:
        matcher_block = {"matcher": "Bash", "hooks": []}
        event_hooks.append(matcher_block)

    matcher_hooks = matcher_block.setdefault("hooks", [])
    wanted = desired_hook(status_message)
    if not any(
        isinstance(item, dict)
        and item.get("type") == wanted["type"]
        and item.get("command") == wanted["command"]
        for item in matcher_hooks
    ):
        matcher_hooks.append(wanted)


def main() -> None:
    settings = load_settings()
    ensure_event_hook(settings, "PostToolUse", "检测后台任务...")
    ensure_event_hook(settings, "PostToolUseFailure", "检测后台任务失败...")
    save_settings(settings)
    print(f"Installed background supervisor hooks into {SETTINGS_PATH}")


if __name__ == "__main__":
    main()
