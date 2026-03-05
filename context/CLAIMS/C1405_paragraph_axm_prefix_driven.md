# C1405: Paragraph AXM Rate Driven by PREFIX Not Section

**Tier:** 2 (ESTABLISHED)
**Scope:** B, paragraph, AXM, PREFIX, variance decomposition
**Phase:** SECTION_PARAGRAPH_AXM_DRIVERS (Phase 514)
**Extends:** C1403 (MONOSTATE thematic dominance), C1169 (27% AXM residual), C1023 (PREFIX routing sole load-bearing)
**Relates to:** C1012 (PREFIX positive channeling), C1015 (PREFIX-conditioned macro-state), C1384 (k-initial predicts AXM dwell)

---

## Statement

Paragraph-level AXM rate is **dominated by PREFIX composition** (5-fold CV R2 = 0.736). Section alone has NEGATIVE predictive power (CV R2 = -0.027). The full model including section, PREFIX, kernel, and category features achieves CV R2 = 0.760. Section's marginal contribution beyond PREFIX is +1.7%, effectively zero. The 24% residual is genuine paragraph-level design freedom.

### Variance Decomposition (n=283 paragraphs)

| Model | CV R2 |
|-------|-------|
| Section only | **-0.027** |
| REGIME only | -0.092 |
| Section + REGIME | -0.077 |
| PREFIX only | **0.736** |
| Kernel only | 0.096 |
| Category only | 0.271 |
| Length only | -0.167 |
| Section + PREFIX | 0.736 |
| Section + kernel | 0.244 |
| Section + category | 0.315 |
| **Full model** | **0.760** |
| Full minus section | 0.743 |
| **Section marginal** | **+0.017** |

### Top Univariate Correlates

| Feature | Spearman rho | p-value |
|---------|-------------|---------|
| qo_frac | +0.576 | 1.9e-26 |
| staging_frac | -0.525 | 1.9e-21 |
| bare_frac | -0.515 | 1.5e-20 |
| chsh_frac | +0.508 | 5.7e-20 |
| operation_frac | -0.469 | 7.0e-17 |

### Key Findings

1. **PREFIX dominates**: qo_frac (rho=+0.576) and chsh_frac (rho=+0.508) are the two strongest positive predictors. Both are thermal-processing PREFIXes. More heat/monitoring = more AXM.

2. **BARE is anti-AXM**: bare_frac (rho=-0.515) is the strongest negative PREFIX predictor. BARE tokens lack operational domain selection, reducing main-loop dwell.

3. **Section is informationally redundant**: Adding section to PREFIX provides zero gain (0.736 vs 0.736). Section effects are fully mediated by the PREFIX profiles of their constituent paragraphs.

4. **Kernel confirms C1384**: k-fraction (rho=+0.432) is the strongest kernel predictor, consistent with C1384's finding that k-initial MIDDLE fraction predicts AXM self-transition at the folio level. This extends to paragraph level.

5. **24% residual = design freedom**: The full model leaves 24% unexplained. This is consistent with C1169's folio-level 27% residual and C458's recovery-free design principle.

---

## Falsification Criteria

1. If a non-PREFIX feature set achieves CV R2 > 0.50, PREFIX dominance is weakened
2. If section's marginal contribution exceeds +0.10 under a different model specification, section carries independent signal
3. If the 24% residual is reduced by >50% by a latent variable (e.g., apparatus type, material class), the design-freedom interpretation weakens

---

## Method

- 283 paragraphs across 74 folios (3+ body lines, 10+ classified tokens per paragraph)
- Paragraph AXM rate = fraction of classified tokens in AXM macro-state (C976 partition)
- 21 morphological features: 7 PREFIX fractions, 3 kernel fractions, suffix rate, mode fraction, mean token length, 8 operational category fractions
- 5-fold cross-validated R2 using sklearn LinearRegression
- Spearman rank correlations for univariate analysis
- Nested model comparison for variance decomposition (full model vs. leave-one-out)

**Script:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/scripts/section_paragraph_drivers.py`
**Results:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json` (tests B1-B6)
