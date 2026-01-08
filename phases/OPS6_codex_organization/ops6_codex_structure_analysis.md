# Phase OPS-6: Codex Structure Analysis Report

**Date:** 2026-01-04

---

## Executive Summary

| Result | Count |
|--------|-------|
| SUPPORTED | 2 |
| REJECTED | 1 |
| INCONCLUSIVE | 2 |

### Hypothesis Summary

| Hypothesis | Status | Effect Size | Key Finding |
|------------|--------|-------------|-------------|
| CEI Smoothing | SUPPORTED | 1.892 | Observed mean CEI jump (0.1264) is at 2.8th percentile of nu... |
| High-CEI Isolation | INCONCLUSIVE | -0.114 | Max cluster size (4) at 58.6th percentile; neighbor CEI (0.5... |
| Restart Placement | SUPPORTED | 2.241 | Restart folios have mean CEI 0.3980 (1.9th percentile of ran... |
| Quire Boundary Interaction | INCONCLUSIVE | 1.75 | Boundary CEI at 96.7th percentile; boundary jumps at 8.1th p... |
| Navigation Topology | REJECTED | -7.334 | Max retreat 18 steps (0.0th percentile); 9 trap positions (0... |

---

## CEI Smoothing

### Observed Metrics

- **Mean Cei Jump:** 0.1264
- **Max Cei Jump:** 0.3677
- **Mean Neighborhood Variance:** 0.01361

### Null Distribution

- **Mean Jump Mean:** 0.1423
- **Mean Jump Std:** 0.0084
- **Variance Mean:** 0.016282
- **Variance Std:** 0.001289

### Statistical Results

- **Mean Jump Percentile:** 2.8%
- **Max Jump Percentile:** 1.2%
- **Variance Percentile:** 3.0%

### Effect Sizes

- **Jump Reduction Cohen D:** 1.892
- **Variance Reduction Cohen D:** 2.073

**Status:** SUPPORTED

**Interpretation:** Observed mean CEI jump (0.1264) is at 2.8th percentile of null distribution

---

## High-CEI Isolation

### Observed Metrics

- **N High Cei Folios:** 29
- **N Clusters:** 18
- **Cluster Sizes:** [1, 1, 3, 3, 1, 2, 1, 1, 1, 1, 1, 1, 4, 3, 1, 1, 2, 1]
- **Max Cluster Size:** 4
- **Mean Neighbor Cei:** 0.5711
- **Mean Gap Between High Cei:** 2.93

### Null Distribution

- **Max Cluster Mean:** 3.88
- **Max Cluster Std:** 1.06
- **Neighbor Cei Mean:** 0.5523
- **Neighbor Cei Std:** 0.0169

### Statistical Results

- **Cluster Size Percentile:** 58.6%
- **Neighbor Cei Percentile:** 87.2%

### Effect Sizes

- **Cluster Isolation Cohen D:** -0.114
- **Neighbor Buffering Cohen D:** -1.114

**Status:** INCONCLUSIVE

**Interpretation:** Max cluster size (4) at 58.6th percentile; neighbor CEI (0.571) at 87.2th percentile

---

## Restart Placement

### Observed Metrics

- **Restart Positions:** {'f50v': 21, 'f57r': 24, 'f82v': 42}
- **Restart Ceis:** {'f50v': 0.3792, 'f57r': 0.4221, 'f82v': 0.3927}
- **Mean Restart Cei:** 0.398
- **Overall Mean Cei:** 0.5532
- **Mean Distance To High Cei Before:** 4.33
- **Cei Drops After Restart:** [0.1021, 0.1105, 0.0743]

### Null Distribution

- **Mean Random Cei:** 0.5562
- **Std Random Cei:** 0.0706
- **Mean Random Distance:** 3.12

### Statistical Results

- **Restart Cei Percentile:** 1.9%

### Effect Sizes

- **Cei Placement Cohen D:** 2.241

**Status:** SUPPORTED

**Interpretation:** Restart folios have mean CEI 0.3980 (1.9th percentile of random)

---

## Quire Boundary Interaction

### Observed Metrics

- **Boundary Ceis:** {'f26r': 0.6387, 'f33r': 0.7772}
- **Mean Boundary Cei:** 0.708
- **Mean Jump At Boundary:** 0.2234
- **Mean Non Boundary Jump:** 0.1252
- **Mean Variance After Boundary:** 0.010114

### Null Distribution

- **Mean Random Boundary Cei:** 0.5508
- **Std Random Boundary Cei:** 0.0898
- **Mean Random Boundary Jump:** 0.1243

### Statistical Results

- **Boundary Cei Percentile:** 96.7%
- **Boundary Jump Percentile:** 8.1%

### Effect Sizes

- **Boundary Cei Cohen D:** 1.75

**Status:** INCONCLUSIVE

**Interpretation:** Boundary CEI at 96.7th percentile; boundary jumps at 8.1th percentile

---

## Navigation Topology

### Observed Metrics

- **Low Cei Threshold:** 0.5032
- **N Low Cei Positions:** 27
- **N High Cei Positions:** 29
- **Max Retreat Distance:** 18
- **Mean Retreat Distance:** 5.14
- **N Trap Positions:** 9

### Null Distribution

- **Mean Max Retreat:** 5.03
- **Std Max Retreat:** 1.77
- **Mean Trap Count:** 0.6
- **Std Trap Count:** 1.2

### Statistical Results

- **Max Retreat Percentile:** 0.0%
- **Mean Retreat Percentile:** 0.0%
- **Trap Count Percentile:** 0.0%

### Effect Sizes

- **Retreat Reduction Cohen D:** -7.334
- **Trap Reduction Cohen D:** -7.002

**Status:** REJECTED

**Interpretation:** Max retreat 18 steps (0.0th percentile); 9 trap positions (0.0th percentile)

---

## Supplementary: CEI Neighbor Buffering

- **High-CEI folios analyzed:** 29
- **Damping cases:** 24 (82.8%)
- **Amplification cases:** 5

---

## Verdict

> **PARTIAL STRUCTURAL ORGANIZATION DETECTED**
> Multiple hypotheses supported suggest intentional CEI management in codex organization.

---

> **"OPS-6 is complete. Codex organization has been evaluated against control-engagement and human-factors hypotheses using purely structural evidence. No new control logic or semantic interpretation has been introduced."**

*Generated: 2026-01-04T22:30:44.358792*