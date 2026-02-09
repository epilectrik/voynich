# A_PP_INTERNAL_STRUCTURE Phase

**Date:** 2026-01-30 (extended 2026-01-31)
**Status:** COMPLETE (5 tests, STRONG verdict)
**Tier:** 2 (Structural)
**Prerequisite:** A_PP_PROCEDURAL_MODES (WEAK - established PP is continuous, not modal)

---

## Results Summary

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Positional Preferences | **CONFIRMED** | 50% of MIDDLEs have position bias, KS p<0.0001 |
| 2. Network Topology | **CONFIRMED** | Hub structure (CV=1.69), top hub: iin (degree 277) |
| 4. WITH-RI vs WITHOUT-RI | **SUPPORT** | Jaccard=0.232 (low overlap), sample imbalanced |
| 6. Gradient Analysis | **NOT SUPPORTED** | Primary axis is DIVERSITY vs CLOSURE, not section |
| 7. A-B Positional Mapping | **CONFIRMED** | A position correlates with B position (r=0.654, p<0.0001) |

**Overall: STRONG** (3 confirmed, 1 support, 1 not supported)

**Key Insights:**

1. **PP has internal positional structure** (C898) that C234's aggregate finding obscured:
   - LATE-biased MIDDLEs: m (0.85), am (0.79), d (0.75), dy (0.73) - closure markers
   - EARLY-biased MIDDLEs: or (0.35) - opening marker
   - Network hubs: iin, ol, s, or, y (scale-free topology)

2. **A's positional order reflects B's procedural order** (C899):
   - Linear correlation r=0.654 (p<0.0001) between A and B positions
   - 92.5% zone preservation (vs 33% by chance)
   - All 5 hubs maintain MIDDLE zone in both systems
   - Reading A left-to-right predicts B execution sequence

**Constraints: C898 (A PP Internal Structure), C899 (A-B Positional Correspondence)**

---

## Objective

Investigate the internal structure of Currier A PP (procedural payload) vocabulary using gradient, network, and positional analysis - avoiding the clustering approach that failed in the previous phase.

**Key insight from A_PP_PROCEDURAL_MODES:**
PP varies continuously, not in discrete modes. Section (H vs P) is the dominant factor. Material class mixing persists (C642 compatible).

**This phase explores:**
1. PP positional grammar within A lines
2. PP co-occurrence network topology and B-survival correlation
3. WITH-RI vs WITHOUT-RI PP functional divergence

---

## Research Questions

1. **Positional Grammar:** Do PP tokens have consistent positional preferences within A lines, or is position truly free (C234)?

2. **Network Hubs:** Which PP tokens are network hubs in the co-occurrence graph, and does centrality predict B-side effects?

3. **RI Context:** Does PP serve different functions in lines with RI vs pure-PP lines?

---

## Test Design

### Test 1: PP Positional Preferences

**Question:** Do PP MIDDLEs have consistent within-line positional preferences?

**Method:**
1. Extract all PP tokens with normalized within-line positions (0=first, 1=last)
2. For each PP MIDDLE with n≥30, compute mean position
3. Test against uniform distribution (Kolmogorov-Smirnov)
4. Identify EARLY-biased, LATE-biased, and POSITION-FREE PP types

**Expected:** If PP has positional grammar, certain MIDDLEs should show significant position bias.

---

### Test 2: PP Co-occurrence Network Topology

**Question:** What is the structure of PP co-occurrence, and which PP are hubs?

**Method:**
1. Build PP co-occurrence graph (edges = same-line co-occurrence, weighted by frequency)
2. Compute centrality metrics (degree, betweenness, eigenvector)
3. Identify hub PP (high degree), bridge PP (high betweenness), peripheral PP
4. Test if hub status correlates with B survival contribution

**Expected:** Hub PP should overlap with C517's superstring hinge letters.

---

### Test 3: PP Network Modularity

**Question:** Does the PP co-occurrence graph have modular structure?

**Method:**
1. Apply community detection (Louvain algorithm)
2. Characterize communities by PREFIX composition
3. Test if communities align with known functional categories

**Expected:** Communities may reflect C475 incompatibility structure.

---

### Test 4: WITH-RI vs WITHOUT-RI PP Comparison

**Question:** Does PP vocabulary differ between lines with RI and pure-PP lines?

**Method:**
1. Partition A lines into WITH-RI and WITHOUT-RI
2. Compare PP vocabulary (Jaccard similarity, type counts)
3. Compare PP positional distributions
4. Test PREFIX profile differences

**Expected:** C888 suggests WITHOUT-RI lines are cross-reference heavy (ct-enriched in H).

---

### Test 5: PP-RI Positional Interaction

**Question:** In WITH-RI lines, does PP position depend on RI position?

**Method:**
1. For lines with both RI and PP, compute relative positions
2. Test if PP tends to appear before/after RI tokens
3. Check if PP type varies by position relative to RI

**Expected:** May reveal PP-RI compositional grammar.

---

### Test 6: PP Gradient Analysis

**Question:** What continuous gradients describe PP variation across folios?

**Method:**
1. Build folio-level PP feature vectors (PREFIX rates, MIDDLE diversity, etc.)
2. Apply PCA to identify principal gradients
3. Correlate gradients with known folio characteristics (section, paragraph count)
4. Avoid clustering - characterize the gradient structure

**Expected:** Section should be the dominant gradient (confirming A_PP_PROCEDURAL_MODES).

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | 4+ tests reveal significant structure; positional grammar confirmed |
| MODERATE | 2-3 tests significant; some internal organization |
| WEAK | 1 test significant; PP is largely unstructured |
| NEGATIVE | No significant patterns; C234 position-freedom confirmed |

---

## Constraints to Reference

| Constraint | Relevance |
|------------|-----------|
| C234 | A tokens are position-free (aggregate) - test if PP specifically is |
| C475 | MIDDLE incompatibility layer - governs co-occurrence |
| C506 | PP count → class survival (r=0.715) |
| C517 | Superstring compression, hinge letters |
| C728 | PP co-occurrence non-random, explained by C475 |
| C730 | Within-line PREFIX-MIDDLE coupling (MI 0.133) |
| C830 | Repetition is FINAL-biased (0.675 mean position) |
| C887 | WITHOUT-RI backward reference asymmetry |
| C888 | Section-specific WITHOUT-RI function |
| C889 | ct-ho reserved vocabulary |

---

## Files

```
phases/A_PP_INTERNAL_STRUCTURE/
├── README.md (this file)
├── scripts/
│   ├── 01_pp_positional_preferences.py
│   ├── 02_pp_network_topology.py
│   ├── 03_pp_network_modularity.py
│   ├── 04_with_without_ri_comparison.py
│   ├── 05_pp_ri_positional_interaction.py
│   ├── 06_pp_gradient_analysis.py
│   └── 07_integrated_verdict.py
└── results/
    └── *.json
```
