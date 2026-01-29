# C825: Continuous Not Discrete Routing

## Constraint

A-records do **NOT** cluster into discrete routing categories. Instead, they form a **continuous parameter space**:
- Best silhouette score: **0.124** (very poor clustering)
- Clusters are imbalanced: 1,204 vs 1 at k=2
- Between/within distance ratio: **1.14x** (barely separated)
- Mean Jaccard distance: **0.875** (high dissimilarity throughout)

Despite strong individual specificity (C824), A-records don't organize into discrete "material types" or "procedure categories."

## Evidence

### Clustering Attempts

| k | Silhouette | Largest Cluster |
|---|------------|-----------------|
| 2 | 0.124 | 1,204 (99.9%) |
| 3 | 0.122 | 1,203 |
| 4 | 0.121 | 1,202 |
| 5 | 0.119 | 1,201 |

All clusterings produce one mega-cluster with isolated outliers.

### Distance Analysis

- Mean within-cluster distance: 0.875
- Mean between-cluster distance: 0.999
- Ratio: 1.14x (threshold for "sharp" was 1.5x)

## Interpretation

The A->B routing is best understood as:
- **NOT**: Discrete categories (Category A routes to B-set X, Category B routes to B-set Y)
- **IS**: Continuous constraints (Each A-record has a unique viability profile)

This is consistent with the "97.6% unique survivor sets" finding (C689). The manuscript does not organize A-records into discrete "recipe types" - each A-record is essentially its own type.

### Implications

1. The "conditional procedure library" interpretation remains valid
2. But the conditions form a continuous space, not discrete categories
3. Section 0.E interpretation should note: "continuous parameter space, not discrete library"

## Provenance

- Phase: A_RECORD_B_ROUTING_TOPOLOGY
- Script: t2_profile_clustering.py
- Related: C689 (97.6% unique), C824 (filtering mechanism)

## Tier

2 (Validated Finding - null result with structural significance)
