---
name: phase-analysis
description: Analyzes completed research phases, extracts findings, validates against the frozen model (411 constraints), and documents new constraints. Use when analyzing phase results, validating findings, or integrating new research into the constraint system.
allowed-tools: Read, Glob, Grep, Write, Edit
---

# Phase Analysis Skill

When analyzing a completed research phase, follow this protocol:

## Step 1: Load Context

Read these files first:
- `context/CORE/frozen_conclusion.md` - Tier 0 facts (never contradict)
- `context/CLAIMS/INDEX.md` - All 411 constraints for reference

## Step 2: Examine Phase Output

Read the phase directory: `phases/<PHASE_NAME>/`

Extract:
- Key metrics (percentages, counts, p-values)
- Claims being made
- Evidence provided
- Statistical tests used

## Step 3: Validate Against Existing Constraints

For each finding:

1. Search `context/CLAIMS/` for related constraints
2. Check if finding CONFIRMS, EXTENDS, or CONTRADICTS existing work
3. If contradicts Tier 0-1: Flag as potential analysis error
4. If confirms Tier 2: Note as supporting evidence

## Step 4: Classify and Document

| Finding Type | Tier | Action |
|--------------|------|--------|
| Proven by internal structure | 0 | Add to CORE/ (rare) |
| Falsifies hypothesis | 1 | Add to falsifications.md |
| High-confidence structural | 2 | Propose new constraint |
| Interpretive alignment | 3 | Add to SPECULATIVE/ |
| Idea generation | 4 | Add to exploratory.md |

## Step 5: Output Format

```markdown
## Phase Analysis: [PHASE_NAME]

### Summary
[2-3 sentence summary of phase purpose and outcome]

### Key Findings
1. [Finding with evidence]
2. [Finding with evidence]

### Constraint Implications

**New Constraints Proposed:**
- C412: [Statement] (Tier X, Phase PHASE_NAME)

**Existing Constraints Confirmed:**
- C### - [additional evidence from this phase]

**Contradictions Detected:**
- [If any - flag for review]

### Files to Update
- context/CLAIMS/INDEX.md - add C412
- context/CLAIMS/[appropriate_file].md - add details
- context/MAPS/claim_to_phase.md - add mapping
```

## Reference Locations

| Need | Location |
|------|----------|
| Tier definitions | context/SYSTEM/TIERS.md |
| Stop conditions | context/SYSTEM/STOP_CONDITIONS.md |
| Falsified claims | context/CORE/falsifications.md |
| Constraint format | context/CLAIMS/ (see existing files) |
