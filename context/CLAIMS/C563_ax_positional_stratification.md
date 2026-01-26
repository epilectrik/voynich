# C563: AUXILIARY Internal Positional Stratification

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** AUXILIARY_STRATIFICATION
**Status:** VALIDATED (CORRECTED 2026-01-26)

> **CORRECTED 2026-01-26:** Class 14 removed from AX_MED. Class 14 is FQ per ICC phase20a (FREQUENT_OPERATOR), confirmed by: suffix rate = 0.0 (vs AX_MED 0.56–1.0), token count = 707 (vs AX_MED 38–212), morphological match with FQ Class 13 (ok/ot-prefixed), JS divergence 0.0018 with Class 13. Root cause: ax_census_reconciliation.py used ICC_FQ = {9, 13, 23} without Class 14, causing it to default into AX by set subtraction. AX classes: 20 → 19. See C583 (FQ Definitive Census).

## Claim

The 19 AUXILIARY classes are internally stratified into three positional sub-groups that form a directional scaffold within lines.

## Evidence

### Sub-Group Membership

| Sub-Group | Classes | Tokens | % of AX | Mean Position | Key Rate |
|-----------|---------|--------|---------|---------------|----------|
| AX_INIT | 4, 5, 6, 24, 26 | 1195 | 31.0% | 0.419 | 25.4% initial |
| AX_MED | 1, 2, 3, 16, 18, 27, 28, 29 | 2056 | 53.4% | 0.480 | neutral |
| AX_FINAL | 15, 19, 20, 21, 22, 25 | 601 | 15.6% | 0.660 | 34.6% final |

### Statistical Validation (re-verified 2026-01-26 with 19 classes)

- Kruskal-Wallis H = 208.8, p = 4.64e-46 (3 subgroups differ in position)
- Cohen's d = 0.69 (INIT vs FINAL, medium-large effect)
- Mann-Whitney pairwise: INIT-MED p=2.5e-07, INIT-FINAL p=2.6e-42, MED-FINAL p=1.5e-33

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

- C121: 49-class grammar (AX is 19 of 49 classes)
- C411: AX internal redundancy (97.4% co-occurrence)
- C556: ENERGY medial concentration (AX_MED parallels EN medial)
- C557: daiin line-initial (AX_INIT parallels CC initial)
- C562: FLOW final hierarchy (AX_FINAL parallels FL final)
- C550: Role transition grammar (AX sub-roles fit the CC -> EN -> FL flow)
