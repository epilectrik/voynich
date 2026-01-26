# C572: AX Class Behavioral Collapse

**Tier:** 2 (Structural Inference)
**Phase:** AX_CLASS_BEHAVIOR
**Scope:** Currier B grammar / AX class structure

## Claim

The 20 AX instruction classes do not form behaviorally distinct groups. Position is the only significant differentiator (10/20 classes distinct), while transitions are uniform (3/20 structured), context provides no classification signal (6.8% vs 10.3% baseline), and clustering yields k=2 with silhouette=0.18. The 20 classes reflect PREFIX morphological diversity, not functional behavioral diversity. Within positional subgroups (INIT/MED/FINAL), classes are largely interchangeable.

## Evidence

### 1. Positional Profiles (Script 2)

- **10/20 classes** have positional distributions significantly different from the AX population (KS test, Bonferroni-corrected at alpha/20 = 0.0025)
- **65/190 pairwise** comparisons are Bonferroni-distinct (Bonferroni threshold = 5.263e-05)
- 12/20 distinct at raw alpha=0.05 (before correction)
- Position is the strongest available signal but still only separates half the classes
- Class 22 has the largest deviation: D=0.506 vs population

### 2. Transition Structure (Script 1)

- **3/20 classes** show structured transitions (chi-squared p<0.01)
- Remaining 17/20 are indistinguishable from uniform random transitions
- Self-chain rates are low across all classes (consistent with AX not self-sequencing)
- Transition entropy is near-uniform, confirming lack of class-specific sequencing rules

### 3. Context Signatures (Script 3)

- **Nearest-centroid classification:** 6.8% overall accuracy
- **Weighted random baseline:** 10.3%
- **Lift over baseline:** 0.66x (worse than random)
- Context provides NO classification signal -- knowing what surrounds an AX token does not reveal which class it is
- **Class 22 exception:** 60% accuracy (next best: 33%)
- Most classes: 0-13% accuracy (effectively random)

### 4. Synthesis (Script 4)

Combined 36-dimensional feature matrix (3 transition + 10 positional + 12 context + 4 regime + 4 section + 3 morphological):

- **Clustering:** Best k=2, silhouette=0.1805 (prior 5-role silhouette was 0.2317 -- adding dimensions made it worse)
- **PCA:** 7 components required for 90% variance (diffuse, no dominant axis)
- **Confusability:** Inter-subgroup mean distance 7.40, intra-subgroup 6.34, separation ratio=1.168x (barely above 1.0)
- **Most confusable pair:** Classes 28/29 (distance=2.57, both AX_MED)
- **Most distinct pair:** Classes 16/22 (distance=11.50, AX_MED vs AX_FINAL)

### 5. Class 22 Outlier

Class 22 is the sole exception to behavioral collapse:
- Positional D=0.506 (strongest of all 20)
- Context accuracy: 60% (9x above overall average)
- Consistently separates in clustering (always in its own cluster)
- Class 22 = AX_FINAL; its distinctiveness may reflect the FINAL position role itself rather than a unique class identity

## Key Numbers

| Metric | Value |
|--------|-------|
| AX tokens analyzed | 4,559 |
| Classes tested | 20 |
| Positional: Bonferroni-distinct classes | 10/20 |
| Positional: distinct pairs | 65/190 |
| Transitions: structured classes | 3/20 |
| Context: classification accuracy | 6.8% |
| Context: weighted random baseline | 10.3% |
| Clustering: best k | 2 |
| Clustering: best silhouette | 0.1805 |
| Prior silhouette (5-role) | 0.2317 |
| PCA: components for 90% | 7 (of 10 non-zero) |
| Subgroup separation ratio | 1.168x |
| Class 22 positional D | 0.506 |
| Class 22 context accuracy | 60% |

## Interpretation

The 20 AX classes are an artifact of PREFIX combinatorics, not functional specialization. The morphological system generates 20 distinct forms, but these forms do not map to 20 distinct behaviors. The effective behavioral resolution is:

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
