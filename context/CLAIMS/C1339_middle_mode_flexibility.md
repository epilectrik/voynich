# C1339: MIDDLE Mode Flexibility

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_ASSIGNMENT (469)

## Constraint

Only 7.7% of frequent MIDDLEs are mode-locked (appearing >80% in one mode). Most MIDDLEs are mode-flexible: 34.6% split evenly between modes (40-60%), 57.6% lean one direction but not strongly. This means MIDDLEs freely appear in both Mode A and Mode B lines — mode is not a MIDDLE selection filter.

## Evidence

From suffix_mode_assignment.py test S2 (104 MIDDLEs with 10+ occurrences):

**Mode preference distribution:**

| Band | Count | % |
|------|-------|---|
| Mode-locked A (>80% Mode A) | 2 | 1.9% |
| Mode-locked B (<20% Mode A) | 6 | 5.8% |
| Leaning A (60-80%) | 17 | 16.3% |
| Leaning B (20-40%) | 43 | 41.3% |
| Flexible (40-60%) | 36 | 34.6% |

**Category × mode preference (mean mode_A_fraction):**

| Category | Mean mode_A_frac | Direction | n |
|----------|-----------------|-----------|---|
| MONITORING | 0.586 | Mode A | 8 |
| FLOW | 0.485 | ~neutral | 18 |
| MARKING | 0.477 | ~neutral | 13 |
| OPERATION | 0.465 | ~neutral | 11 |
| THERMAL | 0.406 | Mode B | 17 |
| CONTAINMENT | 0.397 | Mode B | 8 |
| STAGING | 0.393 | Mode B | 12 |
| TRANSITION | 0.328 | Mode B | 14 |

## Interpretation

The S2 result falsifies the "mode-locked vocabulary" model: MIDDLEs are NOT assigned to modes. The same MIDDLE can appear on a Mode A line or a Mode B line with nearly equal probability. What makes the line Mode A or Mode B is the SUFFIX each token carries (C1338), not which MIDDLEs are present.

The category→mode lean matches C1279/C1309 directionally (MONITORING→A, TRANSITION→B) but the effect is weak. THERMAL MIDDLEs actually lean Mode B (0.406), even though Mode A lines are THERMAL-enriched (C1279: 1.45x). This apparent paradox resolves because THERMAL MIDDLEs carry terminal suffixes more often than average — when they do, they boost Mode A; when they don't, they appear bare in Mode B. The enrichment is about suffix behavior, not token selection.

## Provenance

- suffix_mode_assignment.json: test S2
- Relates to: C1279 (mode category differentiation), C1309 (mode category specialization)
- Extends: C1267 (mode distinction is B-execution only — now explained: mode is emergent from suffix assignment)

## Status

CONFIRMED — MIDDLEs are mode-flexible (92.3%), not mode-locked. Mode is not a token filter.
