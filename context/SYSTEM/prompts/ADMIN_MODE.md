# ADMIN MODE Template

Copy this block at the start of your request:

```
ADMIN MODE ONLY.

Task: [describe your task here]

Constraints:
- DO NOT search for new structure
- DO NOT propose research directions
- DO NOT treat Tier-3/4 unknowns as gaps
- Assume STOP CONDITIONS are valid and enforced
- Assume all Tier-0 and Tier-1 claims are closed

Return only:
1. Mechanical issues found
2. Wording clarifications needed
```

## When to Use

- Fixing broken links
- Correcting typos or labels
- Checking file consistency
- Updating references
- Any maintenance task

## What This Mode Prevents

- Spawning exploration agents unnecessarily
- Treating sparse documentation as incomplete
- Proposing new research directions
- Reopening settled questions
