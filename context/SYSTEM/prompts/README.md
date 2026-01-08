# Voynich Project - Mode-Explicit Prompts

Use these templates to ensure Claude Code operates in the correct mode for your task.

## Why Modes Matter

This project uses a **structure-complete** context system. Without mode guidance:
- Claude may treat sparse documentation as "gaps" (false positives)
- Claude may propose research where none is needed
- Claude may audit when you want explanation

## Available Modes

| Mode | Use Case | Default |
|------|----------|---------|
| **ADMIN** | Links, labels, consistency fixes | Yes |
| **EXPLANATION** | Understanding existing content | No |
| **AUDIT** | Finding Tier 0/1 contradictions | Rare |

## How to Use

Copy the relevant template from the mode files and paste at the start of your request.

## Files

- `ADMIN_MODE.md` - Default for maintenance tasks
- `EXPLANATION_MODE.md` - For questions about the model
- `AUDIT_MODE.md` - For contradiction hunts (use rarely)
