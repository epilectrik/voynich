# C1331: Iterative Refinement Falsified

**Tier:** 1 (falsification)
**Scope:** B (all sections)
**Phase:** BLOCK_VOCABULARY_DRIFT (466)

## Constraint

Consecutive blocks on a folio do NOT show directional vocabulary drift consistent with iterative refinement. The prediction that blocks progressively converge toward a target state (k-kernel decreasing, e-kernel increasing, specification Mode A decreasing, FL material state advancing) is falsified: 1/4 predicted drift axes pass, and the passing axis (vocabulary narrowing, C1330) is consistent with alternative explanations.

## Evidence

From block_vocabulary_drift.py tests D1, D3, D4:

**D1: Kernel composition drift (k→e) — FAIL**

| Kernel | Median rho | Perm p | Predicted |
|--------|-----------|--------|-----------|
| k | +0.026 | 0.600 | <0 (decreasing) |
| h | -0.097 | 0.085 | — |
| e | +0.154 | 0.033 | >0 (increasing) |

e-kernel shows the predicted direction but fails significance threshold (p=0.033 > 0.01). k-kernel shows no trend. Combined FAIL.

**D3: Suffix Mode A shift — FAIL**

| Metric | Value |
|--------|-------|
| Median rho | -0.038 |
| Perm p | 0.199 |
| Direction | 29 negative, 27 positive |

No systematic Mode A decrease across block ordinals.

**D4: FL stage progression — FAIL**

| Metric | Value |
|--------|-------|
| Median rho | +0.021 |
| Perm p | 0.435 |
| Direction | 26 negative, 29 positive |

No systematic FL stage advancement. Mean FL index by ordinal shows no trend (range 2.54-2.85, no monotonic pattern).

**Section-specific signals (NOT pre-registered, sub-Bonferroni):**

| Section | D1 k_rho | D1 e_rho | D3 mode_rho | D4 fl_rho | Pattern |
|---------|---------|---------|-------------|-----------|---------|
| B | -0.286 | +0.310 | -0.429 | -0.500 | Partial refinement but FL reversed |
| C | -0.068 | +0.250 | -0.682 | +0.550 | Mixed |
| H | +0.450 | +0.375 | +0.350 | +0.350 | k/Mode A both INCREASE |
| S | +0.067 | +0.041 | +0.030 | +0.027 | Flat (operationally independent) |

Different sections show different drift patterns, but no section shows the full 4-axis refinement signature. Section H is consistently reversed on D1 and D3.

## What This Rules Out

1. **Blocks are NOT successive approximations to the same target.** Refinement predicts k↓, e↑, Mode A↓, FL↑ — only one weak sub-threshold signal (e↑ at p=0.033).
2. **The iterative refinement model proposed by the internal expert** (each block re-runs a similar procedure with slightly adjusted parameters) is falsified.
3. **C1326 (cross-block similarity)** is NOT explained by refinement convergence. Adjacent blocks are similar because they share REGIME context (C1325), not because they are converging toward a common target.

## What Remains

- C1330 (vocabulary narrowing) survives — later blocks have smaller vocabularies
- C1326 (cross-block similarity) survives — adjacent blocks share operational themes
- C1318 (PREFIX complementarity) survives — adjacent blocks do different PREFIX work
- The mechanism behind block similarity with vocabulary narrowing is an open question

## Provenance

- block_vocabulary_drift.json: tests D1, D3, D4
- Relates to: C1326 (cross-block continuity), C1325 (REGIME homogeneity), C1206 (paragraph kernel gradient), C777 (FL state index), C1229 (suffix modes)

## Status

FALSIFIED — iterative refinement is not the organizing principle for block sequences.
