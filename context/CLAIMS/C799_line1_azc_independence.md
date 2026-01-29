# C799: Line-1 AZC Independence

**Tier:** 2
**Scope:** B/HT
**Phase:** PP_HT_AZC_INTERACTION

## Constraint

Line-1 HT structure is independent of AZC mediation level. Neither the PP/B-exclusive ratio nor the A-context prediction accuracy varies significantly by AZC tertile. The line-1 header mechanism (C794-C795) operates uniformly regardless of AZC involvement.

## Evidence

### Line-1 PP Fraction by AZC Tertile

| AZC Tertile | Line-1 PP Fraction |
|-------------|-------------------|
| Low | 66.7% |
| Medium | 65.3% |
| High | 74.1% |

Kruskal-Wallis: H = 2.63, p = 0.27 (NOT significant)

### A-Context Prediction by AZC Tertile

| AZC Tertile | Correct | Total | Accuracy | Lift |
|-------------|---------|-------|----------|------|
| Low | 4 | 26 | 15.4% | 17.5x |
| Medium | 3 | 22 | 13.6% | 15.5x |
| High | 3 | 24 | 12.5% | 14.2x |

Chi-squared (low vs high): chi2 = 0.00, p = 1.00 (NOT significant)

### AZC as Additional Predictor

| Predictor Set | Correct | Total | Accuracy |
|---------------|---------|-------|----------|
| A-only MIDDLEs | 10 | 72 | 13.9% |
| A+AZC overlap | 7 | 68 | 10.3% |

Adding AZC does NOT improve prediction.

### Line-1 Elevation by Regime

The line-1 HT elevation (~24-25pp) is constant regardless of kernel or escape regime (p = 0.70).

## Interpretation

Line-1 operates as a **fixed header structure** independent of AZC context:

1. The two-part composition (PP for A-context, B-exclusive for folio ID) is consistent across all folios
2. A-context prediction works equally well regardless of AZC involvement
3. AZC-mediated vocabulary does not modulate line-1 behavior

This confirms C794-C795: Line-1 is a program header that declares A-context, not an AZC-modulated structure. The AZC layer affects body HT (C797-C798) but not the header.

## Dependencies

- C794 (Line-1 Composite Header Structure)
- C795 (Line-1 A-Context Prediction)
- C747 (Line-1 HT Enrichment)

## Provenance

```
phases/PP_HT_AZC_INTERACTION/scripts/t2_line1_azc_modulation.py
phases/PP_HT_AZC_INTERACTION/scripts/t3_regime_ht_patterns.py
```
