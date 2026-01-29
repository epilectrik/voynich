# C746: HT Folio Compensatory Distribution

**Tier:** 2
**Phase:** HT_RECONCILIATION
**Test:** T7
**Scope:** B

## Statement

HT density varies significantly across B folios (chi2=429.72, p=6.1e-49), ranging from 15.5% to 47.2% (global mean 30.5%, std 7.6%). HT density is negatively correlated with mean A-B coverage (r=-0.376, p=0.0005): folios with lower classified coverage have higher HT density.

## Evidence

### Density Statistics

| Metric | Value |
|--------|-------|
| Global mean | 30.5% |
| Std | 7.6% |
| Min | 15.5% (f75r) |
| Max | 47.2% (f26v) |
| Median | 30.2% |
| IQR | [24.0%, 36.9%] |

Chi-squared goodness-of-fit (uniform): 429.72, p = 6.1e-49 (n=82 folios).

### Correlations

| Factor | r | p |
|--------|---|---|
| Folio size (total tokens) | -0.110 | 0.324 |
| Classified vocab size | -0.101 | 0.367 |
| Mean A-B coverage | -0.376 | 0.0005 |

### Extreme Folios

**Lowest HT:** f75r (15.5%), f78v (17.5%), f81r (17.9%), f75v (19.2%), f40v (20.8%)
**Highest HT:** f95v1 (43.6%), f48r (43.8%), f57r (44.8%), f115v (46.1%), f26v (47.2%)

## Interpretation

The compensatory pattern (high HT where coverage is low) has two interpretations:

1. **Structural compensation:** HT tokens fill vocabulary gaps where the classified grammar has limited reach, providing material the 49-class system cannot supply.
2. **Tautological co-variation:** Folios with unusual vocabulary content have both (a) rare MIDDLEs not in A pools (low coverage) and (b) rare tokens not in the 479-type grammar (high HT). Both follow from vocabulary unusualness.

Interpretation 2 is more parsimonious. HT density is not independent of folio size or classified vocabulary (no significant correlation with either), but IS tied to the folio's degree of vocabulary novelty.

This is consistent with C450-C453 (HT global threading) and C507 (PP-HT substitution).

## Provenance

- Phase: HT_RECONCILIATION/results/ht_coverage_impact.json
- Script: ht_coverage_impact.py
- Related: C404-C405 (HT non-operational), C450-C453 (HT threading), C507 (PP-HT substitution), C734-C739 (A-B routing)
