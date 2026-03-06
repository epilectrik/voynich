# C1456: i-Modifier Suffix Depletion

**Tier:** 2
**Scope:** B, MIDDLE, atom, i-modifier, suffix, mode, n-terminal, C1383, C1408, C1451
**Phase:** 524 (I_MODIFIER_HAZARD)
**Date:** 2026-03-05

## Claim

i-modified MIDDLEs have 9.4% suffix rate (vs 52.1% non-i, ratio 0.18x) and are 95.7% Mode B (bare/continuation) vs 73.0% non-i. This near-categorical suffix exclusion results from i-tokens' n-terminal structure (ain, iin, aiin all end in n), which functions as a built-in terminal boundary that structurally preempts suffix attachment.

## Evidence

### Suffix rate comparison

| Metric | i-tokens | Non-i tokens | Ratio |
|--------|----------|-------------|-------|
| Has suffix | 9.4% | 52.1% | 0.18x |
| Mode A (specification) | 4.3% | 27.0% | 0.16x |
| Mode B (continuation) | 95.7% | 73.0% | 1.31x |

### Top suffixes when present

| Suffix | Count | Type |
|--------|-------|------|
| -r | 46 | Continuation |
| -hy | 34 | Terminal |
| -dy | 24 | Terminal |
| -y | 20 | Terminal |
| -s | 14 | Continuation |

### Structural explanation

90.5% of i-tokens are n-terminal (C1452). The n atom functions as a terminal boundary marker (C1383: n-terminal boundary avoidance). When n occupies the TERM slot, it creates a natural morphological boundary that resists suffix attachment. The 9.4% that do take suffixes are the non-n-terminal i-tokens (air, ait, airo, etc.).

## Interpretation

i-tokens' suffix depletion is a morphological consequence, not a functional choice. The n-terminal structure that characterizes the ain/iin/aiin family inherently resists suffixation. This connects i's suffix profile to the Mode B concentration (C1451): since Mode A requires terminal suffixes and i-tokens structurally resist suffixes, i-tokens are forced into Mode B. This is consistent with C1382 (a-initial enriched in Mode B) since i-tokens are 65.8% a-initial.

## Falsification Criteria

1. If i-token suffix rate exceeds 20%
2. If i-token Mode A fraction exceeds 15%
3. If n-terminal i-tokens show >5% suffix rate (currently ~1-2%)

## Method

- 2,052 i-modified tokens analyzed for suffix presence and suffix mode
- Mode A = terminal/specification suffixes (edy, ey, dy, y, hy, etc.)
- Mode B = bare or continuation suffixes (r, s, l, al, ar, am, etc.)
- Cross-referenced with TERM atom distribution

**Script:** `phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py`
**Results:** `phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json`

## Dependencies

- C1383 (n-terminal MIDDLE boundary avoidance)
- C1382 (k/a atom-initial suffix mode polarization)
- C1408 (suffix has HEAD->TERM compositional structure)
- C1451 (Mode B exclusive forbidden violation concentration)
