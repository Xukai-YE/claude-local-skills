---
name: obsidian-memory-router
description: Use when a task needs read-only project context from a generic Obsidian vault, especially when only a small number of relevant notes should be loaded before acting.
---

# Obsidian Memory Router

Use Obsidian as a compact project memory layer without reading the whole vault.

## Vault Path

Read the vault root from `OBSIDIAN_VAULT`. If that is not set, look for a local
`.claude/obsidian_vault` file containing one path.

Do not hardcode a generic vault path in this skill. Project-specific skills can
name their own canonical vaults.

## First Pass

Read only:

1. the global index
2. the project card
3. at most three task-relevant notes
4. relevant sections instead of entire long notes when possible

Expand only when the project card points to another note, the user asks about a
previous decision, an experiment result is needed, a known failure may match the
current error, or current code contradicts memory.

## Conflict Rules

If Obsidian conflicts with current code or current user instructions, trust the
current user instruction first, current code and tests second, and Obsidian as
historical context. Report the conflict explicitly.
