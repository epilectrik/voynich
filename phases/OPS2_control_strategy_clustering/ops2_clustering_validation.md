# Phase OPS-2: Clustering Validation Report

**Date:** 2026-01-04

---

## 1. Method Comparison

### Hierarchical (Ward) Results

| k | Silhouette | Calinski-Harabasz | Davies-Bouldin |
|---|------------|-------------------|----------------|
| 3 | 0.2140 | 28.0 | 1.4347 |
| 4 | 0.1710 | 23.9 | 1.4868 |
| 5 | 0.1683 | 22.5 | 1.4055 |
| 6 | 0.1845 | 21.9 | 1.3292 |
| 7 | 0.1757 | 20.9 | 1.4853 |
| 8 | 0.1823 | 20.2 | 1.2865 |
| 9 | 0.1621 | 19.4 | 1.3388 |
| 10 | 0.1680 | 19.1 | 1.2541 |

### K-Means Results

| k | Silhouette | Calinski-Harabasz | Davies-Bouldin |
|---|------------|-------------------|----------------|
| 3 | 0.2294 | 32.4 | 1.3602 |
| 4 | 0.2307 | 29.9 | 1.3471 |
| 5 | 0.2051 | 26.5 | 1.3587 |
| 6 | 0.1877 | 24.0 | 1.4223 |
| 7 | 0.1852 | 22.2 | 1.3914 |
| 8 | 0.2051 | 21.9 | 1.1555 |
| 9 | 0.1944 | 20.6 | 1.2158 |
| 10 | 0.1792 | 20.4 | 1.1847 |

### DBSCAN Results

| eps | Clusters | Noise | Silhouette |
|-----|----------|-------|------------|
| 0.5 | 0 | 83 | N/A |
| 1.0 | 0 | 83 | N/A |
| 1.5 | 3 | 74 | 0.5560 |
| 2.0 | 5 | 54 | 0.3618 |
| 2.5 | 1 | 14 | N/A |
| 3.0 | 1 | 7 | N/A |

---

## 2. Stability Results

| Method | k | Bootstrap ARI | Noise ARI |
|--------|---|---------------|-----------|
| hierarchical | 3 | 0.436 ± 0.159 | 0.565 ± 0.232 |
| kmeans | 4 | 0.646 ± 0.173 | 0.881 ± 0.078 |

---

## 3. Consensus Analysis

**Hierarchical best k:** 3
**K-Means best k:** 4
**Agreement within ±1:** YES

---

## 4. Selected Solution

**Method:** KMEANS
**k:** 4

### Justification

Methods agree within ±1 cluster count. Selection based on stability metrics.

---

## 5. Feature Redundancy

**Highly correlated pairs (|rho| > 0.9):** 20

| Feature 1 | Feature 2 | rho |
|-----------|-----------|---|
| total_tokens | link_count | 0.953 |
| total_tokens | cycle_count | 0.918 |
| link_density | kernel_contact_ratio | -0.997 |
| link_density | hazard_density | -0.951 |
| link_density | aggressiveness | -0.988 |
| link_density | conservatism | 0.988 |
| link_density | control_margin | 0.951 |
| kernel_contact_ratio | hazard_density | 0.959 |
| kernel_contact_ratio | aggressiveness | 0.990 |
| kernel_contact_ratio | conservatism | -0.990 |
| kernel_contact_ratio | control_margin | -0.959 |
| hazard_density | aggressiveness | 0.988 |
| hazard_density | conservatism | -0.988 |
| hazard_density | control_margin | -1.000 |
| aggressiveness | conservatism | -1.000 |
| ... | (5 more) | ... |

*Note: Both features retained per instruction (no pruning).*

---

## 6. Eliminated Alternatives

- **HIERARCHICAL k=3:** Not selected due to lower stability metrics
- **DBSCAN:** Variable cluster counts across epsilon values; noise points complicate interpretation
- **HDBSCAN:** Not available (library not installed)

---

*Generated: 2026-01-04T21:03:10.162087*