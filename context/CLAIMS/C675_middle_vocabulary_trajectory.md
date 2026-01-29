# C675: MIDDLE Vocabulary Trajectory

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

MIDDLE frequency distributions are **nearly stable** across quartiles, with minimal progressive drift. JSD(Q1,Q4) = 0.081, only 7.8% above mean adjacent-quartile JSD (0.075). Of 135 frequent MIDDLEs (>=10 occurrences), only 4 (3.0%) show significant positional preference after Bonferroni correction.

## Method

Pool all MIDDLEs per quartile across 79 valid folios. Compute Jensen-Shannon divergence between all quartile pairs. Per-MIDDLE positional preference: KS test of each MIDDLE's norm_pos distribution against uniform, Bonferroni-corrected at alpha=0.000370.

## Key Numbers

| Metric | Value |
|--------|-------|
| Unique MIDDLEs | 1,320 |
| JSD(Q1,Q2) | 0.0798 |
| JSD(Q2,Q3) | 0.0726 |
| JSD(Q3,Q4) | 0.0738 |
| JSD(Q1,Q4) | 0.0813 |
| Progressive drift ratio | 1.078 |
| Frequent MIDDLEs tested | 135 |
| Significant positional MIDDLEs | 4/135 (3.0%) |

## Positionally-Biased MIDDLEs

| MIDDLE | n | Mean Position | Bias | KS p |
|--------|---|---------------|------|------|
| edy | 1742 | 0.463 | neutral | 3.4e-7 |
| ed | 368 | 0.426 | early | 2.5e-5 |
| t | 568 | 0.450 | early | 2.6e-5 |
| eey | 610 | 0.542 | neutral | 3.0e-4 |

## Interpretation

Token-level vocabulary is nearly position-invariant within folios, complementing C664's finding that class-level proportions are stationary. The 3% positional bias rate is close to the Bonferroni-corrected false discovery rate, suggesting even these 4 MIDDLEs may be marginal. The control system selects MIDDLEs without regard to folio position — specific token identity is orthogonal to the position-dependent effects observed in morphological structure (C676).

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_token_trajectory.py` (Test 6)
- Extends: C506.b (73% within-class MIDDLE heterogeneity), C664 (role profile trajectory stationary)
