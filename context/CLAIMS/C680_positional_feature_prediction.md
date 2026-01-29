# C680: Positional Feature Prediction

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

11 of 27 line features correlate significantly with folio position. 9 of 27 add prediction beyond REGIME identity. The strongest position-dependent feature is line_length_z (partial dR2=0.040, F=99.0, p<1e-16). Position explains an additional 0.2-4.0% of variance beyond what REGIME alone provides.

## Position-Correlated Features (Spearman)

| Feature | rho | p |
|---------|-----|---|
| line_length_z | -0.195 | 5.1e-22 |
| sfx_bare | +0.093 | 5.1e-6 |
| sfx_e_family | -0.091 | 8.6e-6 |
| pfx_qo | -0.088 | 1.6e-5 |
| AX | +0.083 | 4.8e-5 |
| sfx_ol | -0.071 | 5.4e-4 |
| pfx_other | +0.057 | 5.4e-3 |
| QO_frac | -0.055 | 6.8e-3 |
| sfx_y | -0.049 | 0.017 |
| pfx_da | -0.049 | 0.017 |
| pfx_ot | -0.047 | 0.023 |

## Partial R2 (Position Beyond REGIME)

| Feature | R2 REGIME | R2 Full | dR2 | p |
|---------|-----------|---------|-----|---|
| line_length_z | 0.001 | 0.041 | +0.040 | <1e-16 |
| sfx_bare | 0.006 | 0.013 | +0.008 | 1.8e-5 |
| sfx_e_family | 0.004 | 0.010 | +0.006 | 1.5e-4 |
| pfx_qo | 0.046 | 0.053 | +0.007 | 1.8e-5 |
| AX | 0.003 | 0.010 | +0.007 | 4.2e-5 |
| sfx_ol | 0.004 | 0.007 | +0.004 | 3.6e-3 |
| pfx_other | 0.016 | 0.019 | +0.003 | 5.7e-3 |
| pfx_ol | 0.005 | 0.006 | +0.002 | 0.031 |
| QO_frac | 0.008 | 0.010 | +0.002 | 0.026 |

## Interpretation

Position is a weak but real predictor of morphological features, independent of REGIME. The dominant signal is line length declining late (dR2=0.040). Most other position effects are small (dR2<0.01). This confirms C664-C669's finding: positional evolution operates through morphological channels (PREFIX/suffix selection, line length) while maintaining class-level stationarity. 16 of 27 features are NOT predicted by position — the majority of line variation is position-independent.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_profile_classification.py` (Test 14)
- Extends: C664-C669 (class proportions flat, mild convergence), C676 (morphological trajectory)
