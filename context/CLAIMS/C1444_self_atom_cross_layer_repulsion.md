# C1444: Self-Atom Cross-Layer Repulsion

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, suffix, self-repulsion, cross-layer, C1409, C1414, C1440
**Phase:** 522 (TWO_LEVEL_CLOSURE)
**Date:** 2026-03-05

## Claim

Three of six testable atoms actively avoid repeating themselves across the MIDDLE terminal -> suffix head boundary: y (O/E=0.028, Fisher p=0.0), n (O/E=0.000, Fisher p=0.0), r (O/E=0.486, Fisher p=0.0). l shows weak avoidance (O/E=0.621, p=0.0). h and m are neutral. The same character in MIDDLE terminal and suffix head encodes DIFFERENT information (C1409), and the grammar actively prevents redundant repetition for the most opaque terminals.

## Evidence

### Self-co-occurrence rates

| Atom | N TERM tokens | N with self in suffix | Observed rate | Expected rate | O/E | Fisher p | Direction |
|------|-------------|----------------------|---------------|---------------|-----|----------|-----------|
| y | 4,780 | 33 | 0.69% | 25.0% | 0.028 | 0.0 | SELF_REPEL |
| n | 2,147 | 0 | 0.00% | 8.04% | 0.000 | 0.0 | SELF_REPEL |
| r | 1,962 | 71 | 3.62% | 7.45% | 0.486 | 0.0 | SELF_REPEL |
| l | 2,568 | 85 | 3.31% | 5.33% | 0.621 | 0.0 | NEUTRAL (weak) |
| h | 1,284 | 40 | 3.12% | 3.70% | 0.843 | 0.286 | NEUTRAL |
| m | 289 | 4 | 1.38% | 1.32% | 1.048 | 0.795 | NEUTRAL |

### Interpretation by tier

- **OPAQUE terminals (y, m, n):** y and n show extreme self-repulsion (O/E < 0.03). m is neutral but its overall suffix rate is so low (4.15%) that self-co-occurrence is already near-impossible. The repulsion is strongest exactly where suffix attachment is rarest.

- **SEMI-TRANSPARENT terminals (l, r):** r shows genuine self-repulsion (O/E = 0.486). l shows weak avoidance (0.621) but does not reach full statistical significance at the usual thresholds.

- **TRANSPARENT terminal (h):** Neutral (O/E = 0.843, p = 0.286). h-terminal freely co-occurs with h-suffix.

### Alignment with C1409

C1409 established that suffix atoms diverge from MIDDLE-terminal atoms (JSD 0.004-0.560). Self-repulsion extends this: not only do they carry different information, but the grammar actively blocks the same atom from appearing at both the MIDDLE terminal and suffix head positions in the same token.

## Falsification Criteria

1. If y or n self-co-occurrence O/E exceeds 0.3 under replication
2. If the pattern reverses (self-attraction for OPAQUE terminals)

## Method

- For each terminal atom X: count tokens where MIDDLE ends in X AND suffix starts with X
- Expected rate: overall rate of X as suffix-head across all suffixed tokens
- Fisher exact test for significance
- Direction: SELF_REPEL if O/E < 0.5 and p < 0.01; NEUTRAL otherwise

**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json` (T3)

## Dependencies

- C1409 (suffix atoms diverge from MIDDLE-terminal atoms)
- C1414 (cross-slot atom co-occurrence exclusion rules)
- C1440 (three-tier terminal opacity gradient)
