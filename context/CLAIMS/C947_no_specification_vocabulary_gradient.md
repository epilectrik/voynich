# C947: No Specification Vocabulary Gradient

**Tier:** 1 | **Status:** CLOSED (FALSIFIED) | **Scope:** B | **Source:** MATERIAL_LOCUS_SEARCH

## Statement

The hypothesis that early-paragraph vocabulary is more section-discriminative than late-paragraph vocabulary (a "specification gradient" where materials are named early) is **rejected**. Best early-body classification accuracy (62.5%) does not exceed best late-body accuracy (64.2%), yielding a difference of -1.7 percentage points (threshold: >10pp). Cramer's V comparison shows no significant difference (paired Wilcoxon p=0.632). Section discrimination is equally distributed across paragraph positions.

## Evidence

### Classification Accuracy

| Partition | KNN (k=5) | NearestCentroid | Best |
|-----------|-----------|-----------------|------|
| EARLY (first 33%) | 62.5% | 61.2% | 62.5% |
| LATE (last 33%) | 64.2% | 59.1% | 64.2% |

Difference: -1.7pp (wrong direction)

### Cramer's V Comparison (76 shared MIDDLEs)

| Metric | EARLY | LATE |
|--------|-------|------|
| Mean V | 0.166 | 0.167 |
| Higher V count | 36 | 40 |
| Wilcoxon p | 0.632 | |

### Permutation Test

Observed difference -0.017, permutation mean +0.001, z=-0.56, p=0.72

## What This Rules Out

If materials were specified at paragraph start (analogous to "take rosemary and..." in Brunschwig), early vocabulary would be strongly section-distinctive. The null result means either materials are not specified positionally, or section identity pervades the entire paragraph equally.

## Related

C941, C827, C855, C942
