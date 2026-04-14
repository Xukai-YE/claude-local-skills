---
name: background-supervisor-skill
description: Enable automatic Python-based supervision for long-running Claude Code background Bash tasks. Use when you want background programs to emit periodic monitor output and have Claude Code review, verify, and rerun jobs after failures. Installs and maintains hook-driven monitoring in ~/.claude/settings.json.
allowed-tools: "Bash,Read,Edit,Write"
---

# Background Supervisor

This skill turns long-running background Bash tasks into supervised jobs.

When active, the expected outcome is:
- a Python monitor prints background status every 60 seconds
- failed jobs are retried with bounded restart limits
- exhausted restart budgets trigger a Claude Code review/repair attempt
- verified repairs restart the original job

## Use This Skill When

- The user wants long-running background programs to be monitored automatically
- The user wants periodic terminal output from background jobs
- The user wants Claude Code to review and attempt repair when background jobs fail
- The user wants the behavior wired into Claude Code globally through hooks

## Workflow

1. Verify prerequisites:
   - `python` is available on PATH
   - `claude` CLI is available on PATH and authenticated
   - The environment is Windows-oriented, because PID attachment uses `tasklist` and PowerShell process inspection
2. Install or refresh the global hooks:
   - Run `python "$CLAUDE_PLUGIN_ROOT/scripts/install.py"`
3. Verify the install:
   - Inspect `~/.claude/settings.json`
   - Confirm both `PostToolUse` and `PostToolUseFailure` have Bash hooks pointing to `bg_hook.py`
4. Explain the runtime model briefly:
   - monitor interval is 60 seconds
   - restart budget is 2
   - repair budget is 1
   - verified fixes are required before rerun
5. If the user wants to disable the behavior:
   - Run `python "$CLAUDE_PLUGIN_ROOT/scripts/uninstall.py"`

## Runtime Files

- `scripts/bg_hook.py`: receives Claude hook events and persists job state
- `scripts/bg_monitor.py`: watches job state, prints status, restarts jobs, and escalates repairs
- `scripts/bg_repair.py`: invokes Claude Code non-interactively for bounded repair attempts
- `scripts/bg_common.py`: shared helpers and recovery policy

## Notes

- This skill is intentionally narrow. It focuses on background Bash jobs, not general service orchestration.
- It works best for commands that are clearly long-running and safe to restart.
- For setup details, see `references/setup.md`.
- For runtime behavior and safety limits, see `references/runtime-model.md`.
