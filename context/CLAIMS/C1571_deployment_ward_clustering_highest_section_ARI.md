# C1571: Deployment Features Achieve Highest Section ARI via Ward Clustering

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, domain, compositional, deployment, clustering, Ward, ARI, section, C1567, C1568, C1569, C1570
**Phase:** WITHIN_DOMAIN_COMPOSITIONAL_CONTROL (Phase 560b)
**Date:** 2026-03-08

## Claim

Ward-linkage hierarchical clustering on deployment features achieves the highest section Adjusted Rand Index (ARI = 0.615) of any tested feature set, confirming deployment grammar is a stronger section-level discriminator than within-domain marginals (ARI = 0.443). Section identity is encoded more in HOW domains are deployed than in domain proportions alone.

## Evidence

### Ward Clustering ARI by Feature Set

| Feature Set | Size | ARI (Ward) |
|-------------|------|-----------|
| HEAD | 6 | 0.327 |
| MARGINAL | 32 | 0.443 |
| **DEPLOYMENT** | **56** | **0.615** |
| FULL_560 | 38 | 0.460 |
| FULL_560b | 62 | 0.499 |
| COMBINED | 94 | 0.451 |

5 Ward clusters against 5 section labels (S, H, B, C, P). All sets pass the ARI > 0.10 threshold.

### Comparison to Phase 560

Phase 560 D4 used single-linkage clustering and achieved ARI = -0.024 (FAIL). The improvement reflects:
1. **Method correction:** Ward linkage avoids chaining noise that degrades single-linkage
2. **Feature richness:** 56 deployment features capture zone, routing, closure, headless, and paragraph dimensions

### Deployment > Marginal Gap

DEPLOYMENT ARI (0.615) exceeds MARGINAL ARI (0.443) by +0.172. This gap is larger than the HEAD-to-MARGINAL improvement (+0.116), indicating that sections differ primarily in **how shared domains are staged, routed, and closed** rather than merely in domain proportions or within-domain averages.

Notably, COMBINED (94 features, ARI = 0.451) is WORSE than DEPLOYMENT alone (56 features, ARI = 0.615). Adding marginal features to deployment dilutes the deployment signal in Ward clustering, suggesting marginal and deployment features capture partially overlapping structure, with deployment being the cleaner signal.

## Interpretation

Section identity is encoded more strongly in deployment packaging — how domains are placed in zones, how routing chains work, how lines close, how headless tokens distribute, how paragraphs emphasize operations — than in the within-domain tuning of individual domain features. This makes deployment grammar the primary architectural signature of section identity.

## Falsification Criteria

1. If a larger corpus (more folios per section) changes the ARI ranking
2. If average-linkage or complete-linkage clustering reverses the DEPLOYMENT > MARGINAL ordering
3. If the ARI advantage disappears when NaN-heavy features are excluded

## Source

`phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t3b_discriminability.json`
