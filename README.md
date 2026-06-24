# Claude Local Skills

Custom Claude Code skills. Clone and run the install script to add them to your Claude setup.

## Custom Skills (6)

| Skill | Description |
|-------|-------------|
| `background-supervisor-skill` | Automatic Python-based supervision for long-running Claude Code background tasks. Installs hook-driven monitoring into `~/.claude/settings.json`. |
| `effort-calibration` | Effort auto-calibration - internally rates task difficulty (low/medium/high/max) before responding, adapting analysis depth and output structure accordingly. Always active. |
| `obsidian-memory-router` | Read-only Obsidian project-memory routing with a small first-pass note budget. |
| `obsidian-research-memory` | F-drive research-memory routing for EZSpecificity, substrate predictability, experiment progress, and Obsidian sync/update work. |
| `obsidian-writeback-ledger` | Compact writeback ledger for durable decisions, results, failure reasons, and next actions. |
| `plan-review-collaboration` | Plan review collaboration for complex experiments, research routes, system design, and multi-stage implementations. Auto-triggers when tasks have multi-step dependencies or high error cost. |

## Official Plugins

See [OFFICIAL_PLUGINS.md](OFFICIAL_PLUGINS.md) for the full index of 33 official plugins + 16 external plugins from Anthropic.

Quick install all official plugins in Claude Code:
```
/plugins add anthropics/claude-plugins-official
```

---

## Install Custom Skills

```powershell
python scripts/install.py
```

Install to a specific Claude home:

```powershell
python scripts/install.py --claude-home "C:\Users\YourName\.claude"
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

- Skills are installed from the `skills/` directory.
- `background-supervisor-skill` has its own hook installer - run `skills/background-supervisor-skill/scripts/install.py` after installing to wire Claude hooks.
- Credentials, settings, telemetry, history, cache, and session files are intentionally excluded.
