# C737: A-Folio Cluster Structure

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

A folios cluster into approximately 6 groups by their B-coverage profiles. The mean pairwise correlation between A folio coverage vectors is 0.648 — moderately correlated but clearly not identical, indicating distinct A folio "types."

### Clustering Results (Ward's method, ANOVA on mean coverage)

| k | F-statistic | p-value | Cluster sizes |
|---|------------|---------|---------------|
| 2 | 0.20 | 0.658 | [85, 29] |
| 3 | 2.48 | 0.089 | [85, 10, 19] |
| 4 | 13.83 | <0.001 | [62, 23, 10, 19] |
| 5 | 12.04 | <0.001 | [62, 23, 10, 7, 12] |
| 6 | 19.90 | <0.001 | [62, 17, 6, 10, 7, 12] |

Best k=6 (highest F-statistic).

### Cluster Characteristics (k=6)

| Cluster | Members | Mean Coverage | Mean Pool Size |
|---------|---------|---------------|----------------|
| 1 (standard) | 62 | 0.2278 | 31.0 |
| 2 (high-coverage) | 17 | 0.3938 | 48.8 |
| 3 (low-coverage) | 6 | 0.1996 | 32.5 |
| 4 | 10 | 0.2169 | 33.9 |
| 5 | 7 | 0.2415 | 34.4 |
| 6 (medium-high) | 12 | 0.3257 | 41.0 |

### Specificity Ratio

| Metric | Value |
|--------|-------|
| Mean per-A variance across B folios | 0.003293 |
| Null (B-only) variance | 0.002133 |
| Specificity ratio | 1.544x |

The 1.544x ratio exceeds the 1.5x threshold for routing architecture. A folios are not interchangeable — they show differential reach across B folios beyond what B folio characteristics alone predict.

## Implication

The clustering is dominated by pool size (Cluster 2 = large pools, Cluster 1 = standard pools). But the non-trivial cluster structure at k=4-6 and moderate correlation (0.648) suggest that pool COMPOSITION also matters. Clusters 3-5 have similar pool sizes (~33) but different coverage means, indicating they contain different MIDDLEs that open different B vocabulary corridors.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/ab_specificity.py` (T3, T4)
- Depends: C734 (coverage architecture), C735 (pool size dominance)
