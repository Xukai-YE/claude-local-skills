---
name: obsidian-writeback-ledger
description: Use after completing work that produced durable decisions, experiment results, failure reasons, changed paths, or next actions that should be preserved in Obsidian.
---

# Obsidian Writeback Ledger

Persist only the durable result of a task. Do not dump the full conversation,
full logs, source files, large tables, or temporary scratch text into Obsidian.

## What To Write

Write concise entries containing:

- decision or result
- reason or evidence
- modified file paths
- commands or checks run
- failure signature and root cause, if relevant
- remaining risks
- next recommended action

## Rules

1. Read the existing target note before writing.
2. Append short structured entries or edit the exact stale line; do not rewrite
   a long note wholesale.
3. If a canonical/source note already exists, update it instead of creating a
   duplicate summary note.
4. If current code or artifacts contradict Obsidian memory, write the conflict
   explicitly.
5. If a failed path should not be repeated, add a short failure entry to the
   relevant project memory note.
