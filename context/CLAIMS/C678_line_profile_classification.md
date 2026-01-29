# C678: Line Profile Classification

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

Currier B lines form a **continuous distribution** with no discrete functional types. Best KMeans silhouette = 0.0995 (k=5), far below the 0.15 threshold for meaningful clustering. Hierarchical clustering (UPGMA) at k=2 achieved sil=0.582 but was degenerate (2400 vs 1 outlier). PCA shows diffuse variance: 10 components needed for 68.3%.

## Method

27-dimensional feature vector per line: role fractions (5), QO fraction (1), CC trigger fractions (3), LINK density (1), hazard density (1), suffix profile (6), PREFIX profile (8), z-scored line length (1), type-token ratio (1). Z-score normalized. Silhouette sweep k=2..15 for both UPGMA and KMeans (10 restarts).

## Key Numbers

| Metric | Value |
|--------|-------|
| Feature dimensions | 27 |
| Lines classified | 2,401 |
| Best KMeans sil | 0.0995 (k=5) |
| Best UPGMA sil | 0.5822 (k=2, degenerate) |
| Verdict | CONTINUOUS (no discrete types) |

## PCA Structure

| PC | Variance | Top Loadings |
|----|----------|-------------|
| PC1 | 12.1% | +sfx_bare(0.42), -pfx_qo(0.41), -sfx_e_family(0.32), -QO_frac(0.31) |
| PC2 | 9.3% | +CC(0.51), +link_density(0.45), +pfx_ol(0.43), +cc_old(0.38) |
| PC3 | 8.7% | — |
| PC1-10 | 68.3% | Cumulative |

## Interpretation

PC1 captures a **morphological complexity axis**: high bare-suffix, low qo-PREFIX, low e_family lines at one pole vs morphologically rich lines at the other. PC2 captures a **monitoring intensity axis**: high CC, high LINK, high pfx_ol lines are monitoring-heavy.

These are continuous, overlapping dimensions, not discrete line types. Lines vary smoothly along multiple independent axes, consistent with parametric control (each line samples from a multi-dimensional parameter space) rather than categorical switching (discrete modes or phases).

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_profile_classification.py` (Tests 11-12)
- Extends: C171 (94.2% class change line-to-line), C391 (time-reversal symmetry)
