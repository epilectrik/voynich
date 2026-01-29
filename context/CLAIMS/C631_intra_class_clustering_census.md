# C631: Intra-Class Clustering Census

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** INTRA_CLASS_DIVERSITY

## Statement

Hierarchical clustering of within-class successor JS divergence matrices across all 49 cosurvival classes yields an effective vocabulary of **56 functional sub-types** (expansion ratio 1.14x over 49 classes). Only 7/49 classes (14.3%) are heterogeneous (all with k=2); the remaining 42 (85.7%) are functionally uniform despite high mean within-class JS divergence (0.639). The within-class behavioral divergence documented in C506.b (73% of MIDDLE pairs JS > 0.4) is real but **continuous, not clustered** -- silhouette scores are overwhelmingly below the 0.25 acceptance threshold (mean silhouette for 3+ token classes: ~0.14). The 49-class system is therefore close to the effective functional vocabulary.

## Evidence

### Effective Vocabulary

| Metric | Value |
|--------|-------|
| Total cosurvival classes | 49 |
| Classified token types | 480 |
| Effective vocabulary (sum k) | 56 |
| Compression ratio (480/56) | 8.6x |
| Expansion ratio (56/49) | 1.14x |
| Heterogeneous classes | 7 (14.3%) |
| Uniform classes | 42 (85.7%) |

### k Distribution

| k | Classes | Percentage |
|---|---------|------------|
| 1 | 42 | 85.7% |
| 2 | 7 | 14.3% |

No class achieves k > 2.

### Heterogeneous Classes

| Class | Role | n_tokens | n_eligible | Silhouette | Method | Clusters |
|-------|------|----------|------------|------------|--------|----------|
| 3 | AX | 9 | 2 | 0.659 | THRESHOLD | {olain} vs {olkey} |
| 7 | FL | 2 | 2 | 0.408 | THRESHOLD | {ar} vs {al} |
| 8 | EN | 3 | 3 | 0.307 | SILHOUETTE | {chedy, shedy} vs {chol} |
| 22 | AX | 7 | 2 | 0.833 | THRESHOLD | {ly} vs {lr} |
| 30 | FL | 5 | 5 | 0.298 | SILHOUETTE | {dar, dal, dain, dair} vs {dam} |
| 37 | EN | 8 | 2 | 0.678 | THRESHOLD | {shky} vs {shek} |
| 44 | EN | 7 | 2 | 0.686 | THRESHOLD | {qopchdy} vs {qokechy} |

Only 2 classes (8 and 30) were identified by hierarchical clustering + silhouette optimization. The remaining 5 used the JSD > 0.4 threshold for 2-eligible-token classes.

### Silhouette Score Distribution (3+ eligible token classes)

For 36 classes with 3+ eligible tokens, best silhouette scores range 0.043 to 0.307. Only Class 8 (0.307) and Class 30 (0.298) exceed the 0.25 threshold.

## Interpretation

C506.b's finding that 73% of within-class MIDDLE pairs have JS > 0.4 does NOT imply discrete sub-types. The divergence is continuous -- tokens within a class vary in their successor preferences without forming clusters. This validates the 49-class cosurvival system as a near-optimal compression of the 480-type inventory. The 7 additional functional splits (all binary) provide only marginal refinement (56 vs 49).

The two structurally meaningful splits (identified by silhouette, not threshold) are:
- **Class 8** (EN_CHSH): chol separates from {chedy, shedy} -- consistent with C630's finding that chol is functionally distinct
- **Class 30** (FL_HAZ): dam separates from {dar, dal, dain, dair} -- suggesting a within-FL_HAZ functional division

## Extends

- **C506.b**: High within-class JS divergence (73% > 0.4) is continuous, not clustered
- **C629**: Class 23 sub-populations confirmed (silhouette = 0.225, below threshold) -- the restart vs generalist split is real but not discretely separable

## Related

C506, C506.a, C506.b, C629, C630, C632, C633
