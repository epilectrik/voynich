# C1338: MIDDLE Suffix Selectivity

**Tier:** 2
**Scope:** B
**Phase:** SUFFIX_MODE_ASSIGNMENT (469)

## Constraint

MIDDLE identity is the primary determinant of suffix selection, carrying 11.57x more mutual information about suffix category than line mode does. I(MIDDLE; suffix_cat) = 0.697 bits vs I(line_mode; suffix_cat) = 0.060 bits. 60% of frequent MIDDLEs are suffix-locked (>80% one suffix category): 37.1% always bare, 22.9% always terminal.

## Evidence

From suffix_mode_assignment.py test S1 (70 MIDDLEs with 20+ occurrences, 16,004 tokens in classified body lines):

**Mutual information comparison:**

| Predictor | MI (bits) | Ratio |
|-----------|-----------|-------|
| MIDDLE identity | 0.697 | **11.57x** |
| Line mode (A/B) | 0.060 | 1.0x |

**Selectivity distribution (70 frequent MIDDLEs):**

| Band | Count | % |
|------|-------|---|
| Bare-locked (>80% bare) | 26 | 37.1% |
| Terminal-locked (>80% terminal) | 16 | 22.9% |
| Moderate (60-80%) | 12 | 17.1% |
| Low (<60%) | 16 | 22.9% |

Mean selectivity: 0.801, median: 0.889.

**Perfectly selective MIDDLEs (1.000):**
- Always terminal: eck (n=78), ect (n=43), kc (n=24)
- Always bare: eey (n=558), in (n=222), ey (n=727), edy (n=1545)

## Interpretation

Suffix assignment is a MIDDLE property, not a line property. Each MIDDLE has an intrinsic suffix preference that barely depends on what mode the line is classified as. The 11.57x MI ratio means that knowing which MIDDLE a token is tells you 11.6 times more about its suffix than knowing the line's mode. This is the foundation for mode being an emergent property (C1341).

The bare-locked MIDDLEs (eey, ey, edy, in) are the high-frequency backbone of the B grammar — edy alone (n=1545) accounts for ~8.7% of all body-line tokens. Their bare status is intrinsic, not contextually imposed.

## Provenance

- suffix_mode_assignment.json: test S1
- Extends: C1231 (universal suffix mode centroids), C1236 (suffix scope markers)
- Relates to: C1229 (alternating suffix modes), C1256 (opener mode selection V=0.30)

## Status

CONFIRMED — MIDDLE identity determines suffix category 11.57x more than line mode.
