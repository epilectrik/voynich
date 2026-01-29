# C612: UN Population Structure

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase UN_COMPOSITIONAL_MECHANICS
**Scope:** B_INTERNAL | UN

## Statement

UN bifurcates into 2 distinct clusters (silhouette=0.263, stronger than EN anatomy's 0.180). Cluster 0 (n=2,108 types) has 94% suffix rate, dominated by EN/AX predictions. Cluster 1 (n=2,313 types) has 69% suffix rate, dominated by AX/FQ predictions. Hapax types are significantly longer than repeaters (6.65 vs 5.84 chars, p<0.0001). Folio-level UN proportion strongly correlates with lexical diversity (rho=+0.631***) and negatively with LINK density (rho=-0.524***). REGIME does not predict UN proportion (p=0.205).

## Evidence

### Clustering

| k | Silhouette | Calinski-Harabasz |
|---|-----------|-------------------|
| 2 | **0.263** | 2069.4 |
| 3 | 0.183 | 1517.8 |
| 4 | 0.190 | 1241.5 |
| 5 | 0.217 | 1124.3 |

Best k=2 by silhouette. Stronger structure than EN anatomy (C574: silhouette=0.180).

### Cluster Characterization

| Property | Cluster 0 | Cluster 1 |
|----------|-----------|-----------|
| N types | 2,108 | 2,313 |
| Suffix rate | 0.94 | 0.69 |
| Articulator rate | 0.09 | 0.12 |
| Top roles | EN, AX, FQ | AX, FQ, EN |

Interpretation: Cluster 0 = morphologically elaborate forms (suffix-heavy, EN/AX). Cluster 1 = shorter, less elaborated forms (FQ/AX).

### Hapax vs Repeater

| Feature | Hapax (n=3,274) | Repeater (n=1,147) |
|---------|-----------------|-------------------|
| PREFIX rate | 81.8% | 84.3% |
| SUFFIX rate | 83.0% | 74.2% |
| Articulator rate | 10.7% | 9.5% |
| Mean length | **6.65** | **5.84** |

Hapax are significantly longer (Mann-Whitney p<0.0001). Longer tokens = more compositional combinations = more likely to be unique.

### Folio-Level Predictors (Bonferroni-corrected)

| Variable | rho | p_bonf |
|----------|-----|--------|
| type_token_ratio | **+0.631** | <0.0001*** |
| link_density | **-0.524** | <0.0001*** |
| ch_preference | +0.341 | 0.007** |
| escape_density | +0.158 | 0.622 |

Folios with higher lexical diversity have more UN. Folios with more LINK tokens have less UN. REGIME has no significant effect (Kruskal-Wallis H=4.59, p=0.205).

## Interpretation

UN proportion is a **diversity index**: it measures how many morphologically unique tokens a folio produces. High-UN folios are lexically rich (many unique combinations), while low-UN folios reuse common classified tokens. This is consistent with UN being the compositional tail of the grammar, not a structurally distinct population.

## Related

- C566 (UN morphologically normal)
- C574 (EN behavioral collapse at k=2)
- C610 (UN morphological profile)
- C611 (UN role prediction)
