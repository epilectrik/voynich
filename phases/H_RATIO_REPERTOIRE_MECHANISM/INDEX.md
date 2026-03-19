# Phase 609: H_RATIO_REPERTOIRE_MECHANISM

**Status:** COMPLETE
**Verdict:** H_RATIO_GRADIENT_EFFECT
**Constraints:** C1764-C1767
**Script:** `scripts/h_ratio_mechanism.py` (runtime ~45s)
**PREDICTIONS.md SHA-256:** `d194e1a93d6c4ae08d46b6837ae658119e8989b477580bd5fd0af43c2832d7bd`

## Motivation

Phase 608 (C1763) found that repertoire type explains 31.9% additional variance in h_ratio beyond PREFIX + section + paragraph_count (perm p=0.001). This was the only feature (of 5) surviving full controls. This phase asks: is this a genuine paragraph-combination-level effect, or an artifact of discretizing continuous paragraph gradients into hard zone labels?

## Results Summary

### T1: Mechanism Tournament (5 Models vs Baseline A)

| Model | Family | dR^2 | F | F_p | perm_p | Sig |
|-------|--------|------|---|-----|--------|-----|
| **M1 MP_present** | **Presence** | **0.083** | **8.217** | **0.006** | **0.018** | **YES** |
| M2 TQ_MP_excl | Presence | 0.040 | 3.679 | 0.059 | 0.089 | no |
| M3 mono/multi | Breadth | 0.011 | 0.952 | 0.333 | 0.262 | no |
| M4 rep_entropy | Breadth | 0.007 | 0.591 | 0.445 | 0.404 | no |
| **M5 full_rep** | **Full** | **0.241** | **3.451** | **0.002** | **0.004** | **YES** |

Baseline A R^2 = 0.208 (PREFIX + section + parcount).

**Best simple predictor:** M1 (MP_present, Presence family, dR^2=0.083).
**Best overall:** M5 (dR^2=0.241), but uses 8 dummies vs M1's 1 parameter.
**M5 improvement over M1:** 0.158 dR^2 -- the full combinatorial signature adds substantially beyond simple MP presence.

**Baseline B sensitivity check:** Baseline B adds k_ratio + e_ratio (kernel ecology), reaching R^2=0.969. Adding M1: dR^2=0.0003 (null). Adding M5: dR^2=0.0022 (null). **The entire repertoire effect is absorbed by kernel ecology.** This is expected algebraically: h_ratio = h/(k+h+e), so k_ratio and e_ratio nearly determine h_ratio. The repertoire effect from C1763 is a proxy for kernel ecology that PREFIX alone doesn't capture.

### T2: Continuous vs Discrete Representation

| Representation | dR^2 | F | p | Features |
|---------------|------|---|---|----------|
| Continuous-Tier1 (means) | **0.536** | 47.48 | <0.0001 | 3 |
| Continuous-Tier2 (+spread) | 0.540 | 23.16 | <0.0001 | 6 |
| Continuous-Full (+shape) | 0.558 | 11.75 | <0.0001 | 12 |
| Discrete M5 (zone labels) | 0.241 | 3.45 | 0.0023 | 8 dummies |

**Continuous-Tier1 captures 222% of M5's dR^2 using just 3 features (paragraph means of THERMAL score, MONITORING score, h_kernel_frac).**

Tier 2+3 add only 0.022 over Tier 1 -- within-folio heterogeneity and distributional shape add almost nothing. The effect is about paragraph-level means, not within-folio diversity.

Relative margin: -131% (continuous dominates discrete). **Verdict trigger: Continuous-Tier1 alone exceeds M5 --> GRADIENT_EFFECT.**

### T3: Section-Dependent Analysis

| Section | n | Best simple model | dR^2 | perm_p | Sig |
|---------|---|-------------------|------|--------|-----|
| **Stars** | **23** | **M1 MP_present** | **0.276** | **0.018** | **YES** |
| Biologicals | 20 | M1 MP_present | 0.150 | 0.083 | marginal |
| Herbal | 31 | M3 mono/multi | 0.134 | 0.063 | marginal |

Stars is the only section where a simple repertoire property significantly predicts h_ratio (perm_p<0.05). This is consistent with C1154: h is section-determined in BIO/HERBAL/COSMO but program-specific in Stars.

Herbal shows a different mechanism -- breadth (mono/multi) rather than specific zone presence. In Herbal, having diverse paragraph types predicts different h_ratio, while in Stars, what matters is whether MONITORING-Phase paragraphs are present.

### T4: MP Zone Deep-Dive

| Feature | MP-present median | MP-absent median | MW p | Section-ctrl p |
|---------|-------------------|------------------|------|----------------|
| h_ratio | 0.216 | 0.136 | 0.003 | 0.021 |
| monitoring_mean | 0.094 | 0.060 | 0.0001 | 0.0002 |
| h_kernel_mean | 0.098 | 0.056 | <0.0001 | <0.0001 |
| thermal_monitoring_var | 0.0065 | 0.0013 | 0.0002 | 0.032 |

All differences survive section control. Folios with MONITORING-Phase paragraphs have higher monitoring content, higher h_kernel content, and greater within-folio monitoring heterogeneity.

Within MP-present folios, the number of MP paragraphs does not predict h_ratio beyond presence (rho=0.380, p=0.108). Binary presence is sufficient.

### T5: Leave-One-Out Cross-Validation

| Model | RMSE | R^2_cv | In-sample R^2 | Overfit gap |
|-------|------|--------|---------------|-------------|
| D (baseline) | 0.0583 | -0.046 | 0.208 | 0.254 |
| A (discrete) | 0.0537 | 0.111 | 0.481 | 0.370 |
| **B-Tier1 (cont means)** | **0.0323** | **0.679** | 0.744 | 0.065 |
| B-Full (cont all) | 0.0346 | 0.632 | 0.806 | 0.174 |
| C (both) | 0.0380 | 0.556 | - | - |

**Out-of-sample, continuous paragraph means (3 features) predict h_ratio with R^2_cv=0.679, vs discrete zone labels R^2_cv=0.111.** Continuous means are both more accurate and less prone to overfitting.

Adding distributional features (B-Full) HURTS prediction (R^2_cv drops 0.679 to 0.632). Adding discrete labels to continuous (Model C) also HURTS (0.679 to 0.556). Simpler is better: three paragraph means are optimal.

The discrete model massively overfits (0.370 gap vs 0.065 for B-Tier1). With n=80, 8 dummy variables simply memorize noise.

## Prediction Outcomes

| # | Prediction | Outcome |
|---|-----------|---------|
| P1 | MP-related model captures most of h_ratio residual among simple predictors | **PASS** (M1 dR^2=0.083, perm_p=0.018) |
| P2 | Continuous-Full captures 60-80% of M5, Tier2+3 add >=0.05 | **FAIL** (captures 231%; Tier2+3 add only 0.022) |
| P3 | Stars strongest, weak/null in H and B | **PARTIAL** (Stars significant, B/H marginal not null) |
| P4 | MP folios have higher h_ratio + heterogeneity; count doesn't add to presence | **PASS** |
| P5 | A (discrete) lower RMSE than B-Tier1 | **FAIL** (B-Tier1 dramatically lower: 0.032 vs 0.054) |

2/5 pass, 1 partial. Key surprise: continuous paragraph means don't just match the discrete representation -- they utterly dominate it, both in-sample and out-of-sample.

## Findings

### F1: The C1763 repertoire effect is a continuous gradient, not a combinatorial bundle
Continuous paragraph means (THERMAL, MONITORING, h_kernel fractions, 3 features) explain 53.6% additional variance in h_ratio beyond PREFIX + section + parcount, compared to 24.1% for discrete zone labels (8 dummies). LOO cross-validation confirms: R^2_cv = 0.679 (continuous) vs 0.111 (discrete). The "repertoire independently predicts h_ratio" finding from C1763 is real, but the information is in paragraph-level monitoring gradients, not in which zone type combinations appear together.

### F2: Kernel ecology fully absorbs the repertoire effect
Baseline B (adding k_ratio + e_ratio to Baseline A) reaches R^2=0.969. Adding any repertoire property to Baseline B yields dR^2 < 0.003 (null). This means h_ratio variation is almost entirely determined by kernel ecology, which PREFIX alone captures poorly. Paragraph-level continuous scores are better proxies for kernel ecology than PREFIX fractions.

### F3: Stars is the only section with a significant specific-zone effect
M1 (MP_present) explains 27.6% additional h_ratio variance in Stars (perm_p=0.018) but is null in Herbal and marginal in Biologicals. This is consistent with C1154: h is section-determined except in Stars, where monitoring balance varies by program. In Herbal, breadth (mono/multi) shows a marginal effect through a different mechanism.

### F4: Distributional detail and combinatorial structure add nothing useful
Tier 2 (spread) and Tier 3 (quartiles) add only 2.2% dR^2 over Tier 1 (means). In LOO, they actively hurt prediction. Similarly, combining discrete and continuous representations hurts rather than helps. The signal is in three simple paragraph-level means.

## Constraints

### C1764: MP_present is Best Simple Repertoire Predictor of h_ratio
**Tier 2 | Scope: B**

Among 4 simple repertoire properties tested against Baseline A (PREFIX + section + parcount), MP_present (binary: folio has at least one MONITORING-Phase paragraph) is the strongest predictor of h_ratio (dR^2=0.083, F=8.22, perm_p=0.018). TQ_MP_exclusion is marginal (dR^2=0.040, perm_p=0.089). Breadth properties (mono/multi, entropy) are null. Full repertoire type (M5, 8 dummies) explains 0.241 dR^2 but adds 0.158 beyond M1 using 7 extra parameters. MP_present is the most parsimonious simple mechanism.

### C1765: Continuous Paragraph Means Dominate Discrete Zone Labels for h_ratio Prediction
**Tier 2 | Scope: B**

Three continuous paragraph-level means (folio-averaged THERMAL_score, MONITORING_score, h_kernel_frac) explain 53.6% additional h_ratio variance beyond PREFIX + section + parcount, compared to 24.1% for discrete zone labels (8 dummies). LOO cross-validation: continuous R^2_cv=0.679 vs discrete R^2_cv=0.111. Distributional features (spread, quartiles) add only 2.2% in-sample and hurt out-of-sample. The "repertoire predicts h_ratio" effect (C1763) is a continuous gradient, not combinatorial zone bundling. The discrete categorization (C1398) is a crude proxy that loses information relative to the underlying paragraph-level scores.

### C1766: Stars-Specific Repertoire-h_ratio Effect via MP_present
**Tier 2 | Scope: B**

Within Stars (n=23), MP_present explains 27.6% additional h_ratio variance (F=7.41, perm_p=0.018) -- the only section with a significant single-predictor repertoire effect. In Biologicals (n=20), MP_present is marginal (dR^2=0.150, perm_p=0.083). In Herbal (n=31), breadth rather than presence is marginal (mono/multi dR^2=0.134, perm_p=0.063). Consistent with C1154: h is section-determined in 3/4 sections but program-specific in Stars, where MONITORING-Phase paragraph presence discriminates monitoring balance.

### C1767: Kernel Ecology Fully Absorbs Repertoire Effects on h_ratio
**Tier 2 | Scope: B**

Adding k_ratio and e_ratio to Baseline A yields Baseline B with R^2=0.969. Against Baseline B, MP_present adds dR^2=0.0003 and full repertoire type adds dR^2=0.0022 (both null). The entire repertoire effect on h_ratio is mediated by kernel ecology. This is algebraically expected (h_ratio = h/(k+h+e)), but reveals that PREFIX fractions are poor proxies for kernel ecology -- paragraph-level continuous scores (C1765) or kernel ratios themselves capture what PREFIX cannot. Repertoire does not carry independent architectural information about h_ratio beyond kernel composition.
