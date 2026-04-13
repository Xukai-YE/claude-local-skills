#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code async hook for background Bash tasks.

Responsibilities:
- detect long-running background Bash jobs from hook payloads
- persist per-job state and failure incidents
- ensure the standalone monitor is running
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import bg_common


def load_payload() -> dict:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def monitor_alive() -> bool:
    lock = bg_common.load_json(bg_common.MONITOR_LOCK, {})
    if not isinstance(lock, dict):
        return False
    if lock.get("status") == "starting":
        created_at = bg_common.parse_iso(lock.get("created_at"))
        if created_at and (bg_common.now_utc() - created_at).total_seconds() < 30:
            return True
    pid = lock.get("pid")
    return isinstance(pid, int) and bg_common.is_pid_alive(pid)


def ensure_monitor_running() -> None:
    bg_common.ensure_bg_dirs()
    if monitor_alive():
        return

    bg_common.save_json(
        bg_common.MONITOR_LOCK,
        {"status": "starting", "created_at": bg_common.now_iso()},
    )
    monitor_script = pathlib.Path(__file__).resolve().parent / "bg_monitor.py"
    try:
        subprocess.Popen(
            f'start "Claude 后台监控" cmd /k python "{monitor_script}"',
            shell=True,
        )
    except OSError:
        pass


def handle_post_tool_use(payload: dict) -> bool:
    job = bg_common.extract_job_from_hook(payload)
    if not job:
        return False

    job["managed_pid"] = bg_common.resolve_background_pid(job)
    bg_common.save_json(bg_common.job_state_path(job["job_id"]), job)
    bg_common.append_event_dump(job["job_id"], "PostToolUse", payload)
    return True


def handle_post_tool_use_failure(payload: dict) -> bool:
    incident = bg_common.extract_incident_from_hook(payload)
    if not incident:
        return False

    job = bg_common.load_json(bg_common.job_state_path(incident["job_id"]), {})
    if not isinstance(job, dict) or not job:
        job = bg_common.job_from_incident(incident)
    bg_common.append_event_dump(incident["job_id"], "PostToolUseFailure", payload)
    bg_common.record_incident(job, incident)
    return True


def main() -> None:
    payload = load_payload()
    if not payload:
        return

    handled = False
    event_name = payload.get("hook_event_name")
    if event_name == "PostToolUse":
        handled = handle_post_tool_use(payload)
    elif event_name == "PostToolUseFailure":
        handled = handle_post_tool_use_failure(payload)

    if handled:
        ensure_monitor_running()


if __name__ == "__main__":
    main()
