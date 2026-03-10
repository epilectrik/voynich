# Phase 573: A2 Forgivingness Mechanism + Apparatus Family Partition

**Mechanism verdict: A2_MECHANISM_IDENTIFIED_STRONG**
**Family verdict: FAMILY_PARTITION_INCONCLUSIVE**
**Within-A2 verdict: A2_WEAKLY_STRUCTURED**
**Grammar pattern: GRAMMAR_PATTERN_STRENGTH_DEPENDENT**
**New constraints:** 4 (C1639-C1642)

---

## 1. Summary

Phase 573 investigates the mechanism behind A2_SEALED_RECIRCULATION's elevated Forgivingness Index (FI = CCS1), which Phase 572 measured as 9x higher than A1. Using counterfactual ablation across 5 physics channels on 76 eligible Currier B folios, the phase identifies which channels cause A2's excess forgivingness and tests whether the 76-folio set partitions into natural apparatus-response families.

## 2. Mechanism Ablation (T1)

**Verdict: A2_MECHANISM_IDENTIFIED_STRONG**

Single ablation NO_CLOSE_RECOVERY accounts for 159.5% of A2 excess CCS1

### Ablation Shares by Profile

| Profile | CCS1 (FI) | CRR_M4f | NRI_M4f | CROSS_COUPLING | CLOSE_RECOVERY | CONTAINMENT | TR_TO_Y | Y_SENSITIVITY |
|---|---|---|---|---|---|---|---|---|
| A1_BATH_REFLUX | 0.0131 | 0.4138 | 0.0115 | +38.8% | +91.8% | +34.1% | +18.7% | -3.1% |
| A2_SEALED_RECIRCULATION | 0.1140 | 0.3888 | 0.0541 | -57.0% | +159.5% | +116.0% | -49.2% | +1.7% |
| A3_DISTILL_COLLECT | 0.0796 | 0.3079 | 0.0571 | +38.8% | +91.8% | +34.1% | +18.7% | -3.1% |

## 3. Grammar-Strength Forgivingness (T2)

**Pattern: GRAMMAR_PATTERN_STRENGTH_DEPENDENT**

A2 grammar advantage varies by strength: STRONG adv=+0.0209 (n=11), WEAK adv=-0.0140 (n=40). Range=0.0349, CCS1=0.1208. Only strong-grammar events reliably beat the forgiving null. Weak events lose the null.

### M1 DYE by Grammar Strength Band (A2, overall CCS1=0.1208)

| Band | N_m1 | M1_DYE | Adv vs CCS1 |
|------|------|--------|-------------|
| STRONG | 11 | 0.1417 | +0.0209 |
| MEDIUM | 12 | 0.1298 | +0.0090 |
| WEAK | 40 | 0.1068 | -0.0140 |

### Event-Count Matched Comparison (A2 vs non-A2)

| Bin | A2 n | A2 CCS1 | non-A2 n | non-A2 CCS1 | A2 DYE_adv | non-A2 DYE_adv |
|-----|------|---------|----------|-------------|------------|----------------|
| 1-3 | 13 | 0.1301 | 15 | 0.0823 | +0.0006 | +0.1241 |
| 16+ | 0 | 0.0000 | 0 | 0.0000 | +0.0000 | +0.0000 |
| 4-7 | 2 | -0.0215 | 14 | 0.0485 | +0.1011 | +0.1178 |
| 8-15 | 3 | 0.1610 | 29 | 0.0464 | -0.0242 | +0.1022 |

## 4. Apparatus Family Partition (T3)

**Verdict: FAMILY_PARTITION_INCONCLUSIVE**

No stable cluster structure. Silhouettes: 0.361, 0.148. Bootstrap: 0.589, 0.410. Best ARI: 0.385.

### Response-Only Clustering (T3a)

| k | Silhouette | ARI_profile | ARI_2family | Composition |
|---|-----------|-------------|-------------|-------------|
| 2 | 0.361 | 0.117 | 0.385 | C0: {'A3_DISTILL_COLLECT': 3, 'A2_SEALED_RECIRCULATION': 9}; C1: {'A3_DISTILL_COLLECT': 34, 'A1_BATH_REFLUX': 21, 'A2_SEALED_RECIRCULATION': 9} |
| 3 | 0.281 | 0.140 | 0.151 | C0: {'A3_DISTILL_COLLECT': 3, 'A2_SEALED_RECIRCULATION': 9}; C1: {'A3_DISTILL_COLLECT': 17, 'A2_SEALED_RECIRCULATION': 1}; C2: {'A3_DISTILL_COLLECT': 17, 'A1_BATH_REFLUX': 21, 'A2_SEALED_RECIRCULATION': 8} |
| 4 | 0.257 | 0.225 | 0.079 | C0: {'A3_DISTILL_COLLECT': 9}; C1: {'A3_DISTILL_COLLECT': 8, 'A1_BATH_REFLUX': 21, 'A2_SEALED_RECIRCULATION': 8}; C2: {'A3_DISTILL_COLLECT': 3, 'A2_SEALED_RECIRCULATION': 9}; C3: {'A3_DISTILL_COLLECT': 17, 'A2_SEALED_RECIRCULATION': 1} |

### Response-Surface Clustering (T3b)

| k | Silhouette | ARI_profile | Composition |
|---|-----------|-------------|-------------|
| 2 | 0.148 | 0.231 | C0: {'A3_DISTILL_COLLECT': 21, 'A1_BATH_REFLUX': 1, 'A2_SEALED_RECIRCULATION': 18}; C1: {'A3_DISTILL_COLLECT': 16, 'A1_BATH_REFLUX': 20} |
| 3 | 0.126 | 0.348 | C0: {'A3_DISTILL_COLLECT': 13}; C1: {'A3_DISTILL_COLLECT': 3, 'A1_BATH_REFLUX': 20}; C2: {'A3_DISTILL_COLLECT': 21, 'A1_BATH_REFLUX': 1, 'A2_SEALED_RECIRCULATION': 18} |
| 4 | 0.138 | 0.308 | C0: {'A3_DISTILL_COLLECT': 13}; C1: {'A3_DISTILL_COLLECT': 3, 'A1_BATH_REFLUX': 20}; C2: {'A3_DISTILL_COLLECT': 10, 'A1_BATH_REFLUX': 1, 'A2_SEALED_RECIRCULATION': 11}; C3: {'A3_DISTILL_COLLECT': 11, 'A2_SEALED_RECIRCULATION': 7} |

### Supervised Sanity Check (T3c)

- F-param only accuracy: 72.4%
- Response-only accuracy: 98.7%
- Combined accuracy: 100.0%
- Profile prediction (F-only): 68.4%
- Profile prediction (response): 72.4%
- Profile prediction (combined): 82.9%

### Cluster Centroids (Response-only, best k)

**Cluster 0** (n=12, profiles: {'A3_DISTILL_COLLECT': 3, 'A2_SEALED_RECIRCULATION': 9})
  - DYE_M1: 0.1381
  - CCS1: 0.1685
  - DYE_adv: -0.0304
  - CRR_M4f: 0.2318
  - NRI_M4f: 0.0747
  - abl_NO_CROSS_COUPLING: -0.0139
  - abl_NO_CLOSE_RECOVERY: 0.1915
  - abl_NO_CONTAINMENT: 0.1128
  - abl_NO_TR_TO_Y: -0.0284
  - abl_NO_Y_SENSITIVITY: -0.0148

**Cluster 1** (n=64, profiles: {'A3_DISTILL_COLLECT': 34, 'A1_BATH_REFLUX': 21, 'A2_SEALED_RECIRCULATION': 9})
  - DYE_M1: 0.1616
  - CCS1: 0.0508
  - DYE_adv: 0.1108
  - CRR_M4f: 0.3797
  - NRI_M4f: 0.0380
  - abl_NO_CROSS_COUPLING: 0.0299
  - abl_NO_CLOSE_RECOVERY: 0.0374
  - abl_NO_CONTAINMENT: 0.0218
  - abl_NO_TR_TO_Y: 0.0238
  - abl_NO_Y_SENSITIVITY: -0.0003

## 5. Within-A2 Structure (T4)

**Verdict: A2_WEAKLY_STRUCTURED**

Section F-ratio=0.05 (sig=False), boundary 44%, anomalous 0%. Some internal variation but not enough for sub-profiles

### Section Stratification

| Section | N_folios | Mean CCS1 | Mean DYE_adv | Mean EPV |
|---------|----------|-----------|--------------|----------|
| C | 5 | 0.1156 | -0.0189 | 0.5133 |
| H | 11 | 0.1234 | +0.0114 | 0.5063 |
| T | 2 | 0.0586 | +0.0925 | 0.9000 |

### Conformity Distribution

| Class | Count |
|-------|-------|
| A2_to_A1_boundary | 4 |
| A2_to_A3_boundary | 4 |
| core_A2 | 5 |
| marginal_A2 | 5 |

### A2 Folios Ranked by CCS1 (highest = most forgiving)

| Folio | Section | CCS1 | DYE_adv | EPV | Events |
|-------|---------|------|---------|-----|--------|
| f95r2 | H | 0.2982 | -0.1809 | 0.1000 | 1 |
| f86v5 | C | 0.2739 | -0.1471 | 0.0500 | 9 |
| f55v | H | 0.2004 | -0.1156 | 0.1500 | 2 |
| f50v | H | 0.1824 | -0.0366 | 0.0526 | 1 |
| f39v | H | 0.1688 | -0.0696 | 0.0500 | 2 |
| f85r2 | C | 0.1538 | -0.0086 | 0.5000 | 3 |
| f40r | H | 0.1476 | -0.0220 | 0.0667 | 1 |
| f86v6 | C | 0.1204 | +0.0003 | 0.6000 | 7 |
| f55r | H | 0.1083 | +0.0424 | 0.7000 | 3 |
| f94r | H | 0.0908 | +0.0702 | 0.7000 | 1 |
| ... | ... | ... | ... | ... | ... |
| f66r | T | 0.0286 | +0.1109 | 1.0000 | 2 |
| f86v3 | C | -0.0001 | +0.0356 | 1.0000 | 6 |
| f33v | H | -0.0429 | +0.1667 | 1.0000 | 5 |

### Failing A2 Folios (EPV < 0.80)

| Folio | Section | EPV | DYE_adv | CCS1 |
|-------|---------|-----|---------|------|
| f86v5 | C | 0.0500 | -0.1471 | 0.2739 |
| f39v | H | 0.0500 | -0.0696 | 0.1688 |
| f50v | H | 0.0526 | -0.0366 | 0.1824 |
| f40r | H | 0.0667 | -0.0220 | 0.1476 |
| f95r2 | H | 0.1000 | -0.1809 | 0.2982 |
| f55v | H | 0.1500 | -0.1156 | 0.2004 |
| f86v4 | C | 0.4167 | +0.0252 | 0.0301 |
| f85r2 | C | 0.5000 | -0.0086 | 0.1538 |
| f86v6 | C | 0.6000 | +0.0003 | 0.1204 |
| f55r | H | 0.7000 | +0.0424 | 0.1083 |
| f94r | H | 0.7000 | +0.0702 | 0.0908 |
| f50r | H | 0.7500 | +0.1067 | 0.0750 |

## 6. New Constraints

**C1639** (Tier 2, scope B)
  A2_SEALED_RECIRCULATION excess forgivingness mechanism: A2_MECHANISM_IDENTIFIED_STRONG. Single ablation NO_CLOSE_RECOVERY accounts for 159.5% of A2 excess CCS1

**C1640** (Tier 2, scope B)
  Currier B apparatus family partition: FAMILY_PARTITION_INCONCLUSIVE. No stable cluster structure. Silhouettes: 0.361, 0.148. Bootstrap: 0.589, 0.410. Best ARI: 0.385.

**C1641** (Tier 2, scope B)
  Within-A2 structure: A2_WEAKLY_STRUCTURED. Section F-ratio=0.05 (sig=False), boundary 44%, anomalous 0%. Some internal variation but not enough for sub-profiles

**C1642** (Tier 2, scope B)
  A2 event-type x grammar-strength forgivingness pattern: GRAMMAR_PATTERN_STRENGTH_DEPENDENT. A2 grammar advantage varies by strength: STRONG adv=+0.0209 (n=11), WEAK adv=-0.0140 (n=40). Range=0.0349, CCS1=0.1208. Only strong-grammar events reliably beat the forgiving null. Weak events lose the null.

## 7. Interpretive Synthesis

### A2 Mechanism Story

Phase 573 identifies a specific mechanism for A2's elevated forgivingness: **NO_CLOSE_RECOVERY** is the primary channel through which null events convert disruption into Y. 
This supports the containment-mediated energy retention hypothesis: A2's parameter signature (high sensitivity_C, low decay_C, high alpha_XC) creates a regime where energy is retained in containment-related variables and recycled through cross-coupling, eventually feeding Y.


No stable family partition emerged from the clustering analysis.

---

*Generated: 2026-03-10T23:22:42.194395+00:00*