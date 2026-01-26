# C572: AX Class Behavioral Collapse

**Tier:** 2 (Structural Inference)
**Phase:** AX_CLASS_BEHAVIOR
**Scope:** Currier B grammar / AX class structure
**Status:** VALIDATED (re-verified 2026-01-26 with 19 AX classes)

> **CORRECTED 2026-01-26:** AX is 19 classes, not 20. Class 14 removed — confirmed FQ per ICC + behavioral evidence (suffix rate 0.0, 707 tokens; see C583). All statistics below re-verified with 19 classes. Verdict: STRENGTHENED (structured transitions 3/20→0/19, silhouette 0.18→0.43, separation ratio 1.17→1.90).

## Claim

The 19 AX instruction classes do not form behaviorally distinct groups. Position is the only significant differentiator, while transitions are uniform (0/19 structured), context provides no classification signal (9.8% vs 11.1% baseline), and clustering yields k=2 with silhouette=0.43. The 19 classes reflect PREFIX morphological diversity, not functional behavioral diversity. Within positional subgroups (INIT/MED/FINAL), classes are largely interchangeable.

## Evidence

### 1. Positional Profiles (Script 2)

- **9/19 classes** have positional distributions significantly different from the AX population (KS test, Bonferroni-corrected)
- **67/171 pairwise** comparisons are Bonferroni-distinct
- Position is the strongest available signal but still only separates half the classes
- Class 22 has the largest deviation: D=0.506 vs population

### 2. Transition Structure (Script 1)

- **0/19 classes** show structured transitions (chi-squared p<0.01)
- All 19 classes are indistinguishable from uniform random transitions
- Self-chain rates are low across all classes (consistent with AX not self-sequencing)
- Transition entropy is near-uniform, confirming lack of class-specific sequencing rules

### 3. Context Signatures (Script 3)

- **Nearest-centroid classification:** 9.8% overall accuracy
- **Weighted random baseline:** 11.1%
- **Lift over baseline:** 0.88x (worse than random)
- Context provides NO classification signal -- knowing what surrounds an AX token does not reveal which class it is
- **Class 22 exception:** 60% accuracy (next best: 33%)
- Most classes: 0-13% accuracy (effectively random)

### 4. Synthesis (Script 4)

Combined 36-dimensional feature matrix (3 transition + 10 positional + 12 context + 4 regime + 4 section + 3 morphological):

- **Clustering:** Best k=2, silhouette=0.4319 (the 2-cluster structure reflects the INIT/FINAL positional split — cleaner without Class 14 outlier)
- **PCA:** 4 components required for 90% variance (more concentrated than prior 7-component result)
- **Confusability:** Separation ratio=1.897x (mean inter-subgroup 0.57, mean intra-subgroup 0.30)
- **Most confusable pair:** Classes 28/29 (distance=2.57, both AX_MED)
- **Most distinct pair:** Classes 16/22 (distance=11.50, AX_MED vs AX_FINAL)

### 5. Class 22 Outlier

Class 22 is the sole exception to behavioral collapse:
- Positional D=0.506 (strongest of all 19)
- Context accuracy: 60% (9x above overall average)
- Consistently separates in clustering (always in its own cluster)
- Class 22 = AX_FINAL; its distinctiveness may reflect the FINAL position role itself rather than a unique class identity

## Key Numbers

| Metric | Value |
|--------|-------|
| AX tokens analyzed | 3,852 |
| Classes tested | 19 |
| Positional: Bonferroni-distinct classes | 9/19 |
| Positional: distinct pairs | 67/171 |
| Transitions: structured classes | 0/19 |
| Context: classification accuracy | 9.8% |
| Context: weighted random baseline | 11.1% |
| Clustering: best k | 2 |
| Clustering: best silhouette | 0.4319 |
| PCA: components for 90% | 4 |
| Subgroup separation ratio | 1.897x |
| Class 22 positional D | 0.506 |
| Class 22 context accuracy | 60% |

## Interpretation

The 19 AX classes are an artifact of PREFIX combinatorics, not functional specialization. The morphological system generates 19 distinct forms, but these forms do not map to 19 distinct behaviors. The effective behavioral resolution is:

1. **3 positional subgroups** (INIT / MED / FINAL) -- already captured by C563-C566
2. **Class 22 as outlier** -- possibly reflecting FINAL-position extremity
3. **Everything else** -- interchangeable within subgroup

This confirms C571's prediction: PREFIX selects role (scaffold vs operational), and within the scaffold role, the specific PREFIX combination is behaviorally irrelevant.

## Supports

- **C563:** AX positional stratification (the 3-way split is the real structure)
- **C571:** AX functional identity resolution (PREFIX is role selector, not behavior selector)

## Dependencies

- C563-C566: AUXILIARY_STRATIFICATION (positional sub-structure)
- C567-C571: AX_FUNCTIONAL_ANATOMY (functional identity)
- CLASS_COSURVIVAL_TEST: class token mapping
- CLASS_SEMANTIC_VALIDATION: role taxonomy
