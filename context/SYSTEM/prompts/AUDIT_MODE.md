# AUDIT MODE Template

**Use rarely** - only when explicitly hunting for contradictions.

Copy this block at the start of your request:

```
AUDIT MODE.

Purpose: Identify Tier-0 or Tier-1 contradictions ONLY.

Rules:
- IGNORE Tier-2 density imbalances (not a problem)
- IGNORE Tier-3/4 unknowns (expected and closed)
- IGNORE "why" questions without answers (not gaps)
- DO NOT suggest reopening closed domains
- DO NOT treat sparse documentation as incomplete

This is a CONTRADICTION HUNT, not an expansion exercise.

Report only:
1. Direct Tier-0 contradictions (two frozen facts conflict)
2. Tier-1 violations (retrying falsified approach)
3. Administrative errors (broken links, wrong labels)
```

## When to Use

- After major refactoring
- When integrating new phases
- Periodic integrity checks (every ~10 sessions)

## What This Mode Prevents

- False positives from sparse documentation
- Treating all unknowns as gaps
- Proposing unnecessary research
- Over-scoping the audit
