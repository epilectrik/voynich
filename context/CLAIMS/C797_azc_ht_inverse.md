# C797: AZC-HT Inverse Relationship

**Tier:** 2
**Scope:** A<>B/HT
**Phase:** PP_HT_AZC_INTERACTION

## Constraint

AZC mediation level inversely correlates with HT density: rho = -0.352, p = 0.0012. Folios with higher AZC-mediated vocabulary have lower HT density. This effect is independent of escape activity.

## Evidence

### Direct Correlation

| Metric | Value |
|--------|-------|
| Spearman rho (AZC% vs HT%) | -0.352 |
| p-value | 0.0012 |
| Effect | High AZC → less HT |

### Tertile Analysis

| AZC Tertile | Mean AZC% | Mean HT% |
|-------------|-----------|----------|
| Low | 63.7% | 34.9% |
| Medium | 75.0% | 29.7% |
| High | 86.9% | 28.4% |

High-Low difference: -6.5 percentage points

### Independence from FL

- AZC% → FL%: rho = -0.023, p = 0.84 (NOT significant)
- Partial correlation (AZC% vs HT%, controlling FL%): rho = -0.384, p = 0.0004

AZC and FL are orthogonal predictors of HT density.

### Confound Analysis

Partial correlation controlling for vocabulary size: rho = -0.125, p = 0.26 (NOT significant)

The raw AZC-HT correlation is partially confounded by vocabulary size: larger vocabularies have both less AZC mediation and less HT (per token).

## Interpretation

AZC-mediated vocabulary "displaces" HT. When a folio draws heavily from the AZC-filtered vocabulary pool, less HT padding is needed. This may reflect:
- AZC vocabulary is pre-filtered for legality, reducing ambiguity
- Simpler execution paths (C765) require less signaling
- AZC provides sufficient context, reducing HT's indexing function

## Dependencies

- C765 (AZC Kernel Access Bottleneck)
- C746 (HT Folio Compensatory Distribution)
- C796 (HT-Escape Correlation)

## Provenance

```
phases/PP_HT_AZC_INTERACTION/scripts/t1_azc_ht_baseline.py
phases/PP_HT_AZC_INTERACTION/scripts/t4_escape_ht_mechanism.py
```
