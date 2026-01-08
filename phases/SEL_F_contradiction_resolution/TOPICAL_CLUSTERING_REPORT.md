# SEL-F: Topical Clustering & Terminal State Distribution Analysis

**Phase:** SEL-F (Self-Evaluation - Contradiction Resolution)
**Date:** 2026-01-07
**Status:** COMPLETE

---

## Executive Summary

| Hypothesis | Result | Tier |
|------------|--------|------|
| **Procedural Chaining** | FALSIFIED | Tier 1 |
| **Sharp Material-Family Clustering** | NOT SUPPORTED (silhouette 0.018) | — |
| **Material-Conditioned Folio Grouping** | PARTIALLY SUPPORTED | Tier 2 hypothesis |
| **STATE-C as Pause/Checkpoint** | SUPPORTED | Tier 2 |
| **Completion Gradient** | SUPPORTED | Tier 2 |
| **Restart Folios as Boundaries** | INCONCLUSIVE (1/3 only) | Tier 3 hypothesis |

---

## Background

SEL-F Part 1 resolved the MONOSTATE vs 2-cycle contradiction and discovered that only **57.8%** of folios terminate in STATE-C (not 100% as previously claimed). This raised the question: what explains the 42.2% that don't?

Three hypotheses were tested:
1. **Procedural Chaining**: Non-STATE-C folios chain together in sequences
2. **Sharp Material Clustering**: Folios partition cleanly into material families
3. **Soft Material Conditioning**: Folios show overlapping, contextual material grouping

---

## Tests Conducted

### TEST 9: Cluster Detection via Vocabulary

Hierarchical clustering of folios by vocabulary Jaccard similarity.

| k | Silhouette | Within-Cluster J | Between-Cluster J |
|---|------------|------------------|-------------------|
| 3 | 0.0148 | 0.118 | 0.094 |
| **4** | **0.0179** | 0.130 | 0.092 |
| 5 | 0.0178 | 0.136 | 0.093 |

**Result:** Best k=4, but silhouette score is **VERY WEAK** (0.018).

**Interpretation:** Clusters exist statistically, but the embedding space is highly overlapping. This is consistent with:
- Shared vocabularies across procedures
- Multiple workflows touching same materials
- Registry reuse without strict partitioning

**This does NOT support a clean material-family taxonomy.** It suggests soft, contextual grouping.

---

### TEST 10: A-Section Material Families

Do folios within clusters share more A-section vocabulary?

| Metric | Within-Cluster | Between-Cluster | Ratio |
|--------|---------------|-----------------|-------|
| A-reference Jaccard | 0.2054 | 0.1571 | **1.31x** |

**Mann-Whitney U test:** p < 0.000001 (**HIGHLY SIGNIFICANT**)

**Result:** SUPPORTED - Folios within clusters share significantly more A-section vocabulary.

**Interpretation:** Material conditioning is real and non-random. Adjacent folios tend to reference similar Currier A entries. But the weak clustering (TEST 9) means this is overlapping and contextual, not a strict hierarchy.

---

### TEST 11: STATE-C as Cluster Boundary Marker

Do STATE-C folios mark transitions between clusters?

| Location | STATE-C | Other |
|----------|---------|-------|
| At boundaries | 11 | 9 |
| Internal | 36 | 26 |

**Chi-square test:** p = 1.0 (NOT SIGNIFICANT)

**Result:** FALSIFIED - STATE-C is NOT associated with cluster boundaries.

**Interpretation:** STATE-C represents a pause/checkpoint state, not a material-family transition marker. Procedures can end at STATE-C regardless of material grouping.

---

### TEST 12: f82v Anomaly Analysis

The f80-f84 neighborhood shows 90% STATE-C (vs 58% corpus average).

| Folio | Terminal | Kernel | KCR | Reset? |
|-------|----------|--------|-----|--------|
| f80r | STATE-C | k | 0.653 | |
| f80v | STATE-C | k | 0.639 | |
| f81r | STATE-C | k | 0.692 | |
| f81v | STATE-C | k | 0.641 | |
| f82r | STATE-C | k | 0.652 | |
| f82v | initial | k | 0.686 | **RESET** |
| f83r | STATE-C | k | 0.647 | |
| f83v | STATE-C | k | 0.796 | |
| f84r | STATE-C | k | 0.658 | |
| f84v | STATE-C | k | 0.668 | |

**Vocabulary coherence:** 89th percentile (higher than 89% of random windows)

**Result:** This zone is anomalously coherent and complete. Cluster 3 (f75-f84) is the ONLY physically contiguous cluster.

**Interpretation:** This is a local observation, not a general organizational law. The f75-f84 region may represent a compiled or refined section, but this cannot be generalized to the whole manuscript.

---

### TEST 13: Restart Folios as Cluster Initiators

| Restart | Position | Cluster | Starts New Cluster? |
|---------|----------|---------|---------------------|
| f50v | 44 (53%) | 2 | NO |
| f57r | 47 (57%) | 1 | YES |
| f82v | 65 (78%) | 3 | NO |

**Result:** Only 1/3 restart folios marks a cluster boundary.

**Interpretation:** INCONCLUSIVE. Restart folios are **hypothesized transition points**, not proven material boundaries. The evidence does not support using them as reliable organizational markers.

---

### Gradient Hypothesis Tests

#### Position vs Metrics (Spearman Correlation)

| Metric | rho | p-value | Direction |
|--------|-----|---------|-----------|
| STATE-C | +0.24 | 0.031* | Later → MORE complete |
| Vocab size | -0.44 | <0.001* | Later → SMALLER |
| A-ref count | -0.41 | <0.001* | Later → FEWER |
| A-ref density | +0.31 | 0.004* | Later → HIGHER proportion |
| Token count | -0.27 | 0.015* | Later → SHORTER |
| Kernel contact | +0.09 | 0.40 | No trend |

**Result:** COMPLETION GRADIENT CONFIRMED

Later folios are MORE COMPLETE but LESS COMPLEX - they do LESS with HIGHER completion rate.

---

#### Section-Level Analysis

| Section | Folios | STATE-C % |
|---------|--------|-----------|
| H | 32 | 50% |
| S | 23 | 48% |
| **B** | **20** | **70%** |
| **C** | **6** | **100%** |
| T | 2 | 50% |

**Result:** STATE-C is SECTION-DEPENDENT. Sections B and C have dramatically higher completion rates than H and S.

---

## Consolidated Interpretation

### What the Data Shows

1. **Clustering is Weak, Conditioning is Real**
   - Silhouette = 0.018 means clusters are highly overlapping
   - But A-reference sharing IS significant (1.31x, p < 0.000001)
   - This is consistent with soft, contextual material grouping

2. **STATE-C is a Checkpoint, Not a Boundary**
   - 42% of folios don't terminate in STATE-C
   - This is concentrated in sections H/S and earlier positions
   - STATE-C does NOT mark material-family transitions

3. **Completion is Structured**
   - Position gradient: later = more complete
   - Section effect: B/C > H/S
   - This is patterned, not random

4. **Cluster 3 is Anomalous**
   - Only physically contiguous cluster
   - Highest coherence and completion
   - This is a local observation, not a general principle

### What This Does NOT Support

- Clean material-family partitioning
- Restart folios as reliable boundary markers
- STATE-C as organizational signal
- Any strict hierarchical taxonomy

### What This DOES Support (Tier 2)

- Material conditioning exists but is soft and overlapping
- Currier A functions as a material identity index
- Completion behavior is structured by section and position
- The 42% non-STATE-C is patterned, not random

---

## Compatibility with Later Work

This analysis is **fully compatible** with subsequent AZC/axis findings:

- Diagram-anchored workflows (AZC-AXIS)
- Season-gated availability (AZC-AXIS)
- Position-dependent affordances (AZC-PLACEMENT)

A strict material-family library would have conflicted with these. A soft, contextual pattern integrates cleanly.

---

## Constraint Assignments (Tier 2 Structural Inferences)

### Constraint 323
**Terminal state distribution:** 57.8% STATE-C, 38.6% "other" (transitional), 3.6% "initial" (reset). The 42% non-STATE-C is concentrated in sections H/S and earlier positions.

### Constraint 324
**Terminal state is section-dependent:** Sections H/S ~50% STATE-C, Sections B/C 70-100% STATE-C.

### Constraint 325
**Completion gradient exists:** STATE-C increases with position (rho=+0.24, p=0.03); vocabulary decreases (rho=-0.44); A-ref density increases (rho=+0.31).

### Constraint 326
**A-reference sharing within clusters:** Within-cluster overlap 0.205, between-cluster 0.157; enrichment 1.31x (p<0.000001). Material conditioning is real but overlapping.

### Constraint 327
**Cluster 3 (f75-f84) is locally anomalous:** Physically contiguous, 70% STATE-C, highest A-ref coherence (0.294). This is a local observation, not an organizational law.

---

## Falsifications (Tier 1)

| Hypothesis | Evidence |
|------------|----------|
| Procedural chaining | Tests 1-6: no sequential state matching, no token overlap enrichment |
| STATE-C marks cluster boundaries | TEST 11: p = 1.0 |
| Sharp material-family clustering | TEST 9: silhouette = 0.018 |

---

## Hypotheses Requiring Further Testing (Tier 3)

| Hypothesis | Current Status |
|------------|----------------|
| Restart folios as material boundaries | 1/3 supported (inconclusive) |
| Cluster 3 represents compiled/refined section | Plausible but not tested |

---

## Files Created

| File | Purpose |
|------|---------|
| `topical_clustering_hypothesis.py` | Tests 9-13 implementation |
| `clustering_deep_analysis.py` | Cluster profile analysis |
| `gradient_hypothesis_test.py` | Position gradient tests |
| `clustering_results.json` | Cluster assignments |
| `TOPICAL_CLUSTERING_REPORT.md` | This document |

---

## Summary

**The material-conditioned folio grouping pattern is a strong candidate organizational pattern, not a proven organizational principle.**

The evidence supports:
- Soft, overlapping material conditioning (Tier 2)
- Structured completion behavior (Tier 2)
- STATE-C as pause/checkpoint (Tier 2)

The evidence does NOT support:
- Sharp material-family taxonomy
- Restart folios as universal boundary markers
- STATE-C as organizational signal

This integrates cleanly with AZC/axis findings and maintains strict tier discipline.

---

*SEL-F TOPICAL CLUSTERING ANALYSIS COMPLETE*
*Revised: 2026-01-07*
