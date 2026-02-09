# A_PP_PROCEDURAL_MODES Phase

**Date:** 2026-01-30
**Status:** COMPLETE (5 tests, WEAK verdict)
**Tier:** 3 (Interpretation only - insufficient structural support)
**Prerequisite:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (STRONG verdict)

---

## Objective

Investigate whether Currier A folios cluster into distinct **procedural modes** based on PP vocabulary composition, and characterize what distinguishes these modes operationally.

**Framing (per expert validation):**
- NOT "material-specific sensory criteria" (conflicts with C642's material-mixing finding)
- YES "procedural modes reflecting different operational requirements"

**Preliminary finding (from exploratory analysis):**
Section H A folios cluster into 3 groups by PP role composition:
- Cluster 1 (42 folios): HIGH CLOSURE (19%), HIGH ESCAPE (15%) - Output+hazard procedures
- Cluster 2 (20 folios): HIGH CORE (55%), LOW WITH-RI (40%) - Pure processing procedures
- Cluster 3 (33 folios): HIGH CROSS-REF (8.5%) - Cross-referencing procedures

---

## Research Questions

1. **Cluster Validity:** Do the 3 clusters represent genuine structural separation, or are they artifacts of continuous variation?

2. **B-Side Correlation:** Do A folio procedural modes predict anything about corresponding B execution patterns?

3. **Vocabulary Discrimination:** Do clusters have genuinely distinctive MIDDLE inventories, or is overlap dominant?

4. **Section Generalization:** Do P and T sections show analogous clustering, or is this H-specific?

5. **C642 Compatibility:** How do procedural mode clusters relate to material class mixing?

6. **Operational Interpretation:** Can clusters be mapped to Brunschwig procedural categories?

---

## Results Summary

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Cluster Validity | **NOT SUPPORTED** | k=2 optimal (not k=3), silhouette=0.185 (weak) |
| 2. B-Side Correlation | **NOT SUPPORTED** | No direct A-B folio matches available |
| 3. Vocabulary Discrimination | **SUPPORT** | p=0.057 (borderline), 48 exclusive MIDDLEs |
| 4. Section Generalization | **PARTIAL** | Clusters are section-confounded (p=0.019) |
| 5. Material Class Compatibility | **CONFIRMED** | 93-98% heterogeneity (C642 compatible) |

**Overall: WEAK** (1 confirmed, 2 support/partial, 2 not supported)

**Key Insight:** The preliminary 3-cluster finding does not survive validation:
- Silhouette analysis shows k=2 is optimal, and even that is weak (0.286)
- Data appears continuous rather than discretely clustered
- Clusters are confounded with section (H vs P)
- BUT: C642 compatibility is confirmed - whatever variation exists in A PP, it does NOT correlate with material identity

**No constraint recommended** - insufficient structural support for discrete procedural modes.

---

## Test Design

### Test 1: Cluster Validity (Silhouette Analysis)

**Question:** Are 3 clusters optimal, or is the data continuous?

**Method:**
1. Compute silhouette scores for k=2,3,4,5 clusters
2. Test cluster stability via bootstrap resampling
3. Perform gap statistic analysis
4. Visualize cluster separation via PCA

**Expected:** Silhouette > 0.3 indicates meaningful cluster structure.

---

### Test 2: B-Side Execution Correlation

**Question:** Do A procedural modes predict B execution characteristics?

**Method:**
1. Map each A folio to corresponding B folios (same section)
2. Compute B characteristics: FQ rate, LINK rate, kernel ratios (k/h/e)
3. Test if A cluster membership predicts B characteristics
4. Control for section confound

**Expected:** If procedural modes have operational meaning, B-side patterns should differ.

---

### Test 3: Vocabulary Discrimination Analysis

**Question:** How distinctive are cluster MIDDLE inventories?

**Method:**
1. Compute Jaccard similarity between cluster MIDDLE sets
2. Identify MIDDLEs that are cluster-exclusive (appear in only 1 cluster)
3. Compute enrichment ratios for shared MIDDLEs
4. Test significance via permutation (shuffle cluster labels)

**Expected:** Significant vocabulary discrimination (p<0.05) supports genuine modes.

---

### Test 4: Section Generalization

**Question:** Do P and T sections show analogous procedural mode clustering?

**Method:**
1. Apply same clustering method to Section P folios
2. Compare cluster profiles (role composition)
3. Test if P clusters mirror H cluster characteristics

**Expected:** Similar clustering would suggest universal procedural organization.

---

### Test 5: Material Class Compatibility (C642 Check)

**Question:** How do procedural modes relate to material class mixing?

**Method:**
1. For each cluster, compute material class heterogeneity rate
2. Test if procedural mode predicts material mixing behavior
3. Verify C642's finding holds within each cluster

**Expected:** Material mixing should persist across all clusters (C642 compatibility).

---

### Test 6: PREFIX-MIDDLE Co-occurrence by Cluster

**Question:** Do clusters show different PREFIX-MIDDLE coupling patterns?

**Method:**
1. Build PREFIX-MIDDLE co-occurrence matrix per cluster
2. Compare Cramer's V (association strength) across clusters
3. Identify cluster-specific PREFIX-MIDDLE pairings

**Expected:** Different coupling patterns would indicate different procedural grammars.

---

### Test 7: Paragraph Structure by Cluster

**Question:** Do clusters differ in paragraph-level organization?

**Method:**
1. Compare WITH-RI / WITHOUT-RI ratios per cluster
2. Compare paragraph length distributions
3. Test positional patterns (where do cluster-distinctive MIDDLEs appear?)

**Expected:** Paragraph structure differences would support procedural mode interpretation.

---

### Test 8: Brunschwig Operation Mapping

**Question:** Can clusters be mapped to Brunschwig procedural categories?

**Method:**
1. From BRSC: identify operation categories (preparation, distillation, recovery, finishing)
2. Map A PP role profiles to these categories
3. Test if cluster assignments align with Brunschwig workflow stages

**Expected:** Alignment would validate procedural mode interpretation.

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | 6+ tests significant; clusters validated; B-side correlation found |
| MODERATE | 4-5 tests significant; clusters valid but no B-side correlation |
| WEAK | 2-3 tests significant; cluster validity questionable |
| NEGATIVE | Clusters are artifacts of continuous variation |

---

## Constraints to Reference

| Constraint | Relevance |
|------------|-----------|
| C642 | Material class mixing - procedural modes must be compatible |
| C737 | Alternative clustering (B-coverage profiles) - compare dimensions |
| C888 | Section-level differences - this extends to within-section |
| C849 | Paragraph section profiles - relates to WITH-RI patterns |
| C893 | Paragraph kernel signatures - B-side paragraph types |

---

## Files

```
phases/A_PP_PROCEDURAL_MODES/
├── README.md (this file)
├── scripts/
│   ├── 01_cluster_validity.py
│   ├── 02_b_side_correlation.py
│   ├── 03_vocabulary_discrimination.py
│   ├── 04_section_generalization.py
│   ├── 05_material_class_compatibility.py
│   ├── 06_prefix_middle_cooccurrence.py
│   ├── 07_paragraph_structure.py
│   ├── 08_brunschwig_mapping.py
│   └── 09_integrated_verdict.py
└── results/
    └── *.json
```
