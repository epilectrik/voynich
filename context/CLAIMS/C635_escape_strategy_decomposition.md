# C635: Escape Strategy Decomposition

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** RECOVERY_ARCHITECTURE_DECOMPOSITION

## Statement

Escape strategies are **NOT regime-stratified** at the folio level: 0/9 Kruskal-Wallis tests are significant for EN sub-group composition in recovery zones (EN_QO/EN_CHSH/EN_MINOR fractions), first-EN-after-hazard routing, or CC sub-group composition. However, chi-squared on **aggregate** first-EN-after-hazard counts IS significant (chi2=25.45, p=0.0003, dof=6), indicating a population-level REGIME signal in first-response routing that does not resolve to per-folio consistency. Pairwise JS divergence between REGIME escape fingerprints is uniformly low (0.031-0.082), with REGIME_3 vs REGIME_4 most divergent (JSD=0.082), driven by CC_DAIIN vs CC_OL balance.

## Evidence

### EN Sub-Group Fractions in Recovery Zones (Per-REGIME)

| REGIME | n | EN_CHSH | EN_MINOR | EN_QO |
|--------|---|---------|----------|-------|
| REGIME_1 | 23 | 0.262 | 0.108 | 0.630 |
| REGIME_2 | 24 | 0.309 | 0.122 | 0.569 |
| REGIME_3 | 8 | 0.283 | 0.104 | 0.613 |
| REGIME_4 | 27 | 0.246 | 0.126 | 0.629 |

All KW p > 0.48 -- no REGIME differentiation.

### First-EN-After-Hazard Routing

| REGIME | n | EN_CHSH | EN_MINOR | EN_QO |
|--------|---|---------|----------|-------|
| REGIME_1 | 23 | 0.276 | 0.099 | 0.626 |
| REGIME_2 | 24 | 0.269 | 0.139 | 0.592 |
| REGIME_3 | 8 | 0.294 | 0.070 | 0.636 |
| REGIME_4 | 27 | 0.249 | 0.151 | 0.600 |

Per-folio KW: all p > 0.11. Closest: EN_MINOR (p=0.113).
Aggregate chi-squared: chi2=25.45, p=0.0003, dof=6 -- significant at population level.

The discrepancy between per-folio KW (not significant) and aggregate chi-squared (significant) indicates that REGIME-level differences in EN sub-group first-response emerge only from pooled counts, not from individual folio consistency. This is consistent with high within-REGIME folio variance.

### CC Sub-Group Fractions in Recovery Zones

| REGIME | n | CC_DAIIN | CC_OL | CC_OL_D |
|--------|---|----------|-------|---------|
| REGIME_1 | 22 | 0.284 | 0.443 | 0.273 |
| REGIME_2 | 22 | 0.273 | 0.465 | 0.262 |
| REGIME_3 | 8 | 0.246 | 0.504 | 0.249 |
| REGIME_4 | 27 | 0.376 | 0.367 | 0.257 |

All KW p > 0.57 -- no REGIME differentiation in CC trigger composition.

### Pairwise JS Divergence (Escape Fingerprints)

| Pair | JSD |
|------|-----|
| REGIME_1 vs REGIME_2 | 0.034 |
| REGIME_1 vs REGIME_3 | 0.033 |
| REGIME_1 vs REGIME_4 | 0.053 |
| REGIME_2 vs REGIME_3 | 0.031 |
| REGIME_2 vs REGIME_4 | 0.069 |
| REGIME_3 vs REGIME_4 | 0.082 |

All JSD < 0.10 -- REGIMEs use nearly identical escape strategies. The largest divergence (REGIME_3 vs REGIME_4) is driven by REGIME_4 favoring CC_DAIIN (0.188 normalized) over CC_OL (0.183), while REGIME_3 favors CC_OL (0.252) over CC_DAIIN (0.123).

## Interpretation

Recovery escape strategies are folio-specific, not REGIME-dictated. The aggregate chi-squared signal in first-EN routing reflects the mechanical consequence of different class compositions across REGIMEs (C545), not a distinct recovery strategy. When measured at the folio level where individual program decisions are made, no REGIME differentiation emerges. This confirms that escape strategy selection is a per-folio design choice, consistent with C458's characterization of recovery as "free" (CV=0.72-0.82).

## Extends

- **C458**: Recovery freedom (CV=0.72-0.82) extends to escape sub-group routing, not just aggregate recovery counts
- **C398**: QO escape rates vary by class (EN 40-67%, CC 22-32%) -- but this class-level differentiation does not translate to REGIME-level escape strategy differences
- **C545/C551**: REGIME class composition differences produce aggregate chi-squared signals but not per-folio escape strategy differentiation

## Related

C397, C398, C458, C545, C551, C602, C634, C636
