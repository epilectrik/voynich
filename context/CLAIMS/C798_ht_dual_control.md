# C798: HT Dual Control Architecture

**Tier:** 2
**Scope:** GLOBAL/HT
**Phase:** PP_HT_AZC_INTERACTION

## Constraint

HT density is controlled by two orthogonal factors:
1. **AZC mediation** (negative): High AZC → less HT (rho = -0.352)
2. **Escape activity** (positive): High FL → more HT (rho = 0.377)

These factors are independent (AZC-FL correlation = -0.023, NS) and additive.

## Evidence

### Orthogonality

| Correlation | rho | p-value |
|-------------|-----|---------|
| AZC% ↔ FL% | -0.023 | 0.84 |
| AZC% → HT% | -0.352 | 0.0012 |
| FL% → HT% | +0.377 | 0.0005 |

AZC and FL are orthogonal (uncorrelated). Each has an independent effect on HT.

### Quadrant Analysis

| AZC Level | FL Level | Mean HT% | n |
|-----------|----------|----------|---|
| Low | Low | 31.4% | 21 |
| Low | High | 37.0% | 20 |
| High | Low | 25.2% | 20 |
| High | High | 30.2% | 21 |

Effects are additive:
- High FL adds ~5.5pp HT vs Low FL
- Low AZC adds ~6.0pp HT vs High AZC
- Combined effect matches prediction: 37.0% ≈ 25.2% + 5.5 + 6.0

### Partial Correlations Confirm Independence

| Controlling | AZC→HT rho | FL→HT rho |
|-------------|------------|-----------|
| Nothing | -0.352 | +0.377 |
| FL% | -0.384 | — |
| AZC% | — | +0.404 |

Both effects STRENGTHEN when controlling for the other, confirming orthogonality.

## Interpretation

HT density encodes two independent pieces of information:

1. **Vocabulary provenance** (AZC axis):
   - High AZC-mediation = vocabulary pre-filtered by AZC legality
   - Less HT needed because context is provided by vocabulary source

2. **Operational intensity** (FL axis):
   - High escape rate = complex execution with many recovery events
   - More HT needed to signal escape-heavy operational context

This dual control architecture explains why HT is not simply "padding" but carries structured information about both vocabulary source and execution complexity.

## Dependencies

- C796 (HT-Escape Correlation)
- C797 (AZC-HT Inverse Relationship)
- C765 (AZC Kernel Access Bottleneck)
- C746 (HT Folio Compensatory Distribution)

## Provenance

```
phases/PP_HT_AZC_INTERACTION/scripts/t4_escape_ht_mechanism.py
```
