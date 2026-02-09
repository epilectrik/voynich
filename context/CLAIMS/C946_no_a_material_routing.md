# C946: A Folios Show No Material-Domain Routing

**Tier:** 1 | **Status:** CLOSED (FALSIFIED) | **Scope:** A | **Source:** MATERIAL_LOCUS_SEARCH

## Statement

The hypothesis that A folios specialize in covering specific B sections (material domains) is **rejected**. A folio reach vectors have cosine similarity 0.997 (std=0.003), meaning every A folio covers all B sections with essentially identical MIDDLE vocabulary profiles. ARI=-0.007 for reach-vector clustering against B-section assignment. RI extensions show negligible section-routing (Cramer's V=0.071, far below 0.15 threshold). The A-to-B relationship operates through a generic shared vocabulary pool, not through material-domain-specific channels.

## Evidence

### A Folio Reach Uniformity

| Metric | Value |
|--------|-------|
| Pairwise cosine similarity | 0.997 (std=0.003) |
| Entropy ratio (observed/max) | 0.946 (near-uniform) |
| Clustering ARI (k=3) | -0.007 |
| Permutation p | 0.616 |

### RI Extension Section Routing (Test 5)

| Metric | Value | Threshold |
|--------|-------|-----------|
| Cramer's V (extension × section) | 0.071 | > 0.15 |
| Permutation p | 0.005 | < 0.01 |
| Cross-base Jaccard | 0.435 | > 0.70 for material |

The h-extension shows section T enrichment (1.99x) but this is explained by ct-prefix alignment (81% ct rate, per C917).

## What This Rules Out

If materials were routed from A to B through vocabulary specialization, different A folios would preferentially cover different B sections. The near-perfect uniformity (cosine 0.997) rules this out completely. A is a generic operational pool (C846).

## Related

C846, C885, C917, C918, C941
