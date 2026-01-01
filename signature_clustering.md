# Signature Clustering

## Question
Do natural clusters emerge from signature vectors?

## K-Means Analysis

**Optimal K:** 2
**Best Silhouette Score:** 0.255

### Silhouette Scores by K

- K=2: 0.255 *
- K=3: 0.246
- K=4: 0.23
- K=5: 0.233
- K=6: 0.192
- K=7: 0.185
- K=8: 0.156
- K=9: 0.177
- K=10: 0.19

## Cluster-Family Alignment

### Cluster 0
  - Family 2: 40 folios
  - Family 3: 1 folios
  - Family 5: 2 folios

### Cluster 1
  - Family 1: 3 folios
  - Family 2: 13 folios
  - Family 3: 6 folios
  - Family 4: 11 folios
  - Family 5: 3 folios
  - Family 6: 1 folios
  - Family 7: 1 folios
  - Family 8: 2 folios

## PCA Projection

**Variance Explained:** [np.float64(0.351), np.float64(0.238)]

*See signature_clustering.json for 2D projection coordinates.*

---

## Interpretation

**Weak clustering.** Signatures do not form clearly separated groups.

**Clusters do not strongly align with recipe families.** Other structural factors may dominate.