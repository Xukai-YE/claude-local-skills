# Runtime Model

## Detection

The hook only tracks background Bash commands that look long-running.

Signals include:
- training or crawl-style verbs
- common long-run flags such as `--epochs`, `--steps`, `--iter`, `--count`
- loop- or watcher-like command patterns

Short commands like `git status` are ignored even if they run in the background.

## Supervision

- Job state is stored under `~/.claude/bg_jobs`
- The monitor prints a status line every 60 seconds
- A single monitor process owns the supervision loop

## Recovery Policy

- Restart budget: 2
- Repair budget: 1

If a tracked job fails:
1. restart while restart budget remains
2. invoke Claude Code repair when restart budget is exhausted
3. rerun only if the repair returns a verification command and that verification succeeds
4. mark the job `needs_human` when recovery is unsafe or exhausted

## Safety Limits

- No destructive recovery is attempted automatically
- Interrupted jobs are not auto-repaired
- Verification gates reruns after repair
