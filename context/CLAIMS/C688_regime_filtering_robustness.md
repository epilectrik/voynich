# C688: REGIME Filtering Robustness

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

All four REGIMEs show similar robustness to A-record filtering. REGIME_2 is marginally the most robust (0.222 effective-to-baseline ratio), REGIME_3 the least (0.167). The effective instruction budget — classes that survive filtering AND actually appear in the REGIME's folios — is tightly clustered around 21-22% of baseline across REGIMEs 1, 2, and 4.

## Key Numbers

| REGIME | Mean Effective Classes | Median | Baseline | Robustness Ratio |
|--------|----------------------|--------|----------|-----------------|
| REGIME_1 | 10.19 | 10.0 | 48 | 0.212 |
| REGIME_2 | 10.64 | 10.0 | 48 | 0.222 |
| REGIME_3 | 7.85 | 7.0 | 47 | 0.167 |
| REGIME_4 | 10.49 | 10.0 | 48 | 0.219 |

## Interpretation

REGIME_3's lower robustness reflects its smaller token vocabulary (739 types vs 2,000+ for other REGIMEs). With fewer tokens per class, there are fewer chances for a surviving token to land in the REGIME's inventory. The near-equality of REGIMEs 1, 2, and 4 suggests filtering severity is A-record-driven, not REGIME-driven.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/structural_reshape_analysis.py` (Test 7)
- Extends: C682 (filtering profile), C664-C669 (REGIME class stationarity)
