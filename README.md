# Claude Local Skills

Installable package for local Claude skills from `~/.claude/skills`.

## Contents

- `background-supervisor-skill`
- `effort-calibration`
- `plan-review-collaboration`

## Install

```powershell
python scripts/install.py
```

To install into a custom Claude home:

```powershell
python scripts/install.py --claude-home "C:\Users\Administrator\.claude"
```

## Uninstall

```powershell
python scripts/uninstall.py
```

## Verify

```powershell
python -m unittest discover -s tests
```

## Notes

- This package copies only skill directories under `skills/`.
- It intentionally excludes credentials, settings, telemetry, history, cache, and session files.
- `background-supervisor-skill` has its own hook installer under `skills/background-supervisor-skill/scripts/install.py`; run that after installing this package if you want to wire Claude hooks.
