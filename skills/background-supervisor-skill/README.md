# Background Supervisor Skill

Claude Code skill for supervised long-running background Bash jobs.

## What It Does

- Detects background Bash commands that are likely long-running and worth monitoring
- Starts a lightweight Python monitor that prints status every 60 seconds
- Falls back to liveness, log growth, recent activity, and key counters when true progress is unavailable
- Retries failed jobs with a bounded restart budget
- Invokes Claude Code non-interactively to review and repair failed jobs before rerunning them

## Scope

This is intentionally narrow. It is for:
- long-running background tasks
- cases where the user wants periodic progress visibility
- safe bounded restart and repair loops

It is not a general-purpose service orchestrator.

## Install

1. Copy this skill into your Claude skills directory, or install it via your preferred skill workflow.
2. Run:

```powershell
python scripts/install.py
```

3. Verify that `~/.claude/settings.json` now contains Bash hooks for both:
- `PostToolUse`
- `PostToolUseFailure`

## Uninstall

```powershell
python scripts/uninstall.py
```

## Layout

- [SKILL.md](./SKILL.md)
- [scripts/bg_hook.py](./scripts/bg_hook.py)
- [scripts/bg_monitor.py](./scripts/bg_monitor.py)
- [scripts/bg_repair.py](./scripts/bg_repair.py)
- [scripts/bg_common.py](./scripts/bg_common.py)
- [references/setup.md](./references/setup.md)
- [references/runtime-model.md](./references/runtime-model.md)

## Requirements

- Windows
- `python` on PATH
- `claude` CLI on PATH
- Claude Code authenticated for `claude -p` repair calls
