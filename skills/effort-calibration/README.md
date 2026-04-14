# effort-calibration

A passive background skill for Claude Code that automatically selects an effort level (low / medium / high / max) before answering, and adjusts analysis depth, check intensity, and output structure accordingly.

## What it does

Before responding to any task, this skill internally classifies the request along 8 dimensions (multi-step reasoning, dependency chains, information gaps, user premise validity, error cost, trade-off requirements, cross-module coordination, and need for verification). It then selects one of four effort tiers and calibrates behavior accordingly — without exposing the dispatch mechanism to the user.

| Tier | When | Behavior |
|------|------|----------|
| `low` | Clear, stable, low-stakes tasks | Fast, direct, no unnecessary expansion |
| `medium` | Moderate analysis, clear boundaries | Clear logic and actionable recommendations |
| `high` | Multi-step dependencies, significant error cost | Systematic breakdown, assumptions, risks, fallbacks |
| `max` | High-risk, long-chain, multi-module critical decisions | Deepest scrutiny; compares candidates; checks all premises |

## Key rules

- Never judge tier by message length — judge by complexity, risk, and uncertainty
- Plans / experiments / architecture / critical decisions default to at minimum `medium`
- Explicit user requests for rigor automatically bump tier up by one
- When `plan-review-collaboration` skill is active, tier is locked to at least `high`
- Simple, unambiguous tasks are never over-escalated

## Install

Drop `SKILL.md` into your Claude Code skills directory:

```
~/.claude/skills/effort-calibration/SKILL.md
```

This skill is always active and requires no explicit invocation.
