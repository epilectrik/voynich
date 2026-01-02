# Ordering Null Model Summary

> Comparison of observed ordering against permutation null models

---

## Methodology

All tests use 10,000 permutations to construct null distributions.
P-values are computed as the fraction of null samples more extreme than observed.

## Summary of Tests

| Test | Observed | Null Mean | Null Std | p-value | Signal? |
|------|----------|-----------|----------|---------|--------|
| Risk-Order Correlation | 0.3918 | 0.0003 | 0.1101 | 0.0004 | YES |
| Mean Risk Jump | 0.3074 | 0.4440 | 0.0299 | 0.0000 | YES |
| Aggressive Buffering | 0.880 | 0.494 | 0.082 | 0.0000 | YES |

## Verdicts by Test

- **Order vs Risk Gradient**: SIGNAL: Non-random risk ordering with monotonic gradient
- **Boundary Clustering**: NULL: No boundary clustering detected
- **Currier Role Asymmetry**: INSUFFICIENT DATA: All programs are Currier B
- **Local Neighborhood Safety**: SIGNAL: Risk-aware local ordering with buffering
- **Restart Program Placement**: NULL: Restart programs randomly placed
