# C796: HT-Escape Correlation

**Tier:** 2
**Scope:** B/HT
**Phase:** PP_HT_AZC_INTERACTION

## Constraint

HT density correlates positively with escape rate (FL token frequency): rho = 0.377, p = 0.0005. Folios with more escape operations have proportionally more HT tokens. This relationship is independent of AZC mediation.

## Evidence

### Direct Correlation

| Metric | Value |
|--------|-------|
| Spearman rho (HT% vs FL%) | 0.377 |
| p-value | 0.0005 |
| Effect | High escape → more HT |

### Tertile Analysis

| Escape Tertile | Mean FL% | Mean HT% |
|----------------|----------|----------|
| Low | 3.8% | 27.4% |
| Medium | 6.7% | 30.8% |
| High | 10.8% | 34.6% |

Kruskal-Wallis: H = 12.63, p = 0.0018

### Independence from AZC

Partial correlation (HT% vs FL%, controlling AZC%): rho = 0.404, p = 0.0002

The HT-FL relationship is STRONGER after controlling for AZC, confirming independence.

## Interpretation

HT tokens track **escape activity**, not vocabulary gaps. Folios that require more recovery operations (high FL rate) have proportionally more HT tokens. This suggests HT is signaling operational intensity - specifically, the need for escape/recovery cycles.

## Dependencies

- C746 (HT Folio Compensatory Distribution)
- C765 (AZC Kernel Access Bottleneck)
- C582 (FL Definitive Census)

## Provenance

```
phases/PP_HT_AZC_INTERACTION/scripts/t3_regime_ht_patterns.py
phases/PP_HT_AZC_INTERACTION/scripts/t4_escape_ht_mechanism.py
```
