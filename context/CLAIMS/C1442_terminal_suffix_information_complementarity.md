# C1442: TERMINAL-Suffix Category Information Complementarity

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, suffix, information, complementarity, mutual-information, category, C1412, C1440, C1408
**Phase:** 522 (TWO_LEVEL_CLOSURE)
**Date:** 2026-03-05

## Claim

TERMINAL atom carries 1.261 bits of category mutual information vs suffix-head 0.347 bits (3.6x ratio). Joint MI = 1.252 bits; sum of individuals = 1.363 bits; redundancy = 0.112 bits (8.2%). The two layers encode nearly entirely different category information (COMPLEMENTARY verdict). The 3.2-3.5x layer ratio is stable across all five line-position quintiles, confirming position-invariant architecture.

## Evidence

### Information quantities

| Metric | Bits | N tokens |
|--------|------|----------|
| I(category; TERMINAL) all tokens | 1.261 | 16,925 |
| I(category; suffix_head) suffixed only | 0.347 | 10,861 |
| I(category; TERMINAL) suffixed only | 1.016 | 10,861 |
| I(category; TERMINAL + suffix_head) jointly | 1.252 | 6,020 |
| H(category) | 2.750 | -- |

### Redundancy computation

Sum of individual MIs (suffixed tokens): 1.016 + 0.347 = 1.363 bits
Joint MI: 1.252 bits
Redundancy: 1.363 - 1.252 = 0.112 bits = **8.2%** of sum

### Functional partitioning

88.5% of 78 TERMINAL x suffix-head pairs (69/78) have different top operational categories. All 6 self-pairs (y/y, l/l, r/r, h/h, m/m, n/n) are complementary. Example: y-terminal top = OPERATION, y-suffix top = THERMAL.

### Position invariance

| Quintile | MI(TERMINAL) | MI(suffix) | Ratio |
|----------|-------------|-----------|-------|
| Q0 | 1.237 | 0.358 | 3.46x |
| Q1 | 1.223 | 0.360 | 3.40x |
| Q2 | 1.287 | 0.369 | 3.49x |
| Q3 | 1.272 | 0.398 | 3.20x |
| Q4 | 1.317 | 0.372 | 3.54x |

The layer ratio remains between 3.2-3.5x at every position. Neither layer gains or loses dominance across the line.

## Interpretation

MIDDLE terminal and suffix encode complementary operational information. The terminal atom specifies the primary operational domain (with 3.6x more resolving power), while the suffix provides supplementary specification that is almost entirely non-redundant. The position invariance means this architecture is structural, not an artifact of line-position-specific vocabulary.

## Falsification Criteria

1. If redundancy fraction exceeds 25%
2. If layer ratio reverses (suffix carries more MI than terminal)
3. If layer ratio varies by >2x across line positions

## Method

- Mutual information I(X;Y) computed from joint frequency tables
- TERMINAL = last atom of MIDDLE; suffix_head = first atom of suffix
- Category assigned via atom plurality vote (CategoryClassifier)
- Redundancy = sum(individual MIs) - joint MI
- Position quintiles: 5 equal-count bins by normalized within-line position

**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json` (T7, T8)

## Dependencies

- C1412 (MIDDLE dominates suffix determination)
- C1440 (three-tier terminal opacity gradient)
- C1408 (suffix compositional structure)
- C1409 (suffix atoms diverge from MIDDLE-terminal atoms)
