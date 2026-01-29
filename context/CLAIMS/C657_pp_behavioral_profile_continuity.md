# C657: PP Behavioral Profile Continuity

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

B-side successor profiles for PP MIDDLEs are continuous with no discrete behavioral clusters. 93 PP MIDDLEs with ≥10 B-side bigrams produce 49D successor class distributions with mean pairwise JSD=0.537 and median=0.548. Hierarchical clustering yields best silhouette of 0.237 at k=2 (below 0.25 threshold), with a degenerate split (2 outliers vs 91 in main cluster). Lane character does not predict behavioral cluster (ARI=0.010).

## Evidence

- 93 PP MIDDLEs eligible (≥10 B-side bigrams)
- Pairwise JSD: mean=0.537, median=0.548 — substantial behavioral diversity
- UPGMA silhouette: k=2: 0.237, k=3: 0.204, k=5: 0.167, k=10: 0.117 — all below 0.25
- Cluster sizes at k=2: {1: 2, 2: 91} — degenerate (two rare-profile outliers)
- Morphological prediction: ARI(behavioral cluster, lane character) = 0.010
- C649 initial character rule does not predict B-side behavioral profile

## Interpretation

PP MIDDLEs that appear in B execution show continuously varying successor profiles. The behavioral diversity is substantial (mean JSD=0.537 is higher than typical within-class JSD from C631), confirming that PP MIDDLEs spanning multiple B classes create broader behavioral variation. But this variation is gradient, not clustered — there are no natural behavioral types within the PP population.

## Cross-References

- C631: Within-class MIDDLE distributions mostly continuous (34/36 classes) — extended here
- C506.b: Within-class behavioral heterogeneity (73% JSD > 0.4) — here we show the heterogeneity is continuous
- C656: Co-occurrence also continuous — PP is continuous on both A-side and B-side axes
- C659: Behavioral and co-occurrence axes are independent

## Provenance

PP_POOL_CLASSIFICATION, Script 2 (pp_pool_validation.py), Test 5
