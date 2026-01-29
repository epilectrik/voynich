# INTRA_CLASS_DIVERSITY

**Phase status:** COMPLETE | **Constraints:** C631-C633 | **Date:** 2026-01-26

## Objective

Determine the effective functional vocabulary size of Currier B by clustering within-class behavioral diversity across all 49 cosurvival classes, and test whether morphological features predict cluster membership.

## Key Findings

1. **Effective vocabulary is 56** (C631). Only 7/49 classes split (all into k=2). The 49-class system captures 86% of functional vocabulary; within-class JS divergence (C506.b: 73% > 0.4) is continuous, not clustered.

2. **MIDDLE predicts clusters** (C632). In 6/7 heterogeneous classes, MIDDLE identity perfectly separates clusters (ARI = 1.0). Class 30 (FL_HAZ) is morphologically opaque. No test reaches significance due to n = 2-5.

3. **Hazard classes are more diverse** (C633). 50% of hazard classes are heterogeneous vs 9% of non-hazard (Fisher p = 0.031). FLOW_OPERATOR is the most internally diverse role (mean k = 1.50).

4. **Size inversely predicts heterogeneity** (C633). Smaller classes are more likely to split (rho = -0.321, p = 0.025). Mean JSD does NOT predict k (rho = 0.004, p = 0.978).

## Verdict

The 49-class cosurvival system is near-optimal. Within-class divergence is continuous (allophonic) rather than discrete (phonemic). The marginal expansion to 56 sub-types adds 7 binary splits, mostly in small hazard/flow classes. The hazard system contains proportionally more functional distinctions, consistent with its role as a precision mechanism.

## Scripts

| Script | Sections | Output |
|--------|----------|--------|
| `intra_class_clustering.py` | Successor profiles, JSD matrices, hierarchical clustering, silhouette | `results/intra_class_clustering.json` |
| `morphology_subtype_prediction.py` | Feature extraction, ARI test, dominant predictor, summary | `results/morphology_subtype_prediction.json` |
| `effective_vocabulary_census.py` | Vocabulary size, role decomposition, correlations, hazard comparison | `results/effective_vocabulary_census.json` |

## Data Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `scripts/voynich.py`
