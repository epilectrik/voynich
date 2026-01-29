# C679: Line Type Sequencing

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

Adjacent lines within folios are **weakly more similar** than random same-folio pairs. Mean cosine similarity: adjacent = 0.675, random = 0.641 (difference = +0.031). Permutation test p=0.000 (0/1000 shuffles matched or exceeded the observed adjacent similarity).

## Method

Since lines form a continuous distribution (C678, no discrete clusters), measure cosine similarity of 27-feature vectors. For each folio: compute cosine similarity of all adjacent line pairs. Random baseline: sample equal number of random within-folio pairs. Permutation test: shuffle feature vectors within folio 1000 times, recompute adjacent similarity.

## Key Numbers

| Metric | Value |
|--------|-------|
| Adjacent pairs | 2,322 |
| Mean adjacent cosine sim | 0.675 |
| Mean random cosine sim | 0.641 |
| Difference | +0.031 |
| Permuted mean | 0.646 |
| Permutation p | 0.000 |

## Interpretation

There is real but weak adjacent-line coupling. Consecutive lines share ~3% more profile similarity than random within-folio pairs. This is significant (p<0.001) but small in magnitude — lines are 95.4% as similar to random folio-mates as to their immediate neighbors. Combined with C670 (no vocabulary overlap) and C673 (no CC memory), this coupling operates at the aggregate feature level, not at the token or trigger level. Adjacent lines are drawn from similar but not identical parameter configurations.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_profile_classification.py` (Test 13)
- Extends: C678 (continuous distribution), C670 (no vocabulary coupling)
