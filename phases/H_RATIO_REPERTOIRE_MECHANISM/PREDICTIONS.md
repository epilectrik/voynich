# Phase 609: H_RATIO_REPERTOIRE_MECHANISM — Predictions

**Frozen before execution. Do not edit after SHA-256 is recorded.**

## Predictions

### P1 (T1 — Mechanism Tournament)
An MP-related model (M1: MP_present or M2: TQ_MP_exclusion) will capture the largest share of h_ratio residual among simple predictors (M1-M4), because MONITORING-Phase is the most exclusionary zone (C1761) and h_ratio is directly monitoring-related (C104, C1154). M5 (full repertoire_type) will improve only modestly over the best simple predictor (delta-R^2 of M5 minus best simple < 0.10).

### P2 (T2 — Continuous vs Discrete)
Continuous-Full (12 features across 3 tiers) will capture 60-80% of M5's delta-R^2. M5 will retain a modest advantage because combinatorial co-occurrence information is not fully captured by distributional summaries of individual paragraph scores. The gap between Continuous-Tier1 (means only) and Continuous-Full will be >= 0.05 delta-R^2, indicating within-folio heterogeneity matters beyond paragraph means.

### P3 (T3 — Section Dependence)
The repertoire-h_ratio effect will be strongest in Stars (delta-R^2 > 0.15, permutation p < 0.05) and weak/null in Herbal and Biologicals, consistent with C1154 (h is section-determined in BIO/HERBAL/COSMO but program-specific in Stars).

### P4 (T4 — MP Deep-Dive)
Folios with MP paragraphs will have higher h_ratio AND higher within-folio monitoring heterogeneity (thermal_monitoring_var), with both comparisons significant at p < 0.05 after section control. The number of MP paragraphs will not add predictive power beyond MP presence (binary is sufficient).

### P5 (T5 — Cross-Validation)
Model A (discrete) will have lower LOO RMSE than Model B-Tier1 (means only). The gap between Model A and Model B-Full will be smaller. Model C (both) will be marginally better than Model A alone, suggesting a small amount of complementary information.

## Verdict Tree

```
T1 MP/TQ_MP best simple AND T2 discrete > continuous (>30% margin)
  -> H_RATIO_BUNDLE_EFFECT

T1 entropy/mono_multi best simple AND T2 discrete > continuous (>30% margin)
  -> H_RATIO_NARROWNESS_EFFECT

T2 Continuous-Full within 30% of M5 AND Tier2/3 add substantially over Tier1
  -> H_RATIO_HETEROGENEITY_EFFECT

T2 Continuous-Tier1 alone matches M5
  -> H_RATIO_GRADIENT_EFFECT

T3 effect only in Stars
  -> append _STARS_SPECIFIC

All T1 candidates < 5% dR2 or fail permutation
  -> H_RATIO_MECHANISM_UNCLEAR
```
