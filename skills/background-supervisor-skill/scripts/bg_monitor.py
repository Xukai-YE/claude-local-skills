#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone monitor for Claude background jobs.
"""

from __future__ import annotations

import os
import time
from typing import Any

import bg_common
import bg_repair


INTERVAL_SECONDS = 60


def acquire_monitor_lock() -> bool:
    bg_common.ensure_bg_dirs()
    current_pid = os.getpid()
    existing = bg_common.load_json(bg_common.MONITOR_LOCK, {})
    if isinstance(existing, dict):
        pid = existing.get("pid")
        if isinstance(pid, int) and pid != current_pid and bg_common.is_pid_alive(pid):
            print(f"[monitor] another monitor is already running with pid {pid}")
            return False
    bg_common.save_json(
        bg_common.MONITOR_LOCK,
        {
            "pid": current_pid,
            "status": "running",
            "created_at": bg_common.now_iso(),
        },
    )
    return True


def release_monitor_lock() -> None:
    lock = bg_common.load_json(bg_common.MONITOR_LOCK, {})
    if isinstance(lock, dict) and lock.get("pid") == os.getpid():
        bg_common.MONITOR_LOCK.unlink(missing_ok=True)


def save_job(job: dict[str, Any]) -> dict[str, Any]:
    bg_common.save_json(bg_common.job_state_path(job["job_id"]), job)
    return job


def print_job_line(job: dict[str, Any], message: str) -> None:
    now = time.strftime("%H:%M:%S")
    print(
        f"[{now}] job={job['job_id']} status={job.get('status')} "
        f"restarts={job.get('restart_count', 0)} repairs={job.get('repair_count', 0)} "
        f"{message}"
    )


def default_incident(job: dict[str, Any]) -> dict[str, Any]:
    pid = job.get("managed_pid")
    return {
        "job_id": job["job_id"],
        "session_id": job.get("session_id") or "",
        "tool_use_id": job.get("tool_use_id") or "",
        "command": job.get("command") or "",
        "cwd": job.get("cwd") or "",
        "transcript_path": job.get("transcript_path") or "",
        "kind": "process_exit",
        "summary": f"Background process {pid} is no longer running",
        "created_at": bg_common.now_iso(),
        "is_interrupt": False,
    }


def materialize_incident(job: dict[str, Any]) -> dict[str, Any] | None:
    incident = bg_common.load_json(bg_common.incident_path(job["job_id"]), {})
    if isinstance(incident, dict) and incident:
        return incident
    if job.get("incident_kind") or job.get("incident_summary"):
        return {
            "job_id": job["job_id"],
            "session_id": job.get("session_id") or "",
            "tool_use_id": job.get("tool_use_id") or "",
            "command": job.get("command") or "",
            "cwd": job.get("cwd") or "",
            "transcript_path": job.get("transcript_path") or "",
            "kind": job.get("incident_kind") or "unknown_failure",
            "summary": job.get("incident_summary") or "Unknown background incident",
            "created_at": bg_common.now_iso(),
            "is_interrupt": False,
        }
    return None


def restart_job(job: dict[str, Any], incident: dict[str, Any]) -> dict[str, Any]:
    job = bg_common.merge_dict(
        job,
        {
            "status": "restarting",
            "restart_count": int(job.get("restart_count") or 0) + 1,
            "updated_at": bg_common.now_iso(),
        },
    )
    save_job(job)
    print_job_line(job, f"incident={incident['kind']} action=restart")
    restarted = bg_common.run_managed_background(job)
    bg_common.clear_incident(job["job_id"])
    return restarted


def repair_job(job: dict[str, Any], incident: dict[str, Any]) -> dict[str, Any]:
    job = bg_common.merge_dict(
        job,
        {
            "status": "repairing",
            "repair_count": int(job.get("repair_count") or 0) + 1,
            "updated_at": bg_common.now_iso(),
        },
    )
    save_job(job)
    print_job_line(job, f"incident={incident['kind']} action=repair")

    result = bg_repair.attempt_repair(job, incident)
    job = bg_common.merge_dict(
        job,
        {
            "last_repair_at": bg_common.now_iso(),
            "last_repair_summary": result.get("summary"),
            "last_verify_command": result.get("verify_command"),
            "last_verify_output": result.get("verify_output"),
        },
    )
    if result.get("status") == "fixed" and result.get("verified"):
        save_job(job)
        restarted = bg_common.run_managed_background(job)
        bg_common.clear_incident(job["job_id"])
        print_job_line(restarted, "repair verified and job restarted")
        return restarted

    job = bg_common.merge_dict(
        job,
        {
            "status": "needs_human",
            "updated_at": bg_common.now_iso(),
            "incident_kind": incident.get("kind"),
            "incident_summary": result.get("summary") or incident.get("summary"),
        },
    )
    save_job(job)
    print_job_line(job, "repair could not verify safely; escalated to human")
    return job


def handle_failed_job(job: dict[str, Any]) -> dict[str, Any]:
    incident = materialize_incident(job)
    decision = bg_common.choose_recovery_action(job, incident)
    action = decision["action"]
    if action == "restart" and incident:
        return restart_job(job, incident)
    if action == "repair" and incident:
        return repair_job(job, incident)

    job = bg_common.merge_dict(
        job,
        {
            "status": "needs_human",
            "updated_at": bg_common.now_iso(),
        },
    )
    save_job(job)
    print_job_line(job, f"action=needs_human reason={decision['reason']}")
    return job


def track_active_job(job: dict[str, Any]) -> dict[str, Any]:
    job = bg_common.update_job_output_state(job)
    pid = job.get("managed_pid")

    if pid and bg_common.is_pid_alive(int(pid)):
        save_job(job)
        print_job_line(job, f"pid={pid} alive")
        return job

    if not pid:
        resolved = bg_common.resolve_background_pid(job)
        if resolved:
            job = bg_common.merge_dict(
                job,
                {
                    "managed_pid": resolved,
                    "updated_at": bg_common.now_iso(),
                },
            )
            save_job(job)
            print_job_line(job, f"pid={resolved} attached")
            return job
        save_job(job)
        print_job_line(job, "awaiting a resolvable pid")
        return job

    incident = materialize_incident(job) or default_incident(job)
    job = bg_common.record_incident(job, incident)
    print_job_line(job, f"pid={pid} exited; incident recorded")
    return handle_failed_job(job)


def monitor_cycle() -> None:
    jobs = bg_common.iter_jobs()
    if not jobs:
        print(f"[{time.strftime('%H:%M:%S')}] no tracked background jobs")
        return

    for job in jobs:
        status = job.get("status")
        if status == "active":
            track_active_job(job)
        elif status == "failed":
            handle_failed_job(job)
        elif status == "needs_human":
            print_job_line(job, "waiting for manual intervention")
        else:
            print_job_line(job, "idle")


def main() -> None:
    if not acquire_monitor_lock():
        return

    print("=" * 72)
    print("Claude Code background supervisor monitor")
    print("=" * 72)
    print("Press Ctrl+C to stop the monitor window.\n")

    try:
        while True:
            monitor_cycle()
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[monitor] stopped by user")
    finally:
        release_monitor_lock()


if __name__ == "__main__":
    main()
