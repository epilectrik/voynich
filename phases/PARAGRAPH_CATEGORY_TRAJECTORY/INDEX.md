# Phase 591: PARAGRAPH_CATEGORY_TRAJECTORY

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1716, C1717

## Objective

Test whether the 8-category fraction vector (C1250: THERMAL, FLOW, TRANSITION, OPERATION, STAGING, CONTAINMENT, MARKING, MONITORING) shows systematic trajectory across paragraph body line positions. C963 established homogeneity at role-fraction level; this phase tests at the finest available grain.

## Method

- **Paragraphs:** 100 gallows-initial paragraphs with 6+ lines (5+ body lines). Section distribution: B=34, H=30, S=28, C=7, T=1. 914 body lines analyzed.
- **T1:** Raw Spearman rho per category vs body position (Bonferroni alpha=0.00625)
- **T2 (DECISIVE):** Partial Spearman controlling for line length, pooled and within-section
- **T3:** Within- vs between-paragraph JSD on 8-category vector (extends C1288)
- **T4:** Lag-k autocorrelation on PCA-reduced category vectors (PC1 31%, PC2 19%)
- **T5:** Category × suffix mode interaction (Mann-Whitney per category)
- **T6:** Partial correlation controlling kernel fractions + line length

## Key Results

| Test | Verdict | Key Metric |
|------|---------|------------|
| T1: Raw trajectory | 0/8 significant | Largest rho: +0.044 (THERMAL) |
| T2: Length-controlled | **0/8 significant** (pooled + all sections) | All p > 0.17 |
| T3: JSD comparison | Within > between | Ratio 1.11 (within=0.209, between-same-folio=0.188) |
| T4: Serial dependence | No significant autocorrelation | All shuffle p > 0.14 |
| T5: Mode-category | **5/8 significant** | THERMAL +0.150, TRANSITION -0.068, STAGING -0.049 |
| T6: Kernel control | All 8 collapsed | 0/8 survive kernel+length control |

## Interpretation

Body lines within paragraphs are compositionally homogeneous at 8-category resolution after controlling for line length. No category shows significant trend across body positions, neither pooled nor within any section. This extends C963 from role-fraction level to the finest operational grain available.

T3 reveals that within-paragraph body-line JSD (0.209) actually *exceeds* between-paragraph-same-folio JSD (0.188). Paragraph identity does not constrain body-line category composition beyond the folio template. Body lines are drawn from the folio's category profile, not from a paragraph-specific subprofile.

T5 confirms C1279/C1309: suffix modes A and B have strongly different category profiles (5/8 categories differentiated). Mode A is THERMAL-enriched (+0.150), Mode B is TRANSITION/STAGING-enriched. This mode-category coupling is real but does NOT create trajectory — modes alternate without systematic positional trend.

T6 confirms all category-position effects (already non-significant) collapse further under kernel control, consistent with C1291 (kernel-mediated category associations).

## Constraints

### C1716: Category trajectory flat at 8-category resolution
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Body lines within paragraphs show no systematic category trajectory after length control. 0/8 categories significant at Bonferroni alpha=0.00625, both pooled (N=914 body lines, 100 paragraphs) and within-section (B: N=378, H: N=223, S: N=240, C: N=68). Largest partial rho: -0.042 (MARKING, p=0.20). Extends C963 from role-fraction level (EN/FL/CC) to the finest operational grain (8 categories, C1250). No serial dependence detected: lag-1 autocorrelation on category PC1 = -0.13 (shuffle null: -0.16, p=0.69).

### C1717: Within-paragraph category diversity exceeds between-paragraph
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Within-paragraph body-line JSD on 8-category vector (0.209) exceeds between-paragraph-same-folio JSD (0.188), ratio=1.11. Cross-folio JSD = 0.241. Paragraph identity does NOT constrain body-line category composition — body lines are drawn from the folio category profile, not from a paragraph-specific subprofile. Folio shuffle null JSD = 0.212 (within-paragraph observed is below null in 0/100 permutations). This extends C963 (body homogeneity) and C1288 (within-folio paragraph similarity) by showing that the similarity operates at folio level, not paragraph level.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/paragraph_category_trajectory.py` | ~90 sec |

## Results

| File | Content |
|------|---------|
| `results/paragraph_category_trajectory_results.json` | Full results with all 6 tests, controls, decision logic |
