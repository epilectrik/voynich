# Lane 3: Stability Matrix

## Material Class vs Cluster Stability

| Material | Cluster 1 | Cluster 2 | Cluster 3 | Cluster 4 | Cluster 5 | Overall |
|----|----|----|----|----|----|----|
| CLASS_A | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| CLASS_B | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| CLASS_C | 0.34 | 0.15 | 0.07 | 0.11 | 0.31 | 0.20 |
| CLASS_D | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| CLASS_E | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |

*Values show failure rate (lower = more compatible)*

## Convergence Rate by Material Class

| Material | Mean Convergence | Mean Failure | Status |
|----------|------------------|--------------|--------|
| CLASS_A | 1.000 | 0.000 | COMPATIBLE |
| CLASS_B | 1.000 | 0.000 | COMPATIBLE |
| CLASS_C | 0.802 | 0.198 | INCOMPATIBLE |
| CLASS_D | 1.000 | 0.000 | COMPATIBLE |
| CLASS_E | 1.000 | 0.000 | COMPATIBLE |

## Statistical Summary

- Kruskal-Wallis H: 106.277
- p-value: 0.000000
- Effect size (eta^2): 0.930
- Compatible classes: 4
- Incompatible classes: 1

## Verdict: **PASS**

Material classes differentially compatible (p=0.0000, eta^2=0.930)
