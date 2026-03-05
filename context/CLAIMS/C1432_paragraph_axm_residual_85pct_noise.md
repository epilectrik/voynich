# C1432: Paragraph AXM residual is 85% measurement noise

**Tier:** 2
**Scope:** B, paragraph, AXM, noise, design-freedom, C1169, C1405
**Phase:** 520 (PARAGRAPH_AXM_RESIDUAL)
**Date:** 2026-03-05

## Claim

The 29.4% paragraph AXM variance unexplained by PREFIX decomposes as: 25.2% binomial sampling noise (irreducible measurement uncertainty from finite token counts per paragraph) + 4.2% genuine design freedom. Noise accounts for 85.5% of the residual. Theoretical maximum R2 is 0.748; PREFIX achieves 0.706 (94.4% of theoretical maximum). Residuals are normally distributed (Shapiro-Wilk p=0.152), section-neutral (Kruskal-Wallis p=0.061), REGIME-neutral (p=0.444), and position-neutral (rho=0.030, p=0.615). Upgrades C1169's "~27% genuine design freedom" to "~4% genuine + ~25% noise" at paragraph level.

## Evidence

### Variance decomposition
- Total paragraph AXM variance: 0.01615
- Mean within-paragraph sampling variance: 0.00407 (binomial approximation)
- Noise fraction: 25.2% of total variance
- Theoretical maximum R2: 0.748 (= 1 - noise_fraction)
- PREFIX CV R2: 0.706 (94.4% of theoretical max)
- Gap to theoretical max: 4.3%
- Signal-to-noise ratio: 2.97

### Residual structure
- Residual mean: -0.0002 (centered)
- Residual std: 0.060
- Shapiro-Wilk normality: W=0.992, p=0.152 (normal)
- Section effect: Kruskal-Wallis H=9.00, p=0.061 (marginal, not significant)
- REGIME effect: Kruskal-Wallis H=2.68, p=0.444 (null)
- Paragraph position: rho=+0.030, p=0.615 (null)
- Folio residual std: 0.033 (folio-clustered but unstructured)

### Null control
- Shuffled PREFIX assignment: R2 = -0.056 +/- 0.030
- Z-score vs null: 25.2
- Real PREFIX signal is 25 standard deviations above noise

### Final decomposition
| Component | Fraction |
|-----------|----------|
| PREFIX explains | 70.6% |
| Other features add | 0.1% |
| Measurement noise | 25.2% |
| Genuine design freedom | 4.2% |

## Method

- Noise estimated from binomial sampling variance: Var(p) = p(1-p)/n for each paragraph
- Mean within-paragraph sampling variance computed across all 283 paragraphs
- Theoretical max R2 = 1 - (mean_sampling_variance / total_variance)
- Residual normality tested with Shapiro-Wilk
- Section/REGIME/position effects tested with Kruskal-Wallis and Spearman

## Provenance

- Script: `phases/PARAGRAPH_AXM_RESIDUAL/scripts/paragraph_axm_residual.py`
- Results: `phases/PARAGRAPH_AXM_RESIDUAL/results/paragraph_axm_residual.json`

## Dependencies

- C1405 (paragraph AXM driven by PREFIX)
- C1169 (AXM residual closed at ~27% -- now refined)
- C1035 (AXM residual irreducible -- now noise-decomposed)
- C458 (design asymmetry -- freedom narrower than estimated)
