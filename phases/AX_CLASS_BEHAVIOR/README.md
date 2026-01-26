# AX_CLASS_BEHAVIOR Phase

## Purpose

Test whether the 20 AX instruction classes exhibit distinct behavioral patterns across positional, transitional, and contextual dimensions. If 20 classes exist, do they behave as 20 distinct functional units -- or do they collapse to fewer effective groups?

## Status: CLOSED

Phase complete. 1 constraint documented (C572). The 20 AX classes do NOT form behaviorally distinct groups. They collapse to 2 weak groups (silhouette=0.18). Position is the only real differentiator; transitions are mostly uniform; context provides no classification signal. This reinforces C571: AX classes reflect PREFIX morphological diversity, not functional behavioral diversity.

## Research Questions

| Question | Script | Status | Finding | Constraint |
|----------|--------|--------|---------|------------|
| Q1: Transition structure | ax_class_transition_matrix.py | **DOCUMENTED** | 3/20 classes structured (chi-squared p<0.01), rest uniform | C572 |
| Q2: Positional distinctness | ax_class_positional_profiles.py | **DOCUMENTED** | 10/20 Bonferroni-distinct from population, 65/190 pairs distinct | C572 |
| Q3: Context classification | ax_class_context_signatures.py | **DOCUMENTED** | 6.8% accuracy, below 10.3% weighted random baseline | C572 |
| Q4: Behavioral synthesis | ax_class_distinctness_synthesis.py | **DOCUMENTED** | k=2 clusters, silhouette=0.18, 7 PCA components for 90% | C572 |

## Key Finding: Behavioral Collapse

The 20 AX classes are morphologically distinct (different PREFIX patterns) but behaviorally interchangeable:

| Dimension | Signal Strength | Detail |
|-----------|----------------|--------|
| **Position** | Weak-moderate | 10/20 distinct from population; 65/190 pairwise distinct |
| **Transitions** | Minimal | 3/20 structured; rest indistinguishable from uniform |
| **Context** | None | 6.8% classification accuracy (below 10.3% random baseline) |
| **Clustering** | Weak | Best k=2, silhouette=0.1805 (worse than prior 0.2317) |
| **PCA** | Diffuse | 7 components for 90% variance |
| **Subgroup separation** | Marginal | 1.168x ratio (inter-/intra-subgroup distance) |

### Class 22: Sole Outlier

Class 22 is the only class with notable behavioral identity:
- Positional: D=0.506 vs population (strongest of all 20 classes)
- Context: 60% classification accuracy (next best: 33%)
- Clustering: consistently separates from others

All other classes are largely interchangeable within their positional subgroups (INIT/MED/FINAL).

## Interpretation

The 20 AX classes exist because PREFIX morphology creates 20 combinations, not because there are 20 functional roles. Position is the one axis where classes differ -- which is already captured by the 3-way positional sub-structure (INIT/MED/FINAL) from AUXILIARY_STRATIFICATION. The 20-class level adds almost no behavioral resolution beyond the 3-subgroup level.

This reinforces C571: PREFIX is the role selector, and MIDDLE is the material carrier. Within a given positional role (INIT, MED, FINAL), the specific AX class is functionally irrelevant.

## Documented Findings

### C572: AX Class Behavioral Collapse (Tier 2)
- 20 AX classes collapse to 2 effective behavioral groups
- Position: 10/20 Bonferroni-distinct, 65/190 pairs distinct
- Transitions: 3/20 structured (chi-squared p<0.01)
- Context: 6.8% accuracy (below 10.3% weighted random baseline)
- Clustering: best k=2, silhouette=0.1805 (worse than prior 0.2317)
- PCA: 7 components for 90% variance (36D feature space)
- Subgroup separation: 1.168x (barely above 1.0)
- Class 22 sole outlier (D=0.506, 60% context accuracy)
- Classes are interchangeable within positional subgroups (INIT/MED/FINAL)

## Scripts

| Script | Description | Status | Output |
|--------|-------------|--------|--------|
| ax_class_transition_matrix.py | 20x20 AX-to-AX transition matrix; per-class self-chain rate, entropy, chi-squared independence test | **C572** | ax_class_transition_matrix.json |
| ax_class_positional_profiles.py | Per-class positional CDFs; KS tests vs population; 190 pairwise KS tests with Bonferroni correction | **C572** | ax_class_positional_profiles.json |
| ax_class_context_signatures.py | Neighborhood role signatures; bigram enrichment; nearest-centroid classifier (16D context features) | **C572** | ax_class_context_signatures.json |
| ax_class_distinctness_synthesis.py | Combined 36D feature matrix; k-medoids clustering (k=2..8); PCA; confusability analysis; verdict | **C572** | ax_class_distinctness_synthesis.json |

## Dependencies

- **AUXILIARY_STRATIFICATION** (C563-C566): Positional sub-structure (INIT/MED/FINAL), class census
- **AX_FUNCTIONAL_ANATOMY** (C567-C571): PREFIX as role selector, vocabulary overlap, functional identity
- **CLASS_COSURVIVAL_TEST**: Class token map (class -> token membership)
- **CLASS_SEMANTIC_VALIDATION**: Role taxonomy (CC, EN, FL, FQ, AX)
