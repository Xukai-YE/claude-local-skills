#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared helpers for Claude background task monitoring and recovery.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any


CLAUDE_HOME = pathlib.Path.home() / ".claude"
BG_ROOT = CLAUDE_HOME / "bg_jobs"
EVENT_ROOT = BG_ROOT / "events"
INCIDENT_ROOT = BG_ROOT / "incidents"
MONITOR_LOCK = BG_ROOT / "monitor.lock"

LONG_RUNNING_KEYWORDS = (
    "train",
    "fit",
    "crawl",
    "spider",
    "scrape",
    "download",
    "wget",
    "serve",
    "server",
    "uvicorn",
    "gunicorn",
    "flask run",
    "fastapi",
    "watch",
    "loop",
    "while true",
    "tail -f",
    "--epoch",
    "--epochs",
    "--step",
    "--steps",
    "--iter",
    "--iters",
    "--count",
)

SHORT_COMMAND_PREFIXES = (
    "ls",
    "dir",
    "echo",
    "cat",
    "pwd",
    "cd",
    "git status",
    "git log",
    "python --version",
    "node --version",
    "which ",
)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def now_iso() -> str:
    return now_utc().isoformat()


def parse_iso(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def ensure_bg_dirs() -> None:
    BG_ROOT.mkdir(parents=True, exist_ok=True)
    EVENT_ROOT.mkdir(parents=True, exist_ok=True)
    INCIDENT_ROOT.mkdir(parents=True, exist_ok=True)


def should_monitor(command: str) -> bool:
    text = (command or "").strip().lower()
    if not text:
        return False
    if any(text == prefix or text.startswith(f"{prefix} ") for prefix in SHORT_COMMAND_PREFIXES):
        return False
    return any(keyword in text for keyword in LONG_RUNNING_KEYWORDS)


def make_job_id(session_id: str, tool_use_id: str, command: str) -> str:
    raw = "||".join((session_id or "", tool_use_id or "", command or ""))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def job_state_path(job_id: str) -> pathlib.Path:
    return BG_ROOT / f"{job_id}.json"


def stdout_log_path(job_id: str) -> pathlib.Path:
    return BG_ROOT / f"{job_id}.stdout.log"


def stderr_log_path(job_id: str) -> pathlib.Path:
    return BG_ROOT / f"{job_id}.stderr.log"


def incident_path(job_id: str) -> pathlib.Path:
    return INCIDENT_ROOT / f"{job_id}.incident.json"


def event_dump_path(job_id: str, event_name: str) -> pathlib.Path:
    stamp = now_utc().strftime("%Y%m%dT%H%M%S")
    safe_event = event_name.lower()
    return EVENT_ROOT / f"{stamp}-{job_id}-{safe_event}.json"


def load_json(path: pathlib.Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def merge_dict(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    merged.update(updates)
    return merged


def extract_job_from_hook(payload: dict[str, Any]) -> dict[str, Any] | None:
    if payload.get("hook_event_name") != "PostToolUse":
        return None
    if payload.get("tool_name") != "Bash":
        return None

    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "").strip()
    if not tool_input.get("run_in_background"):
        return None
    if not should_monitor(command):
        return None

    session_id = str(payload.get("session_id") or "")
    tool_use_id = str(payload.get("tool_use_id") or "")
    job_id = make_job_id(session_id, tool_use_id, command)
    created_at = now_iso()

    return {
        "job_id": job_id,
        "command": command,
        "cwd": str(payload.get("cwd") or ""),
        "session_id": session_id,
        "tool_use_id": tool_use_id,
        "transcript_path": str(payload.get("transcript_path") or ""),
        "permission_mode": str(payload.get("permission_mode") or ""),
        "status": "active",
        "created_at": created_at,
        "updated_at": created_at,
        "last_seen_at": created_at,
        "restart_count": 0,
        "repair_count": 0,
        "max_restarts": 2,
        "max_repairs": 1,
        "managed": False,
        "managed_pid": None,
        "stdout_log": str(stdout_log_path(job_id)),
        "stderr_log": str(stderr_log_path(job_id)),
        "last_stdout_size": 0,
        "last_stderr_size": 0,
        "last_output_at": None,
        "incident_kind": None,
        "incident_summary": None,
        "tool_response": payload.get("tool_response"),
    }


def extract_incident_from_hook(payload: dict[str, Any]) -> dict[str, Any] | None:
    if payload.get("hook_event_name") != "PostToolUseFailure":
        return None
    if payload.get("tool_name") != "Bash":
        return None

    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "").strip()
    if not tool_input.get("run_in_background"):
        return None
    if not should_monitor(command):
        return None

    session_id = str(payload.get("session_id") or "")
    tool_use_id = str(payload.get("tool_use_id") or "")
    job_id = make_job_id(session_id, tool_use_id, command)
    error = str(payload.get("error") or "Unknown background task failure")
    return {
        "job_id": job_id,
        "session_id": session_id,
        "tool_use_id": tool_use_id,
        "command": command,
        "cwd": str(payload.get("cwd") or ""),
        "transcript_path": str(payload.get("transcript_path") or ""),
        "kind": "tool_failure",
        "summary": error,
        "created_at": now_iso(),
        "is_interrupt": bool(payload.get("is_interrupt")),
    }


def choose_recovery_action(
    job: dict[str, Any],
    incident: dict[str, Any] | None,
) -> dict[str, Any]:
    if not incident:
        return {"action": "wait", "reason": "No active incident"}
    if incident.get("is_interrupt"):
        return {"action": "needs_human", "reason": "User interrupted the job"}

    restart_count = int(job.get("restart_count") or 0)
    repair_count = int(job.get("repair_count") or 0)
    max_restarts = int(job.get("max_restarts") or 0)
    max_repairs = int(job.get("max_repairs") or 0)

    if restart_count < max_restarts:
        return {"action": "restart", "reason": "Restart budget remains"}
    if repair_count < max_repairs:
        return {"action": "repair", "reason": "Restart budget exhausted; try repair"}
    return {"action": "needs_human", "reason": "Recovery budget exhausted"}


def job_from_incident(incident: dict[str, Any]) -> dict[str, Any]:
    created_at = incident.get("created_at") or now_iso()
    job_id = str(incident["job_id"])
    return {
        "job_id": job_id,
        "command": incident.get("command") or "",
        "cwd": incident.get("cwd") or "",
        "session_id": incident.get("session_id") or "",
        "tool_use_id": incident.get("tool_use_id") or "",
        "transcript_path": incident.get("transcript_path") or "",
        "permission_mode": "",
        "status": "failed",
        "created_at": created_at,
        "updated_at": created_at,
        "last_seen_at": created_at,
        "restart_count": 0,
        "repair_count": 0,
        "max_restarts": 2,
        "max_repairs": 1,
        "managed": False,
        "managed_pid": None,
        "stdout_log": str(stdout_log_path(job_id)),
        "stderr_log": str(stderr_log_path(job_id)),
        "last_stdout_size": 0,
        "last_stderr_size": 0,
        "last_output_at": None,
        "incident_kind": incident.get("kind"),
        "incident_summary": incident.get("summary"),
        "last_incident_at": created_at,
    }


def append_event_dump(job_id: str, event_name: str, payload: dict[str, Any]) -> None:
    ensure_bg_dirs()
    save_json(event_dump_path(job_id, event_name), payload)


def record_incident(job: dict[str, Any], incident: dict[str, Any]) -> dict[str, Any]:
    updates = {
        "status": "failed",
        "updated_at": now_iso(),
        "incident_kind": incident.get("kind"),
        "incident_summary": incident.get("summary"),
        "last_incident_at": incident.get("created_at") or now_iso(),
    }
    merged = merge_dict(job, updates)
    save_json(incident_path(merged["job_id"]), incident)
    save_json(job_state_path(merged["job_id"]), merged)
    return merged


def clear_incident(job_id: str) -> None:
    path = incident_path(job_id)
    if path.exists():
        path.unlink()


def iter_jobs() -> list[dict[str, Any]]:
    ensure_bg_dirs()
    jobs: list[dict[str, Any]] = []
    for path in BG_ROOT.glob("*.json"):
        payload = load_json(path)
        if isinstance(payload, dict) and "job_id" in payload:
            jobs.append(payload)
    return sorted(jobs, key=lambda item: item.get("created_at", ""))


def is_pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return str(pid) in result.stdout


def powershell_json(script: str, extra_env: dict[str, str] | None = None) -> Any:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def resolve_background_pid(job: dict[str, Any]) -> int | None:
    if job.get("managed_pid") and is_pid_alive(int(job["managed_pid"])):
        return int(job["managed_pid"])

    command = str(job.get("command") or "").strip()
    started_at = str(job.get("created_at") or "")
    if not command or not started_at:
        return None

    snippet = command[:180]
    script = r"""
$ErrorActionPreference = 'SilentlyContinue'
$cutoff = [DateTime]::Parse($env:BG_CUTOFF).AddMinutes(-2)
$match = $env:BG_MATCH
$items = Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -and $_.CommandLine.Contains($match) } |
  ForEach-Object {
    [PSCustomObject]@{
      pid = $_.ProcessId
      created_at = $_.CreationDate.ToUniversalTime().ToString("o")
      command_line = $_.CommandLine
    }
  }
$items | ConvertTo-Json -Compress
"""
    data = powershell_json(script, {"BG_MATCH": snippet, "BG_CUTOFF": started_at})
    if not data:
        return None
    candidates = data if isinstance(data, list) else [data]
    cutoff = parse_iso(started_at) or now_utc()
    fresh: list[tuple[dt.datetime, int]] = []
    for item in candidates:
        created_at = parse_iso(item.get("created_at"))
        pid = item.get("pid")
        if not created_at or not pid:
            continue
        if created_at >= cutoff - dt.timedelta(minutes=2):
            fresh.append((created_at, int(pid)))
    if not fresh:
        return None
    fresh.sort(key=lambda pair: pair[0], reverse=True)
    return fresh[0][1]


def update_job_output_state(job: dict[str, Any]) -> dict[str, Any]:
    updates: dict[str, Any] = {
        "updated_at": now_iso(),
        "last_seen_at": now_iso(),
    }
    saw_output = False
    for key, path_fn, size_key in (
        ("stdout", stdout_log_path, "last_stdout_size"),
        ("stderr", stderr_log_path, "last_stderr_size"),
    ):
        path = path_fn(job["job_id"])
        if not path.exists():
            continue
        size = path.stat().st_size
        prev_size = int(job.get(size_key) or 0)
        updates[size_key] = size
        if size > prev_size:
            saw_output = True
    if saw_output:
        updates["last_output_at"] = now_iso()
    return merge_dict(job, updates)


def tail_text(path: pathlib.Path, max_chars: int = 6000) -> str:
    if not path.exists():
        return ""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return content[-max_chars:]


def run_managed_background(job: dict[str, Any]) -> dict[str, Any]:
    ensure_bg_dirs()
    stdout_path = stdout_log_path(job["job_id"])
    stderr_path = stderr_log_path(job["job_id"])
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("a", encoding="utf-8") as stdout_handle, stderr_path.open(
        "a",
        encoding="utf-8",
    ) as stderr_handle:
        process = subprocess.Popen(
            job["command"],
            cwd=job.get("cwd") or None,
            shell=True,
            stdout=stdout_handle,
            stderr=stderr_handle,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
    updates = {
        "status": "active",
        "managed": True,
        "managed_pid": process.pid,
        "updated_at": now_iso(),
        "last_seen_at": now_iso(),
        "last_restart_at": now_iso(),
        "incident_kind": None,
        "incident_summary": None,
    }
    merged = merge_dict(job, updates)
    save_json(job_state_path(merged["job_id"]), merged)
    return merged


def write_status_line(message: str) -> None:
    sys.stdout.write(message + os.linesep)
    sys.stdout.flush()
