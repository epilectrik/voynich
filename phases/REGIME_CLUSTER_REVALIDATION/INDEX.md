# Phase 590: REGIME_CLUSTER_REVALIDATION

**Status:** COMPLETE
**Date:** 2026-03-15
**Constraints:** C1712-C1715

## Objective

Revalidate C179 (4-REGIME count, silhouette 0.23) with 22 primary transcript features, 3 clustering methods (K-Means, Ward, GMM), gap statistic, permutation null, within-Herbal substructure test, section residualization, and bootstrap stability.

## Method

- **Features:** 22 features from 6 families (HEAD domain, PREFIX composition, suffix/closure, line structure, dynamics, vocabulary), computed directly from transcript
- **PCA:** 95% variance threshold → 12 PCs
- **Clustering:** K-Means (100 restarts), Ward hierarchical, GMM (diag covariance) for k=2..8
- **Validation:** Silhouette, Calinski-Harabasz, Davies-Bouldin, BIC (GMM), gap statistic (B=500), bootstrap stability (200 resamples), permutation null (100 permutations)
- **Controls:** Within-Herbal clustering (32 folios), section residualization, random null

## Key Results

| Metric | k=2 | k=4 |
|--------|-----|-----|
| K-Means silhouette | 0.2175 | 0.2142 |
| Ward silhouette | 0.2091 | 0.1768 |
| GMM silhouette | 0.2080 | 0.1679 |
| Null p95 | 0.2343 | 0.1671 |
| **Above null?** | **NO** (0.2175 < 0.2343) | **YES** (0.2142 > 0.1671) |

- **Gap statistic optimal k:** 2 (Tibshirani criterion)
- **Consensus k:** 2 (3/3 methods by silhouette)
- **k=2 cross-tab:** Cluster 0 = {H:30, C:5, S:9, T:2}, Cluster 1 = {B:20, S:14} — essentially Bio vs non-Bio
- **Within-Herbal best sil:** 0.1676 (k=2), functionally meaningful: F=43.0 for HEAD self-transition rate (df=1,30)
- **Section-residualized best sil:** 0.1768 (k=2)
- **Bootstrap ARI:** 0.80 (k=2), 0.76 (k=4)
- **v2 comparison ARI:** 0.41 (new k=2 vs old k=4)

## Interpretation

The dominant signal in B folio feature space is a binary Bio vs non-Bio split, but this split is **not significant** against a permutation null (observed silhouette < null p95). At k≥3, genuine structure emerges that exceeds the null. k=4 is the strongest genuinely non-trivial partition (excess over null p95 = 0.047).

C179's k=4 is real but weak. The feature space is better described as a **gradient** than a set of discrete clusters. The gradient has a primary axis (Bio vs non-Bio, driven by qo_frac/k_frac/headless_frac on PC1) and secondary axes that create genuine but soft 4-way differentiation.

Within Herbal alone (32 folios), substructure is weak by silhouette (0.17) but functionally meaningful — HEAD self-transition rate differs dramatically across Herbal subgroups (F=43.0). This confirms REGIME is not purely a section alias: within-section operational variation exists.

## Constraints

### C1712: REGIME partition is gradient-like, not discrete
**Tier:** 2 (ESTABLISHED) | **Scope:** B

The 82 Currier B folios exhibit a feature-space gradient rather than discrete clusters. All three methods (K-Means, Ward, GMM) select k=2 by silhouette, but k=2 is not significant vs permutation null (sil=0.2175 < null p95=0.2343). The k=2 split is driven by Bio section membership. At k=4, genuine above-null structure exists (KM sil=0.2142 > null p95=0.1671, excess=0.047). C179's count of 4 is retained as the strongest non-trivial partition, but the silhouette (0.21) confirms these are soft modes on a gradient, not crisp clusters.

### C1713: REGIME has within-section functional substructure
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Within Herbal section alone (32 folios), k=2 clustering produces silhouette=0.1676 (weak by absolute standards) but HEAD self-transition rate differs dramatically across Herbal subgroups (one-way ANOVA F=43.0, df=1,30, p<<0.001). Section-residualized clustering on all 82 folios yields silhouette=0.1768 at k=2. REGIME is not purely a section alias — within-section operational variation exists and is functionally meaningful.

### C1714: REGIME assignment bootstrap stability 0.76-0.80
**Tier:** 2 (ESTABLISHED) | **Scope:** B

Bootstrap stability (200 resamples) yields ARI=0.80±0.15 at k=2 and ARI=0.76±0.14 at k=4. Both partitions are moderately stable under resampling. The 4-REGIME partition (ARI=0.76) is less stable than the binary section split (0.80) but not drastically so.

### C1715: PC1 is PREFIX/kernel axis (32% variance)
**Tier:** 2 (ESTABLISHED) | **Scope:** B

PCA on 22 folio features yields 12 PCs at 95% variance. PC1 (32% variance) loads on qo_frac (+0.326), headless_frac (-0.306), k_frac (+0.304) — the PREFIX/kernel composition axis that separates sections. PC2 (17%) loads on suffix_rate (+0.348), mean_middle_length (+0.346), e_frac (+0.325) — the closure/complexity axis. PC3 (11%) loads on ot_frac (+0.413), da_frac (-0.374), log_token_count (+0.360). The first two PCs alone capture 49% of variance and correspond to known structural axes.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/regime_revalidation.py` | ~2 min |

## Results

| File | Content |
|------|---------|
| `results/regime_revalidation_results.json` | Full results with all metrics, sweep data, controls |
