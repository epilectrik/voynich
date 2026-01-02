# Option A: Geometry Comparison Report

## Geometry Class Performance

| Geometry | Recirculation | Conv Rate | Failure | STATE-C | LINK Eff | Status |
|----------|---------------|-----------|---------|---------|----------|--------|
| G1 | 0.00 | 0.065 | 0.935 | 0.444 | 0.200 | INCOMPATIBLE |
| G2 | 0.00 | 0.993 | 0.007 | 0.800 | 0.200 | COMPATIBLE |
| G3 | 0.50 | 0.999 | 0.001 | 0.864 | 0.200 | COMPATIBLE |
| G4 | 1.00 | 1.000 | 0.000 | 0.998 | 0.800 | COMPATIBLE |
| G5 | 1.00 | 1.000 | 0.000 | 0.999 | 1.350 | COMPATIBLE |

*Values: Conv Rate = convergence rate, STATE-C = mean time in target state, LINK Eff = LINK operator effectiveness*

## Cluster × Geometry Matrix (Convergence Rate)

| Cluster | G1 | G2 | G3 | G4 | G5 |
|---------|----|----|----|----|----| 
| 1 | 0.02 | 0.99 | 1.00 | 1.00 | 1.00 |
| 2 | 0.19 | 1.00 | 1.00 | 1.00 | 1.00 |
| 3 | 0.34 | 1.00 | 1.00 | 1.00 | 1.00 |
| 4 | 0.08 | 1.00 | 1.00 | 1.00 | 1.00 |
| 5 | 0.02 | 1.00 | 1.00 | 1.00 | 1.00 |

## Statistical Summary

- Kruskal-Wallis H: 359.310
- p-value: 1.71e-76
- Effect size (eta^2): 0.867

## Closed-Loop vs Open-Flow Comparison

- t-statistic: 12.864
- p-value: 5.68e-31
- Cohen's d: 1.416

## LINK Effectiveness by Geometry Type

- Mean closed-loop (G4+G5): 1.075
- Mean open-flow (G1+G2): 0.200
- Cohen's d: 4.500

## Verdict

**PASS**

Grammar selectively compatible with closed-loop geometries (G4, G5). Open flow (G1) fails (6.5% convergence). LINK maps to physical delay only in closed loops (d=4.50). Effect size eta^2=0.867
