# Setup

## Purpose

Install a Claude Code hook pipeline that supervises long-running background Bash commands.

## Prerequisites

- Windows environment
- `python` on PATH
- `claude` on PATH
- Claude Code authenticated for non-interactive `claude -p` repair calls

## Install

From the installed skill directory:

```powershell
python scripts/install.py
```

That updates `~/.claude/settings.json` so both `PostToolUse` and `PostToolUseFailure` for `Bash` call `scripts/bg_hook.py`.

## Uninstall

```powershell
python scripts/uninstall.py
```

## Verify

- Open `~/.claude/settings.json`
- Confirm the hook command points at this skill's `scripts/bg_hook.py`
- Start a long-running background Bash command and confirm a monitor window appears
