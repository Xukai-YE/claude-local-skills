#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Invoke Claude CLI to attempt a bounded repair for a failed background job.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
from typing import Any

import bg_common


REPAIR_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["fixed", "needs_human"]},
            "summary": {"type": "string"},
            "verify_command": {"type": "string"},
        },
        "required": ["status", "summary", "verify_command"],
        "additionalProperties": False,
    }
)


def build_repair_prompt(job: dict[str, Any], incident: dict[str, Any]) -> str:
    stdout_tail = bg_common.tail_text(bg_common.stdout_log_path(job["job_id"]))
    stderr_tail = bg_common.tail_text(bg_common.stderr_log_path(job["job_id"]))
    return f"""Background job supervision needs a bounded autonomous repair.

Repository/CWD: {job.get('cwd') or '<unknown>'}
Command: {job.get('command') or '<unknown>'}
Session: {job.get('session_id') or '<unknown>'}
Tool use id: {job.get('tool_use_id') or '<unknown>'}
Transcript: {job.get('transcript_path') or '<unknown>'}

Incident kind: {incident.get('kind') or '<unknown>'}
Incident summary: {incident.get('summary') or '<unknown>'}

Recent stdout tail:
{stdout_tail or '<empty>'}

Recent stderr tail:
{stderr_tail or '<empty>'}

Requirements:
1. Diagnose the root cause from the available context.
2. Apply the minimal safe fix in the current working directory.
3. Run a targeted verification command proving the fix.
4. Respond only with JSON matching the schema.
5. Use status "needs_human" if the fix is unsafe, unclear, destructive, or not verified.
"""


def run_verify_command(job: dict[str, Any], command: str) -> tuple[bool, str]:
    if not command.strip():
        return False, "Missing verification command"
    result = subprocess.run(
        command,
        cwd=job.get("cwd") or None,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output[-6000:]


def attempt_repair(job: dict[str, Any], incident: dict[str, Any]) -> dict[str, Any]:
    prompt = build_repair_prompt(job, incident)
    command = [
        "claude",
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "bypassPermissions",
        "--add-dir",
        job.get("cwd") or ".",
        "--json-schema",
        REPAIR_SCHEMA,
        prompt,
    ]
    result = subprocess.run(
        command,
        cwd=job.get("cwd") or None,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {
            "status": "needs_human",
            "summary": f"Claude repair invocation failed: {result.stderr.strip() or result.stdout.strip() or 'unknown error'}",
            "verify_command": "",
            "verified": False,
            "verify_output": "",
        }

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "status": "needs_human",
            "summary": f"Claude repair returned invalid JSON: {result.stdout[-1000:]}",
            "verify_command": "",
            "verified": False,
            "verify_output": "",
        }

    verify_command = str(payload.get("verify_command") or "")
    verified = False
    verify_output = ""
    if payload.get("status") == "fixed":
        verified, verify_output = run_verify_command(job, verify_command)
        if not verified:
            payload["status"] = "needs_human"
            payload["summary"] = (
                f"{payload.get('summary') or 'Repair attempted'}, but verification failed"
            )
    payload["verified"] = verified
    payload["verify_output"] = verify_output
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()

    job = bg_common.load_json(bg_common.job_state_path(args.job_id), {})
    incident = bg_common.load_json(bg_common.incident_path(args.job_id), {})
    if not job or not incident:
        print(
            json.dumps(
                {
                    "status": "needs_human",
                    "summary": "Missing job state or incident context",
                    "verify_command": "",
                    "verified": False,
                    "verify_output": "",
                }
            )
        )
        return

    result = attempt_repair(job, incident)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
