# C563: AUXILIARY Internal Positional Stratification

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** AUXILIARY_STRATIFICATION
**Status:** VALIDATED

## Claim

The 20 AUXILIARY classes are internally stratified into three positional sub-groups that form a directional scaffold within lines.

## Evidence

### Sub-Group Membership

| Sub-Group | Classes | Tokens | % of AX | Mean Position | Key Rate |
|-----------|---------|--------|---------|---------------|----------|
| AX_INIT | 4, 5, 6, 24, 26 | 1195 | 26.2% | 0.419 | 25.4% initial |
| AX_MED | 1, 2, 3, 14, 16, 18, 27, 28, 29 | 2763 | 60.6% | 0.514 | neutral |
| AX_FINAL | 15, 19, 20, 21, 22, 25 | 601 | 13.2% | 0.660 | 34.6% final |

### Statistical Validation

- Kruskal-Wallis H = 213.9, p = 3.60e-47 (3 subgroups differ in position)
- Cohen's d = 0.69 (INIT vs FINAL, medium-large effect)
- Mann-Whitney pairwise: all p < 1e-16

### Directional Ordering

- 71.8% of INIT-FINAL co-occurring pairs show INIT before FINAL
- n = 369 pairs, strongly non-random
- AX subgroup bigram flow: INIT -> MED (418) > MED -> INIT (323)
- MED -> FINAL (243) > FINAL -> MED (161)

### Not Explained by Clustering

- Distributional clustering gives weak silhouette (0.232 at k=2)
- The POSITIONAL gradient is the primary structural signal
- AX is not well-separated into clusters; it's a GRADIENT

## Interpretation

AUXILIARY is not a "heterogeneous residual" (contra Q6 from CLASS_SEMANTIC_VALIDATION). It is a positionally stratified execution scaffold:

- **AX_INIT**: Frame openers (structural setup, not ENERGY triggers)
- **AX_MED**: Scaffold (neutral infrastructure filler)
- **AX_FINAL**: Frame closers (structural closure, not flow redirection)

The sub-roles mirror the named role positions (CC -> INIT, EN -> MED, FL -> FINAL) but provide STRUCTURAL framing rather than FUNCTIONAL operations.

## Cross-References

- C121: 49-class grammar (AX is 20 of 49 classes)
- C411: AX internal redundancy (97.4% co-occurrence)
- C556: ENERGY medial concentration (AX_MED parallels EN medial)
- C557: daiin line-initial (AX_INIT parallels CC initial)
- C562: FLOW final hierarchy (AX_FINAL parallels FL final)
- C550: Role transition grammar (AX sub-roles fit the CC -> EN -> FL flow)
