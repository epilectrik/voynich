# C1443: 17 Forbidden TERMINAL x Suffix-Head Pairs

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, suffix, forbidden, co-occurrence, exclusion, C1414, C1440, C1412
**Phase:** 522 (TWO_LEVEL_CLOSURE)
**Date:** 2026-03-05

## Claim

17 TERMINAL atom x suffix-head atom combinations show near-zero co-occurrence (O/E < 0.1). The e-suffix head is excluded by all non-h terminals (5 forbidden pairs). r-terminal excludes 5 suffix heads (e, h, y, r, s). l-terminal excludes 4 (e, h, y, i). h-terminal excludes 5 (y, r, l, i, g). Extends C1414 cross-slot exclusion rules to the full TERMINAL x suffix-head interaction space.

## Evidence

### Complete forbidden pair inventory

| # | Terminal | Suffix Head | O/E | Observed | Expected |
|---|----------|------------|-----|----------|----------|
| 1 | y | e | 0.046 | 1 | 21.7 |
| 2 | l | e | 0.033 | 4 | 121.5 |
| 3 | l | h | 0.000 | 0 | 33.0 |
| 4 | l | y | 0.000 | 0 | 26.2 |
| 5 | l | i | 0.000 | 0 | 5.6 |
| 6 | r | e | 0.000 | 0 | 108.0 |
| 7 | r | h | 0.000 | 0 | 29.3 |
| 8 | r | y | 0.000 | 0 | 23.3 |
| 9 | r | r | 0.000 | 0 | 16.4 |
| 10 | r | s | 0.069 | 1 | 14.6 |
| 11 | h | y | 0.000 | 0 | 77.0 |
| 12 | h | r | 0.037 | 2 | 54.2 |
| 13 | h | l | 0.085 | 2 | 23.5 |
| 14 | h | i | 0.000 | 0 | 16.4 |
| 15 | h | g | 0.000 | 0 | 2.2 |
| 16 | m | e | 0.000 | 0 | 3.4 |
| 17 | n | e | 0.000 | 0 | 5.1 |

### Pattern analysis

1. **e-suffix universally blocked by non-h terminals:** All 5 non-h terminals exclude e-suffix (y: 0.046x, l: 0.033x, r: 0, m: 0, n: 0). Only h-terminal permits e-suffix (O/E = 2.211x). This makes h the exclusive gateway for e-suffixed tokens.

2. **r-terminal has broadest exclusion:** 5 suffix heads blocked. r is the most restrictive SEMI-TRANSPARENT terminal.

3. **Self-exclusion included:** r-terminal excludes r-suffix (O/E = 0.000), extending the self-repulsion pattern (C1444).

### Complementary strong co-occurrences

8 pairs show O/E > 3.0: y+d(3.8x), y+r(3.0x), y+s(3.1x), y+l(8.4x), l+o(5.4x), r+o(3.5x), m+o(3.7x), n+y(8.2x). o-suffix is the universal attractor for l/r/m terminals.

## Interpretation

The TERMINAL x suffix-head interaction creates a structured selectivity landscape. Each terminal permits a characteristic subset of suffix heads and blocks others. The 17 forbidden pairs complement C1414's general cross-slot exclusion rules but operate specifically at the TERMINAL-suffix boundary, implementing the gating mechanism that C1412 identified at aggregate level.

## Falsification Criteria

1. If more than 3 of the 17 pairs exceed O/E = 0.3 under replication with different data subsets
2. If the e-exclusion pattern breaks (non-h terminal shows e-suffix O/E > 0.5)

## Method

- O/E ratios from 6 x 13 TERMINAL x suffix-head contingency table
- Expected counts from marginal products / grand total
- Threshold: O/E < 0.1 for forbidden, O/E > 3.0 for enriched
- Tokens: all suffixed Currier B tokens with identifiable terminal (N varies by terminal)

**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json` (T1, T6)

## Dependencies

- C1414 (cross-slot atom co-occurrence exclusion rules)
- C1412 (MIDDLE dominates suffix determination)
- C1440 (three-tier terminal opacity gradient)
