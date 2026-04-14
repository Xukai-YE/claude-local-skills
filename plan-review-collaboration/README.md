# plan-review-collaboration

A Claude Code skill that enforces a structured draft → external review → selective adoption → final output workflow for complex plans, experiment designs, research routes, and multi-stage engineering tasks.

## What it does

When triggered, instead of immediately outputting a plan, Claude:

1. **Drafts a complete, executable plan** independently (no placeholders, no outlines)
2. **Resolves relevant context paths** from a local memory file (project background, experiment history, prior results)
3. **Calls a local Codex CLI instance** as a reviewer, passing the plan and context file paths so Codex reads them before reviewing
4. **Evaluates each suggestion** — adopts only those that meaningfully improve the plan
5. **Outputs the final plan** in a single, coherent voice

Claude remains the decision-maker throughout. Codex is the reviewer, not the author.

## Trigger conditions (any one is sufficient)

- Multi-step task with obvious dependencies
- Experiment design (variables, controls, metrics, ablations)
- Engineering implementation path or debug sequence
- Trade-off between multiple candidate approaches
- Task chain where an early mistake propagates downstream
- Research planning with stage milestones

## Dependencies

### Codex CLI

The Codex review step calls:

```powershell
$prompt | codex exec -C "F:\" -m "gpt-5.4" --sandbox danger-full-access --skip-git-repo-check -
```

Replace `-C "F:\"` with your working directory and `-m "gpt-5.4"` with your preferred model.

### Memory file (Obsidian integration — optional but recommended)

The skill reads context paths from a local memory file at:

```
~/.claude/projects/<project-slug>/memory/reference_obsidian_paths.md
```

This file maps your project memory layer (Obsidian vault, run cards, experiment indexes) to the paths Codex should read before reviewing. If you do not use Obsidian, replace this step with any structured context file listing relevant paths for your project.

See [`reference_obsidian_paths.md`](https://github.com/Xukai-YE/claude-memory/blob/main/reference_obsidian_paths.md) for the path schema used in this setup.

### effort-calibration (optional but recommended)

When this skill is active, [`effort-calibration`](https://github.com/Xukai-YE/effort-calibration) automatically locks the effort tier to at least `high`.

## Install

```
~/.claude/skills/plan-review-collaboration/SKILL.md
```

Add the mandatory trigger to your `CLAUDE.md` (global or project-level):

```markdown
Before producing any response that involves experiment design, research plan,
multi-step implementation path, ablation design, system architecture, or complex
engineering decision, invoke the `plan-review-collaboration` skill first.
```

## Codex fallback

If the Codex CLI is unavailable, Claude completes a high-quality plan and performs a self-review against the same six dimensions (missing steps, risks, unreasonable assumptions, executability, checkpoints, alternatives). The task is never abandoned.
