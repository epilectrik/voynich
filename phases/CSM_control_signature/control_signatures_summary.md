# Control Signatures Summary - Phase 22B

**Generated:** 2025-12-31T20:59:25.129060
**Total Folios Analyzed:** 83

---

## Distribution Statistics

| Dimension | Mean | Std | Range |
|-----------|------|-----|-------|
| dominant_cycle_order | 2.00 | 0.00 | [2.00, 2.00] |
| secondary_cycle_order | 5.12 | 2.92 | [3.00, 11.00] |
| mean_cycle_length | 4.64 | 0.71 | [2.41, 6.12] |
| cycle_count | 106.73 | 71.25 | [8.00, 254.00] |
| cycle_regularity | 3.45 | 0.63 | [0.69, 4.41] |
| link_density | 0.38 | 0.07 | [0.20, 0.58] |
| max_consecutive_link | 8.47 | 5.93 | [3.00, 37.00] |
| intervention_frequency | 5.94 | 2.06 | [2.14, 14.62] |
| intervention_diversity | 5.94 | 0.24 | [5.00, 6.00] |
| kernel_distance_mean | 1.38 | 0.07 | [1.20, 1.58] |
| kernel_contact_ratio | 0.62 | 0.07 | [0.42, 0.80] |
| hazard_adjacency_count | 540.78 | 353.77 | [93.00, 1552.00] |
| hazard_density | 0.58 | 0.07 | [0.41, 0.77] |
| near_miss_count | 23.70 | 17.11 | [2.00, 79.00] |
| recovery_ops_count | 16.07 | 13.16 | [0.00, 67.00] |
| reset_present | 0.04 | 0.19 | [0.00, 1.00] |
| total_length | 906.60 | 552.15 | [163.00, 2222.00] |
| compression_ratio | 0.01 | 0.01 | [0.00, 0.04] |
| phase_ordering_rigidity | 0.17 | 0.04 | [0.07, 0.30] |

---

## Family Coherence Analysis

**F-ratio:** 2.54
**Interpretation:** HIGH

**Best Discriminating Dimensions:**

- total_length: variance = 88667.483
- hazard_adjacency_count: variance = 34063.912
- cycle_count: variance = 1555.716
- near_miss_count: variance = 52.448
- recovery_ops_count: variance = 43.404

---

## Invariants

**Total Invariants Found:** 3

### Grammar Invariants


### Manuscript Invariants

- dominant_cycle_order: mean=2.0, cv=0.0
- intervention_diversity: mean=5.94, cv=0.04
- kernel_distance_mean: mean=1.383, cv=0.05

---

## Outliers

**Outlier Count:** 15

### f33r (Family 4)
- compression_ratio: z=2.06, value=0.032
- phase_ordering_rigidity: z=-2.28, value=0.066

### f48r (Family 3)
- link_density: z=2.78, value=0.576
- kernel_distance_mean: z=2.83, value=1.58
- kernel_contact_ratio: z=-2.78, value=0.424
- hazard_density: z=-2.65, value=0.406

### f57r (Family 6)
- intervention_diversity: z=-3.95, value=5.0
- reset_present: z=5.16, value=1.0

### f76r (Family 2)
- cycle_count: z=2.05, value=253.0
- hazard_adjacency_count: z=2.86, value=1552.0
- near_miss_count: z=2.18, value=61.0
- total_length: z=2.38, value=2222.0

### f83v (Family 2)
- link_density: z=-2.59, value=0.204
- kernel_distance_mean: z=-2.64, value=1.2
- kernel_contact_ratio: z=2.59, value=0.796
- hazard_density: z=2.86, value=0.771

### f85v2 (Family 4)
- mean_cycle_length: z=-3.16, value=2.41
- cycle_regularity: z=-4.39, value=0.687
- link_density: z=2.47, value=0.554
- kernel_distance_mean: z=2.4, value=1.55
- kernel_contact_ratio: z=-2.47, value=0.446
- hazard_density: z=-2.57, value=0.411
- phase_ordering_rigidity: z=3.03, value=0.297

### f86v4 (Family 8)
- mean_cycle_length: z=-3.13, value=2.43
- cycle_regularity: z=-2.86, value=1.647

### f94v (Family 4)
- cycle_regularity: z=-2.14, value=2.1
- intervention_frequency: z=2.79, value=11.7
- compression_ratio: z=2.49, value=0.036

### f95r2 (Family 4)
- intervention_diversity: z=-3.95, value=5.0
- phase_ordering_rigidity: z=-2.03, value=0.077

### f95v2 (Family 4)
- mean_cycle_length: z=2.09, value=6.12
- intervention_frequency: z=4.2, value=14.62
- compression_ratio: z=2.59, value=0.037

---

## Process Class Exclusion Analysis

### [X] Mechanical timing systems
**Status:** SOFT_EXCLUDED
**Justification:** Some timing characteristics but not conclusive

### [X] Astronomical/calendrical
**Status:** SOFT_EXCLUDED
**Justification:** No clear astronomical number patterns

### [X] Biological cultivation
**Status:** SOFT_EXCLUDED
**Justification:** Cultivation requires growth/decay asymmetry

### [X] Open-loop control
**Status:** SOFT_EXCLUDED
**Justification:** System shows closed-loop characteristics

### [?] Discrete batch processing
**Status:** PLAUSIBLE
**Justification:** Cannot rule out batch-like segments

### [?] Continuous closed-loop control
**Status:** PLAUSIBLE
**Justification:** Signature compatible with closed-loop thermal/chemical control

---

## Clustering Results

**Optimal K:** 2
**Silhouette Score:** 0.255

**Silhouette Scores by K:**

- K=2: 0.255
- K=3: 0.246
- K=4: 0.23
- K=5: 0.233
- K=6: 0.192
- K=7: 0.185
- K=8: 0.156
- K=9: 0.177
- K=10: 0.19

---

*All metrics computed using control-theoretic and graph-theoretic language only.*
