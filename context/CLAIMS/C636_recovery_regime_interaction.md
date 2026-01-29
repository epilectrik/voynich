# C636: Recovery-Regime Interaction

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** RECOVERY_ARCHITECTURE_DECOMPOSITION

## Statement

Recovery architecture is **UNCONDITIONALLY FREE** for 10/12 features: no REGIME dependence survives in raw or partial Kruskal-Wallis tests. However, two kernel absorption features (e_rate, h_rate) show a **SUPPRESSOR** pattern: not significant in raw KW (p=0.565, p=0.742) but highly significant after controlling for class composition (partial KW p=0.0005 eta_sq=0.188 for e_rate; p<0.0001 eta_sq=0.293 for h_rate). Class composition masks a latent REGIME effect on kernel routing -- REGIMEs differ in how kernel transitions resolve toward e (HOME_POSITION) versus h, but this is invisible without controlling for the covariates that REGIMEs also determine.

## Evidence

### Feature-Level Verdicts

| Feature | Raw_p | Partial_p | Verdict |
|---------|-------|-----------|---------|
| e_rate | 0.565 | **0.0005** | SUPPRESSOR |
| h_rate | 0.742 | **<0.0001** | SUPPRESSOR |
| k_rate | 0.464 | 0.069 | FREE |
| kernel_exit_rate | 0.583 | 0.739 | FREE |
| mean_recovery_path_length | 0.693 | 0.879 | FREE |
| n_recovery_paths | 0.098 | 0.604 | FREE |
| post_kernel_en_frac | 0.830 | 0.997 | FREE |
| post_kernel_ax_frac | 0.188 | 0.523 | FREE |
| en_qo_recovery_frac | 0.485 | 0.642 | FREE |
| en_chsh_recovery_frac | 0.552 | 0.904 | FREE |
| first_en_qo_frac | 0.422 | 0.704 | FREE |
| cc_daiin_recovery_frac | 0.879 | 0.971 | FREE |

Verdict distribution: FREE 10/12, SUPPRESSOR 2/12.

### Suppressor Mechanism Explained

REGIMEs strongly differ in class composition covariates:
- en_qo_share: REGIME_1=0.342 vs REGIME_2=0.208 (KW p<0.0001)
- en_chsh_share: REGIME_1=0.135 vs REGIME_2=0.098 (KW p=0.004)
- total_en_share: REGIME_1=0.525 vs REGIME_2=0.345 (KW p<0.0001)
- cc_share: REGIME_3=0.105 vs others ~0.061 (KW p=0.034)

These composition differences are correlated with kernel absorption in a way that cancels the direct REGIME->kernel routing effect. Once composition is regressed out, the residual kernel routing differs significantly by REGIME with substantial effect sizes (eta_sq=0.188 and 0.293).

### Interpretation of the SUPPRESSOR Effect

The SUPPRESSOR pattern for e_rate and h_rate means: **REGIMEs have distinct kernel routing preferences (e vs h absorption) that are masked by their different class compositions.** In other words, REGIME_1's high EN_QO share and REGIME_3's high CC share produce different baseline expectations for e/h rates, and when those baselines are removed, the REGIME-specific routing differences emerge.

This is NOT the same as "REGIME-STRATIFIED" in the standard sense, because the raw signal is invisible. It represents a **second-order REGIME effect** -- a hidden constraint on kernel routing that only becomes detectable after partialing out composition.

### Partial Correlation Method

1. Rank-transform recovery feature and 5 covariates (en_qo_share, en_chsh_share, en_minor_share, cc_share, total_en_share)
2. OLS regress recovery feature on covariates
3. Extract residuals (recovery variance NOT explained by composition)
4. Kruskal-Wallis test on residuals grouped by REGIME

## Interpretation

The dominant finding is UNCONDITIONALLY FREE: 10/12 recovery features show no REGIME dependence at any level. Each folio independently determines its recovery strategy for path lengths, escape routing, post-kernel destinations, and sub-group composition.

The SUPPRESSOR effect on e_rate and h_rate is a secondary finding. It suggests REGIMEs may encode a latent preference for e (HOME_POSITION) vs h absorption that is mechanically obscured by composition differences. This could reflect a genuine second-order architectural distinction or could arise from multicollinearity between the 5 covariates and the rank-transformed REGIME groups. With n=82 folios and 5 covariates, the partial correlation has adequate but not generous degrees of freedom.

**Conservative interpretation:** Recovery is free. The e/h suppressor effect warrants noting but does not change the dominant characterization.

## Extends

- **C458**: "Recovery is free" CONFIRMED and decomposed: free at pathway level (C634), escape strategy level (C635), and 10/12 composite features (this constraint)
- **C105**: e=54.7% HOME_POSITION dominance -- the suppressor effect suggests this dominance may vary by REGIME after controlling for composition
- **C521**: h->e one-way valve -- the relative balance of e vs h absorption appears REGIME-sensitive in partial analysis

## Related

C105, C397, C398, C458, C521, C545, C551, C602, C634, C635
